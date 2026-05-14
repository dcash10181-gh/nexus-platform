"""
Federated / on-device inference router.

POST /v1/federated/score   — Score candidates using ONNX preference model
GET  /v1/federated/status  — Model availability and version info
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from inference.onnx_engine import federated_score, get_onnx_scorer

router = APIRouter()


class FederatedScoreRequest(BaseModel):
    candidates: list[dict]
    user_profile: dict = {}


@router.post("/score")
async def score_federated(req: FederatedScoreRequest):
    """
    Score candidates using the local ONNX preference model.
    User profile stays local — only candidate scores are returned.

    user_profile shape:
      { genre_weights: {Drama: 0.4, ...}, avg_pacing_pref: 0.5, completion_rate: 0.75 }
    """
    scored = await federated_score(req.candidates, req.user_profile)
    return {
        "scored_count": len(scored),
        "mode": "onnx" if not get_onnx_scorer()._fallback else "rule-based",
        "results": scored,
    }


@router.get("/status")
async def federated_status():
    scorer = get_onnx_scorer()
    return {
        "mode":          "onnx" if not scorer._fallback else "rule-based-fallback",
        "model_loaded":  not scorer._fallback,
        "feature_dim":   8,
        "privacy_note":  "Raw behavioral data never leaves the client in full federated mode.",
    }
