"""
Proactive recommendation agent — NEXUS's agentic layer.

Uses LangGraph to orchestrate a multi-step agent that:
  1. Checks user activity patterns (last watch time, completion rates, day-of-week)
  2. Evaluates new content arrivals against user profile
  3. Generates a personalised "right now" recommendation moment
  4. Produces a push notification payload and an in-app banner message
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, TypedDict

from catalog.graph import get_graph
from catalog.vector_store import get_vector_store
from llm.orchestrator import get_orchestrator
from models import Content, Signal

log = logging.getLogger(__name__)


# ── Agent state schema ────────────────────────────────────────────────────

class AgentState(TypedDict):
    user_id: str
    time_of_day: str          # morning | afternoon | evening | night
    day_of_week: str
    recent_watch_ids: list[str]
    genre_weights: dict[str, float]
    candidate_titles: list[dict]
    recommendation: dict | None
    notification_text: str
    reasoning: str


# ── Node implementations ─────────────────────────────────────────────────

async def node_gather_context(state: AgentState) -> AgentState:
    """Fetch user context from graph and vector store."""
    graph = get_graph()
    uid = state["user_id"]

    recent = await graph.get_watch_history(uid, limit=10)
    genre_weights = await graph.get_user_genre_weights(uid)

    now = datetime.now(timezone.utc)
    hour = now.hour
    if 5 <= hour < 12:
        tod = "morning"
    elif 12 <= hour < 17:
        tod = "afternoon"
    elif 17 <= hour < 22:
        tod = "evening"
    else:
        tod = "night"

    return {
        **state,
        "recent_watch_ids": recent,
        "genre_weights": genre_weights,
        "time_of_day": tod,
        "day_of_week": now.strftime("%A"),
    }


async def node_retrieve_candidates(state: AgentState) -> AgentState:
    """Get fresh candidates using the user's preference vector."""
    vs = get_vector_store()
    # Build a mood query from genre weights
    top_genres = sorted(state["genre_weights"].items(), key=lambda x: x[1], reverse=True)[:3]
    genre_query = " ".join(g for g, _ in top_genres) if top_genres else "acclaimed engaging"

    candidates = await vs.personalized_search(
        user_id=state["user_id"],
        query=genre_query,
        limit=15,
    )
    # Exclude recently watched
    watched = set(state["recent_watch_ids"])
    fresh = [c for c in candidates if c.get("id") not in watched]

    return {**state, "candidate_titles": fresh[:8]}


async def node_reason_and_select(state: AgentState) -> AgentState:
    """LLM-powered reasoning step: pick the single best 'right now' recommendation."""
    if not state["candidate_titles"]:
        return {**state, "recommendation": None, "reasoning": "No fresh candidates found."}

    llm = get_orchestrator()

    candidates_text = "\n".join(
        f"- {c.get('title', '?')} ({c.get('year', '?')}, {', '.join(c.get('genres', []))}): "
        f"{c.get('synopsis', '')[:120]}"
        for c in state["candidate_titles"]
    )

    top_genres = [g for g, _ in sorted(state["genre_weights"].items(), key=lambda x: x[1], reverse=True)[:4]]

    system = (
        "You are NEXUS's proactive recommendation agent. "
        "Select the SINGLE best content item for the user RIGHT NOW based on: "
        "their genre preferences, current time of day, and day of week. "
        "Return JSON: {chosen_index: int, reasoning: str (≤25 words), notification: str (≤15 words, warm tone)}"
    )
    user_msg = (
        f"Time: {state['time_of_day']}, Day: {state['day_of_week']}\n"
        f"User's top genres: {', '.join(top_genres)}\n\n"
        f"Candidates:\n{candidates_text}"
    )

    response = await llm.complete(
        system=system,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
        max_tokens=256,
        json_mode=True,
    )

    result = response.structured or {}
    chosen_idx = result.get("chosen_index", 0)
    candidates = state["candidate_titles"]
    chosen = candidates[min(chosen_idx, len(candidates) - 1)] if candidates else None

    return {
        **state,
        "recommendation": chosen,
        "reasoning": result.get("reasoning", "Matches your current preferences."),
        "notification_text": result.get("notification", "Something perfect is waiting for you."),
    }


async def node_format_output(state: AgentState) -> AgentState:
    """Attach metadata and finalise the push payload."""
    if not state["recommendation"]:
        return state

    rec = state["recommendation"]
    rec["agent_reasoning"] = state["reasoning"]
    rec["push_notification"] = {
        "title": "Perfect for right now ✦",
        "body": state["notification_text"],
        "content_id": rec.get("id"),
        "content_title": rec.get("title"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return {**state, "recommendation": rec}


# ── Simple async graph runner (no langgraph dep at runtime) ──────────────

AGENT_NODES = [
    node_gather_context,
    node_retrieve_candidates,
    node_reason_and_select,
    node_format_output,
]


async def run_proactive_agent(user_id: str) -> dict:
    """
    Execute the proactive agent pipeline for a given user.
    Returns the final recommendation dict with push payload attached.
    """
    state: AgentState = {
        "user_id": user_id,
        "time_of_day": "evening",
        "day_of_week": "Monday",
        "recent_watch_ids": [],
        "genre_weights": {},
        "candidate_titles": [],
        "recommendation": None,
        "notification_text": "",
        "reasoning": "",
    }

    for node in AGENT_NODES:
        try:
            state = await node(state)
        except Exception as e:
            log.error("Agent node %s failed: %s", node.__name__, e)
            break

    rec = state.get("recommendation")
    if not rec:
        return {"status": "no_recommendation", "user_id": user_id}

    return {
        "status": "ok",
        "user_id": user_id,
        "content": rec,
        "push_notification": rec.get("push_notification", {}),
        "reasoning": state.get("reasoning", ""),
    }


async def run_proactive_batch(user_ids: list[str]) -> list[dict]:
    """Run proactive agent for multiple users concurrently."""
    return await asyncio.gather(*[run_proactive_agent(uid) for uid in user_ids])
