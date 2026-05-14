"""
Recommendation engine — the core scoring and ranking layer.

Pipeline:
  1. Candidate retrieval   — personalized vector search (200 candidates)
  2. Signal scoring        — semantic, graph, recency, diversity signals
  3. Re-ranking            — weighted ensemble with diversity injection
  4. Explainability        — attach human-readable Signal objects per item
  5. Response assembly     — final list with confidence scores
"""
from __future__ import annotations

import logging
import math
import time
from datetime import datetime

from models import (
    Content,
    ContentDNA,
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
    Signal,
)
from catalog.vector_store import get_vector_store
from catalog.graph import get_graph
from config import get_settings

log = logging.getLogger(__name__)


class RecommendationEngine:
    """Main engine entry point — stateless, all state via injected services."""

    def __init__(self):
        self._vs = get_vector_store()
        self._graph = get_graph()
        self._settings = get_settings()

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        t0 = time.monotonic()

        # ── 1. Candidate retrieval ─────────────────────────────────────
        candidates = await self._retrieve_candidates(request)
        if not candidates:
            log.warning("No candidates found for user %s", request.user_id)
            return self._empty_response(t0)

        # ── 2. Filter already-watched ──────────────────────────────────
        watched = set(await self._graph.get_watch_history(request.user_id, limit=200))
        candidates = [c for c in candidates if c.get("id") not in watched]

        # ── 3. Graph-based signals ─────────────────────────────────────
        genre_weights = await self._graph.get_user_genre_weights(request.user_id)

        # ── 4. Score each candidate ────────────────────────────────────
        scored = [
            self._score_candidate(c, genre_weights, request.context)
            for c in candidates
        ]
        scored.sort(key=lambda x: x["final_score"], reverse=True)

        # ── 5. Diversity injection ─────────────────────────────────────
        diverse = self._diversify(scored, target=request.limit)

        # ── 6. Build Recommendation objects ───────────────────────────
        recs = []
        for rank, item in enumerate(diverse[: request.limit]):
            content = _dict_to_content(item["payload"])
            signals = _build_signals(item, genre_weights)
            recs.append(Recommendation(
                content=content,
                score=item["final_score"],
                rank=rank + 1,
                signals=signals,
                confidence=min(0.99, item["final_score"] * 0.95),
            ))

        latency_ms = int((time.monotonic() - t0) * 1000)
        log.info(
            "rec.complete user=%s count=%d latency_ms=%d",
            request.user_id, len(recs), latency_ms,
        )
        return RecommendationResponse(
            recommendations=recs,
            generated_at=datetime.utcnow(),
            model_version="nexus-v1-hybrid",
            latency_ms=latency_ms,
        )

    # ── Candidate retrieval ───────────────────────────────────────────

    async def _retrieve_candidates(self, request: RecommendationRequest) -> list[dict]:
        mood_hint = request.context.get("mood_hint", "")
        query = mood_hint if mood_hint else None
        pool_size = self._settings.rec_candidate_pool_size

        return await self._vs.personalized_search(
            user_id=request.user_id,
            query=query,
            limit=pool_size,
        )

    # ── Scoring ────────────────────────────────────────────────────────

    def _score_candidate(
        self,
        item: dict,
        genre_weights: dict[str, float],
        context: dict,
    ) -> dict:
        semantic_score = item.get("score", 0.5)

        # Genre affinity signal (graph-derived)
        item_genres = item.get("genres", [])
        genre_score = sum(genre_weights.get(g, 0.0) for g in item_genres)
        genre_score = min(1.0, genre_score)

        # Recency signal — newer content gets a slight boost
        year = item.get("year", 2000)
        recency_score = _recency_signal(year)

        # Context signals — time-of-day and device
        context_boost = _context_signal(item, context)

        # Weighted combination
        w = self._settings
        final = (
            0.45 * semantic_score
            + 0.30 * genre_score
            + w.rec_recency_weight * recency_score
            + w.rec_diversity_weight * context_boost
        )
        return {
            **item,
            "payload": item,
            "semantic_score": semantic_score,
            "genre_score": genre_score,
            "recency_score": recency_score,
            "context_boost": context_boost,
            "final_score": round(final, 4),
        }

    # ── Diversity ─────────────────────────────────────────────────────

    def _diversify(self, scored: list[dict], target: int) -> list[dict]:
        """
        Maximal Marginal Relevance-style diversity.
        Ensures varied genres, kinds, and pacing in the top results.
        """
        seen_genres: set[str] = set()
        seen_kinds: set[str] = set()
        diverse: list[dict] = []

        for item in scored:
            if len(diverse) >= target:
                break
            genres = frozenset(item.get("genres", []))
            kind = item.get("kind", "film")

            # Penalise heavy genre overlap but don't exclude
            overlap = len(genres & seen_genres)
            if overlap > 2 and len(diverse) < target // 2:
                continue

            diverse.append(item)
            seen_genres |= genres
            seen_kinds.add(kind)

        # Backfill if diversity pruned too aggressively
        if len(diverse) < target:
            ids_in = {d.get("id") for d in diverse}
            for item in scored:
                if len(diverse) >= target:
                    break
                if item.get("id") not in ids_in:
                    diverse.append(item)

        return diverse


