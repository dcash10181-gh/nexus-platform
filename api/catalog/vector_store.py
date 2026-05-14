"""
Vector store — Qdrant wrapper for semantic content + user preference embeddings.

Handles:
  - Collection lifecycle (create / ensure)
  - Upsert of content embeddings
  - k-NN search with payload filters
  - User preference vector management
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm
from sentence_transformers import SentenceTransformer

from config import get_settings

log = logging.getLogger(__name__)

_CONTENT_COLLECTION = "nexus_content"  # default; overridden per-tenant
_USER_COLLECTION = "nexus_users"


class VectorStore:
    def __init__(self, url: str, embedding_model: str, dim: int, api_key: str = ""):
        self._client = AsyncQdrantClient(url=url, api_key=api_key or None)
        self._encoder = SentenceTransformer(embedding_model)
        self._dim = dim
        # Collection names — overridden per-tenant via get_tenant_vector_store()
        self._content_collection = _CONTENT_COLLECTION
        self._users_collection = _USER_COLLECTION

    # ── Collection management ─────────────────────────────────────────────

    async def ensure_collection(self) -> None:
        existing = {c.name for c in (await self._client.get_collections()).collections}

        for name in (self._content_collection, self._users_collection):
            if name not in existing:
                await self._client.create_collection(
                    collection_name=name,
                    vectors_config=qm.VectorParams(
                        size=self._dim,
                        distance=qm.Distance.COSINE,
                    ),
                )
                log.info("Created Qdrant collection: %s", name)
            else:
                log.info("Qdrant collection exists: %s", name)

    # ── Encoding ─────────────────────────────────────────────────────────

    def encode(self, text: str) -> list[float]:
        vec = self._encoder.encode(text, normalize_embeddings=True)
        return vec.tolist()

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        vecs = self._encoder.encode(texts, normalize_embeddings=True, batch_size=64)
        return vecs.tolist()

    # ── Content upsert ───────────────────────────────────────────────────

    async def upsert_content(self, items: list[dict]) -> None:
        """
        items: each dict has at minimum {id, title, synopsis, genres, ...}
        We embed synopsis + title + genres concatenation for rich semantic recall.
        """
        texts = [
            f"{i['title']}. {i.get('synopsis', '')} Genres: {', '.join(i.get('genres', []))}"
            for i in items
        ]
        vectors = self.encode_batch(texts)

        points = [
            qm.PointStruct(
                id=_stable_id(item["id"]),
                vector=vec,
                payload={k: v for k, v in item.items() if k != "dna"},
            )
            for item, vec in zip(items, vectors)
        ]

        await self._client.upsert(collection_name=self._content_collection, points=points)
        log.info("Upserted %d content vectors", len(points))

    # ── Semantic search ──────────────────────────────────────────────────

    async def semantic_search(
        self,
        query: str,
        limit: int = 50,
        filters: dict | None = None,
        score_threshold: float = 0.25,
    ) -> list[dict]:
        vec = self.encode(query)
        qdrant_filter = _build_filter(filters) if filters else None

        results = await self._client.search(
            collection_name=self._content_collection,
            query_vector=vec,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        return [
            {"score": r.score, **r.payload}
            for r in results
        ]

    async def get_similar(self, content_id: str, limit: int = 20) -> list[dict]:
        """Content-to-content similarity using existing vector."""
        numeric_id = _stable_id(content_id)
        results = await self._client.recommend(
            collection_name=self._content_collection,
            positive=[numeric_id],
            limit=limit,
            with_payload=True,
        )
        return [{"score": r.score, **r.payload} for r in results]

    # ── User preference vectors ──────────────────────────────────────────

    async def upsert_user_vector(self, user_id: str, preference_text: str) -> None:
        vec = self.encode(preference_text)
        await self._client.upsert(
            collection_name=self._users_collection,
            points=[qm.PointStruct(
                id=_stable_id(user_id),
                vector=vec,
                payload={"user_id": user_id},
            )],
        )

    async def get_user_vector(self, user_id: str) -> list[float] | None:
        results = await self._client.retrieve(
            collection_name=self._users_collection,
            ids=[_stable_id(user_id)],
            with_vectors=True,
        )
        if results:
            return results[0].vector
        return None

    async def personalized_search(
        self,
        user_id: str,
        query: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Blend user preference vector with optional query vector."""
        user_vec = await self.get_user_vector(user_id)

        if query:
            query_vec = np.array(self.encode(query))
        else:
            query_vec = None

        if user_vec is not None:
            u = np.array(user_vec)
            if query_vec is not None:
                # 60% user preference, 40% query intent
                blended = 0.6 * u + 0.4 * query_vec
                blended = blended / np.linalg.norm(blended)
                search_vec = blended.tolist()
            else:
                search_vec = user_vec
        elif query_vec is not None:
            search_vec = query_vec.tolist()
        else:
            # Cold start — return popular items
            return await self.semantic_search("popular acclaimed critically acclaimed", limit=limit)

        results = await self._client.search(
            collection_name=self._content_collection,
            query_vector=search_vec,
            limit=limit,
            with_payload=True,
        )
        return [{"score": r.score, **r.payload} for r in results]

    # ── Catalog helpers ──────────────────────────────────────────────────

    async def get_by_ids(self, ids: list[str]) -> list[dict]:
        numeric_ids = [_stable_id(i) for i in ids]
        results = await self._client.retrieve(
            collection_name=self._content_collection,
            ids=numeric_ids,
            with_payload=True,
        )
        return [r.payload for r in results]

    async def count(self) -> int:
        info = await self._client.get_collection(_CONTENT_COLLECTION)
        return info.points_count or 0


# ── Helpers ───────────────────────────────────────────────────────────────

def _stable_id(s: str) -> int:
    """Map arbitrary string IDs to stable positive integers for Qdrant."""
    import hashlib
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def _build_filter(filters: dict) -> qm.Filter:
    must = []
    for key, value in filters.items():
        if isinstance(value, list):
            must.append(qm.FieldCondition(
                key=key,
                match=qm.MatchAny(any=value),
            ))
        else:
            must.append(qm.FieldCondition(
                key=key,
                match=qm.MatchValue(value=value),
            ))
    return qm.Filter(must=must)


@lru_cache
def get_vector_store() -> VectorStore:
    s = get_settings()
    return VectorStore(
        url=s.qdrant_url,
        embedding_model=s.embedding_model,
        dim=s.embedding_dim,
        api_key=s.qdrant_api_key,
    )


# ── Tenant-scoped factory ─────────────────────────────────────────────────

_tenant_stores: dict[str, VectorStore] = {}


def get_tenant_vector_store(tenant_id: str) -> VectorStore:
    """
    Return a VectorStore scoped to a specific tenant.
    Each tenant gets isolated Qdrant collections: {tenant_id}_content, {tenant_id}_users.
    """
    if tenant_id not in _tenant_stores:
        s = get_settings()
        store = VectorStore(
            url=s.qdrant_url,
            embedding_model=s.embedding_model,
            dim=s.embedding_dim,
        )
        # Override collection names with tenant namespace
        store._content_collection = f"{tenant_id}_content"
        store._users_collection = f"{tenant_id}_users"
        _tenant_stores[tenant_id] = store
    return _tenant_stores[tenant_id]
