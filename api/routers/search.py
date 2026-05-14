"""
Search router — semantic + keyword search.
GET /v1/search/?q=...
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from middleware.auth import require_auth, ApiKey
from catalog.vector_store import get_vector_store

router = APIRouter()


@router.get("/")
async def search(
    _auth: ApiKey = Depends(require_auth),
    q: str = Query(..., min_length=1, description="Natural language or keyword query"),
    limit: int = Query(20, ge=1, le=100),
    genre: str | None = None,
    kind: str | None = None,
):
    """
    Semantic search over the content catalog.
    Supports natural language: "slow burn psychological thriller like Parasite"
    """
    vs = get_vector_store()
    filters = {}
    if genre:
        filters["genres"] = [genre]
    if kind:
        filters["kind"] = kind

    results = await vs.semantic_search(
        query=q,
        limit=limit,
        filters=filters if filters else None,
    )
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
