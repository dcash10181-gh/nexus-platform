"""Agents router — proactive recommendation agent endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from middleware.auth import require_auth, ApiKey
from pydantic import BaseModel
from agents.proactive import run_proactive_agent, run_proactive_batch

router = APIRouter()


class ProactiveRequest(BaseModel):
    user_id: str


class BatchRequest(BaseModel):
    user_ids: list[str]


@router.post("/proactive")
async def proactive_recommendation(req: ProactiveRequest, _auth: ApiKey = Depends(require_auth)):
    """
    Run the proactive recommendation agent for a single user.
    Returns the 'right now' recommendation with push notification payload.
    This is NEXUS's agentic layer — surfacing content before the user asks.
    """
    result = await run_proactive_agent(req.user_id)
    return result


@router.post("/proactive/batch")
async def proactive_batch(req: BatchRequest):
    """Run the proactive agent concurrently for multiple users."""
    results = await run_proactive_batch(req.user_ids)
    return {"count": len(results), "results": results}


@router.get("/status")
async def agent_status():
    return {
        "agents": [
            {"name": "ProactiveRecommendationAgent", "status": "active", "version": "1.0"},
        ]
    }
