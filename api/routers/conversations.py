"""
Conversational discovery router — "Ask Nexus".
POST /v1/conversations/chat
"""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import require_auth, ApiKey
from pydantic import BaseModel

from catalog.vector_store import get_vector_store
from llm.orchestrator import get_orchestrator
from models import ConversationRequest, ConversationTurn

log = logging.getLogger(__name__)
router = APIRouter()

# In-memory conversation store (Redis in production)
_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    content_suggestions: list[dict]
    intent: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, _auth: ApiKey = Depends(require_auth)):
    """
    Multi-turn conversational discovery.
    Understands mood, context, and preferences via LLM intent extraction.
    Retrieves semantically matching content and generates a warm narrative reply.
    """
    session_key = f"{req.user_id}:{req.session_id}"
    history = _sessions.get(session_key, [])

    llm = get_orchestrator()
    vs = get_vector_store()

    # Extract structured intent
    intent = await llm.extract_intent(req.message, history)
    log.info("Intent extracted: %s", intent)

    # Build search query from intent
    mood = intent.get("mood", "")
    genres = intent.get("genres", [])
    length = intent.get("length", "any")

    search_query = f"{mood} {' '.join(genres)} engaging acclaimed".strip()

    # Length → filter
    length_filter = None
    if length == "short":
        search_query += " short episode series"
    elif length == "long":
        search_query += " epic feature film"

    candidates = await vs.semantic_search(search_query, limit=8)

    # Build candidates summary for LLM
    summary_lines = [
        f"{c.get('title')} ({c.get('year')}): {(c.get('synopsis') or '')[:100]}"
        for c in candidates[:4]
    ]
    candidates_summary = "\n".join(summary_lines)

    # Generate conversational reply
    reply = await llm.converse(
        user_message=req.message,
        history=history,
        candidates_summary=candidates_summary,
    )

    # Append to history
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    _sessions[session_key] = history[-20:]  # Keep last 10 turns

    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        content_suggestions=candidates[:4],
        intent=intent,
    )


@router.delete("/chat/{session_id}")
async def clear_session(user_id: str, session_id: str):
    """Reset a conversation session."""
    key = f"{user_id}:{session_id}"
    _sessions.pop(key, None)
    return {"cleared": True}
