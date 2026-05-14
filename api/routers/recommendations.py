"""
Recommendations router.
POST /v1/recommendations/   → personalised recommendation feed
POST /v1/recommendations/because-you-watched/{content_id}
"""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from models import RecommendationRequest, RecommendationResponse
from middleware.auth import require_auth, ApiKey
from recommendations.engine import RecommendationEngine
from catalog.graph import get_graph

log = logging.getLogger(__name__)
router = APIRouter()

_engine: RecommendationEngine | None = None

def _get_engine() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest, _auth: ApiKey = Depends(require_auth)):
    """Main recommendation feed — personalised, explainable, diversity-injected."""
    try:
        return await _get_engine().recommend(request)
    except Exception as e:
        log.error("Recommendation error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/because-you-watched/{content_id}")
async def because_you_watched(content_id: str, limit: int = 10, _auth: ApiKey = Depends(require_auth)):
    """Graph-path recommendations seeded from a specific title."""
    graph = get_graph()
    similar = await graph.get_because_you_watched(content_id, limit=limit)
    return {"seed": content_id, "recommendations": similar}