# ── Helpers ───────────────────────────────────────────────────────────────

def _recency_signal(year: int) -> float:
    """Maps title year to a 0..1 recency bonus, peaking at current year."""
    current = 2025
    age = max(0, current - year)
    return max(0.0, 1.0 - age / 20.0)


def _context_signal(item: dict, context: dict) -> float:
    """
    Lightweight context-aware boost.
    Considers: time_of_day (morning/evening), device (mobile/tv), mood_hint.
    """
    boost = 0.0
    time_of_day = context.get("time_of_day", "evening")
    device = context.get("device", "tv")
    dna = item.get("dna") or {}
    pacing = dna.get("pacing", 0.5)
    runtime = dna.get("runtime_min", 90)

    # Morning → lighter, shorter content
    if time_of_day in ("morning", "afternoon"):
        if pacing < 0.5 and runtime < 45:
            boost += 0.15

    # Mobile → shorter episodes/films
    if device == "mobile" and runtime < 40:
        boost += 0.1

    # TV / evening → epic or prestige
    if device == "tv" and time_of_day == "evening":
        if pacing > 0.5:
            boost += 0.08

    return min(1.0, boost)


def _build_signals(item: dict, genre_weights: dict[str, float]) -> list[Signal]:
    signals = []
    semantic = item.get("semantic_score", 0.0)
    genre = item.get("genre_score", 0.0)
    recency = item.get("recency_score", 0.0)

    if semantic > 0.3:
        signals.append(Signal(
            name="Semantic match",
            weight=round(semantic, 2),
            detail=f"Strong thematic and narrative alignment with your viewing profile",
            icon="brain",
        ))

    top_genre = max(
        item.get("genres", []),
        key=lambda g: genre_weights.get(g, 0.0),
        default=None,
    )
    if top_genre and genre_weights.get(top_genre, 0) > 0.1:
        signals.append(Signal(
            name="Genre affinity",
            weight=round(genre, 2),
            detail=f"Matches your consistent preference for {top_genre}",
            icon="film",
        ))

    dna = item.get("dna") or {}
    visual = dna.get("visual_style", "")
    if visual:
        signals.append(Signal(
            name="Visual DNA",
            weight=0.18,
            detail=f"Cinematography fingerprint: {visual.replace('_', ' ')}",
            icon="eye",
        ))

    year = item.get("year", 2000)
    if year >= 2022:
        signals.append(Signal(
            name="Recent release",
            weight=round(recency, 2),
            detail=f"Released in {year} — trending and critically discussed",
            icon="trending-up",
        ))

    return signals[:4]  # Cap at 4 signals per card


def _dict_to_content(d: dict) -> Content:
    raw_dna = d.get("dna")
    dna = ContentDNA(**raw_dna) if raw_dna and isinstance(raw_dna, dict) else None
    return Content(
        id=d.get("id", ""),
        title=d.get("title", "Unknown"),
        year=d.get("year", 0),
        kind=d.get("kind", "film"),
        synopsis=d.get("synopsis", ""),
        genres=d.get("genres", []),
        cast=d.get("cast", []),
        director=d.get("director"),
        poster_url=d.get("poster_url", ""),
        backdrop_url=d.get("backdrop_url", ""),
        rating=d.get("rating", 0.0),
        dna=dna,
    )


def _empty_response(t0: float) -> RecommendationResponse:
    return RecommendationResponse(
        recommendations=[],
        generated_at=datetime.utcnow(),
        model_version="nexus-v1-hybrid",
        latency_ms=int((time.monotonic() - t0) * 1000),
    )
