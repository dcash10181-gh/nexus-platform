"""
Live Content AI router.

GET  /v1/live/events                       — List active live events
POST /v1/live/events                       — Register a new live event
GET  /v1/live/events/{id}/summary          — AI catch-up summary
GET  /v1/live/events/{id}/jump-point       — Personalized jump-in timestamp
POST /v1/live/events/{id}/moments          — Ingest a new moment (from streaming proxy)
POST /v1/live/events/{id}/simulate         — Inject demo moments (dev only)
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from inference.live_ai import (
    LiveMoment,
    register_live_event,
    ingest_moment,
    get_event,
    list_live_events,
    generate_catchup_summary,
    get_personalized_jump_point,
    simulate_live_moments,
)

router = APIRouter()


class RegisterEventRequest(BaseModel):
    id: str
    title: str
    stream_url: str = ""


class MomentIngestRequest(BaseModel):
    timestamp_sec: float
    moment_type: Literal["goal", "highlight", "turning_point", "ad_break", "key_play", "commentary"]
    description: str
    intensity: float = 0.5
    tags: list[str] = []
    clip_url: str = ""


@router.get("/events")
async def get_live_events():
    events = list_live_events()
    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "started_at": e.started_at.isoformat(),
                "moment_count": len(e.moments),
                "is_live": e.is_live,
            }
            for e in events
        ],
    }


@router.post("/events")
async def create_live_event(req: RegisterEventRequest):
    event = register_live_event(req.id, req.title, req.stream_url)
    return {"id": event.id, "title": event.title, "status": "registered"}


@router.get("/events/{event_id}/summary")
async def catchup_summary(event_id: str):
    """AI-generated 90-second catch-up summary for a live event."""
    event = get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")

    summary = await generate_catchup_summary(event_id)
    if not summary:
        raise HTTPException(status_code=503, detail="Summary generation failed")

    return {
        "event_id": event_id,
        "title": event.title,
        "generated_at": summary.generated_at.isoformat(),
        "summary": summary.summary_text,
        "sentiment": summary.sentiment,
        "momentum": summary.momentum,
        "jump_in_sec": summary.jump_in_sec,
        "key_moments": [
            {
                "timestamp_sec": m.timestamp_sec,
                "type": m.moment_type,
                "description": m.description,
                "intensity": m.intensity,
            }
            for m in summary.key_moments
        ],
    }


@router.get("/events/{event_id}/jump-point")
async def jump_point(event_id: str, user_id: str = "anonymous"):
    """Personalized jump-in timestamp for a user."""
    from catalog.graph import get_graph
    graph = get_graph()

    try:
        genre_weights = await graph.get_user_genre_weights(user_id)
    except Exception:
        genre_weights = {}

    ts = await get_personalized_jump_point(event_id, {"genre_weights": genre_weights})
    return {
        "event_id": event_id,
        "user_id": user_id,
        "jump_in_sec": ts,
        "jump_in_formatted": f"{int(ts // 60)}:{int(ts % 60):02d}",
    }


@router.post("/events/{event_id}/moments")
async def ingest_live_moment(event_id: str, req: MomentIngestRequest):
    """Ingest a live moment from the streaming proxy."""
    event = get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    moment = LiveMoment(
        timestamp_sec=req.timestamp_sec,
        moment_type=req.moment_type,
        description=req.description,
        intensity=req.intensity,
        tags=req.tags,
        clip_url=req.clip_url,
    )
    ingest_moment(event_id, moment)
    return {"status": "ingested", "moment_count": len(event.moments)}


@router.post("/events/{event_id}/simulate")
async def simulate_moments(event_id: str, count: int = 10):
    """Inject simulated moments for demo/testing (dev only)."""
    event = get_event(event_id)
    if not event:
        # Auto-create for demo
        register_live_event(event_id, f"Demo Event: {event_id}", "")
    simulate_live_moments(event_id, count)
    event = get_event(event_id)
    return {"status": "simulated", "total_moments": len(event.moments)}
