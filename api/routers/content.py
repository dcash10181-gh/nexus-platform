"""Content router — catalog lookup and Content DNA."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from catalog.graph import get_graph
from catalog.vector_store import get_vector_store

router = APIRouter()


@router.get("/{content_id}")
async def get_content(content_id: str):
    graph = get_graph()
    item = await graph.get_content_by_id(content_id)
    if not item:
        # Fallback to vector store
        vs = get_vector_store()
        items = await vs.get_by_ids([content_id])
        if not items:
            raise HTTPException(status_code=404, detail="Content not found")
        item = items[0]
    return item


@router.get("/{content_id}/similar")
async def get_similar(content_id: str, limit: int = 12):
    vs = get_vector_store()
    similar = await vs.get_similar(content_id, limit=limit)
    return {"content_id": content_id, "similar": similar}


@router.get("/{content_id}/graph-connections")
async def get_graph_connections(content_id: str, limit: int = 10):
    graph = get_graph()
    connections = await graph.get_because_you_watched(content_id, limit=limit)
    return {"content_id": content_id, "connections": connections}
