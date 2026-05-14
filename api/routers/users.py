"""Users router — profile, watch events, preference vectors."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from catalog.graph import get_graph
from catalog.vector_store import get_vector_store

router = APIRouter()


class WatchEvent(BaseModel):
    user_id: str
    content_id: str
    completed: bool = False
    rating: float | None = None
    watch_percentage: float = 0.0


class UserPreferenceUpdate(BaseModel):
    user_id: str
    preference_text: str  # e.g., "psychological thrillers slow burn cinema"


@router.post("/watch-event")
async def record_watch_event(event: WatchEvent):
    """Record that a user watched (or started) a piece of content."""
    graph = get_graph()
    await graph.record_watch(
        user_id=event.user_id,
        content_id=event.content_id,
        completed=event.completed,
        rating=event.rating,
    )
    # Update preference vector if they completed it
    if event.completed or event.watch_percentage > 0.7:
        vs = get_vector_store()
        content_data = await vs.get_by_ids([event.content_id])
        if content_data:
            c = content_data[0]
            pref_text = f"{c.get('title', '')} {' '.join(c.get('genres', []))} {c.get('synopsis', '')[:100]}"
            await vs.upsert_user_vector(event.user_id, pref_text)

    return {"status": "recorded", "user_id": event.user_id, "content_id": event.content_id}


@router.get("/{user_id}/history")
async def get_history(user_id: str, limit: int = 20):
    graph = get_graph()
    history = await graph.get_watch_history(user_id, limit=limit)
    return {"user_id": user_id, "history": history}


@router.get("/{user_id}/taste-profile")
async def get_taste_profile(user_id: str):
    graph = get_graph()
    genre_weights = await graph.get_user_genre_weights(user_id)
    return {
        "user_id": user_id,
        "genre_weights": genre_weights,
        "top_genres": sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)[:5],
    }


@router.put("/preferences")
async def update_preferences(update: UserPreferenceUpdate):
    vs = get_vector_store()
    await vs.upsert_user_vector(update.user_id, update.preference_text)
    return {"status": "updated"}
