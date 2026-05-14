"""
Live Content AI Layer — real-time intelligence for live events.

Provides:
  1. 90-second "catch-up" summaries for live sports, news, and events
  2. AI-generated highlight clips index (timestamps + descriptions)
  3. Real-time sentiment and momentum tracking for live broadcasts
  4. Personalized "jump-in point" recommendation based on user interest profile

This is the infrastructure for live content — the AI layer that turns
a raw HLS stream into an intelligent, personalized viewing experience.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from llm.orchestrator import get_orchestrator

log = logging.getLogger(__name__)


# ── Data models ───────────────────────────────────────────────────────────

@dataclass
class LiveMoment:
    """A significant moment detected in a live stream."""
    timestamp_sec: float
    moment_type:   Literal["goal", "highlight", "turning_point", "ad_break", "key_play", "commentary"]
    description:   str
    intensity:     float              # 0..1 excitement/importance score
    tags:          list[str] = field(default_factory=list)
    clip_url:      str = ""           # HLS segment URL for the moment


@dataclass
class LiveSummary:
    """AI-generated catch-up summary for a live event."""
    event_id:      str
    generated_at:  datetime
    summary_text:  str                # 90-second read or ~300 words
    key_moments:   list[LiveMoment]
    sentiment:     Literal["exciting", "tense", "comfortable", "chaotic", "boring"]
    momentum:      float              # -1 (away team/underdog) to +1 (home/favourite)
    jump_in_sec:   float              # Recommended timestamp to join live


@dataclass
class LiveEvent:
    """A registered live event with its accumulated moments."""
    id:          str
    title:       str
    stream_url:  str
    started_at:  datetime
    moments:     list[LiveMoment] = field(default_factory=list)
    is_live:     bool = True


# ── In-memory event store (Redis-backed in production) ───────────────────

_live_events: dict[str, LiveEvent] = {}


def register_live_event(event_id: str, title: str, stream_url: str) -> LiveEvent:
    event = LiveEvent(
        id=event_id,
        title=title,
        stream_url=stream_url,
        started_at=datetime.now(timezone.utc),
    )
    _live_events[event_id] = event
    log.info("Live event registered: %s — %s", event_id, title)
    return event


def ingest_moment(event_id: str, moment: LiveMoment) -> None:
    """Called by the streaming proxy when a significant moment is detected."""
    if event_id in _live_events:
        _live_events[event_id].moments.append(moment)
        log.debug("Moment ingested: %s @ %.1fs", moment.moment_type, moment.timestamp_sec)


def get_event(event_id: str) -> LiveEvent | None:
    return _live_events.get(event_id)


def list_live_events() -> list[LiveEvent]:
    return [e for e in _live_events.values() if e.is_live]


# ── AI Summary Generation ─────────────────────────────────────────────────

async def generate_catchup_summary(event_id: str) -> LiveSummary | None:
    """
    Generate a 90-second catch-up summary for a live event.

    Uses the LLM to synthesize recent moments into a coherent narrative.
    """
    event = _live_events.get(event_id)
    if not event:
        return None

    llm = get_orchestrator()
    now_sec = (datetime.now(timezone.utc) - event.started_at).total_seconds()

    # Take last 20 moments (roughly last 15–30 minutes of a match)
    recent = event.moments[-20:]
    if not recent:
        moments_text = "No significant moments recorded yet."
    else:
        moments_text = "\n".join(
            f"[{int(m.timestamp_sec // 60)}:{int(m.timestamp_sec % 60):02d}] "
            f"{m.moment_type.upper()}: {m.description} (intensity: {m.intensity:.1f})"
            for m in recent
        )

    system = (
        "You are NEXUS Live, an AI sports/events analyst. "
        "Generate a punchy catch-up summary a viewer can read in 90 seconds. "
        "Include: what's happened so far, current score/state if known, the most exciting moment, "
        "and the ideal timestamp to jump in right now. "
        "Return JSON: {summary: str, sentiment: str, momentum: float, jump_in_sec: float}"
    )

    user_msg = (
        f"Event: {event.title}\n"
        f"Duration: {int(now_sec // 60)} minutes live\n"
        f"Recent moments:\n{moments_text}"
    )

    resp = await llm.complete(
        system=system,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.4,
        max_tokens=512,
        json_mode=True,
    )

    data = resp.structured or {}
    sentiment = data.get("sentiment", "exciting")
    if sentiment not in ("exciting", "tense", "comfortable", "chaotic", "boring"):
        sentiment = "exciting"

    # Select top 5 moments by intensity for the summary
    top_moments = sorted(recent, key=lambda m: m.intensity, reverse=True)[:5]

    return LiveSummary(
        event_id=event_id,
        generated_at=datetime.now(timezone.utc),
        summary_text=data.get("summary", f"{event.title} is currently live."),
        key_moments=top_moments,
        sentiment=sentiment,
        momentum=float(data.get("momentum", 0.0)),
        jump_in_sec=float(data.get("jump_in_sec", max(0, now_sec - 120))),
    )


async def get_personalized_jump_point(event_id: str, user_profile: dict) -> float:
    """
    Suggest the best timestamp for THIS user to jump into the live event,
    based on their interest profile.

    E.g., a user who loves tactical analysis → join at a tactical turning point.
         a user who loves goals/highlights → jump to highest-intensity moment.
    """
    event = _live_events.get(event_id)
    if not event or not event.moments:
        return 0.0

    genre_weights = user_profile.get("genre_weights", {})
    prefers_action = genre_weights.get("Action", 0) + genre_weights.get("Thriller", 0)
    prefers_drama  = genre_weights.get("Drama", 0)

    if prefers_action > 0.3:
        # Find the highest-intensity moment in the last 30 minutes
        recent_cutoff = (datetime.now(timezone.utc) - event.started_at).total_seconds() - 1800
        recent = [m for m in event.moments if m.timestamp_sec > recent_cutoff]
        if recent:
            best = max(recent, key=lambda m: m.intensity)
            return max(0.0, best.timestamp_sec - 30)  # 30s before the action

    # Default: 2 minutes before live
    now_sec = (datetime.now(timezone.utc) - event.started_at).total_seconds()
    return max(0.0, now_sec - 120)


# ── Live router helpers ────────────────────────────────────────────────────

def simulate_live_moments(event_id: str, count: int = 10) -> None:
    """
    Inject simulated live moments for demo/testing purposes.
    In production, moments are ingested from the streaming proxy.
    """
    import random
    event = _live_events.get(event_id)
    if not event:
        return

    moment_types = ["goal", "highlight", "turning_point", "key_play", "commentary"]
    descriptions = [
        "Stunning long-range strike into the top corner",
        "Counter-attack breaks defensive line",
        "VAR decision reverses the ruling",
        "Yellow card — tempers flaring on the pitch",
        "Substitution changes the tactical dynamic",
        "Near miss — goalkeeper scrambles to save",
        "Corner kick cleared off the line",
        "Clinical finish from close range",
        "Midfield press wins the ball back in dangerous position",
        "Slow-motion replay confirms the controversial decision",
    ]

    now_sec = (datetime.now(timezone.utc) - event.started_at).total_seconds()
    for i in range(count):
        moment = LiveMoment(
            timestamp_sec=max(0, now_sec - random.randint(60, 2700)),
            moment_type=random.choice(moment_types),
            description=random.choice(descriptions),
            intensity=round(random.uniform(0.3, 1.0), 2),
            tags=random.sample(["attack", "defense", "midfield", "VAR", "set-piece"], 2),
        )
        event.moments.append(moment)

    event.moments.sort(key=lambda m: m.timestamp_sec)
    log.info("Injected %d simulated moments into event %s", count, event_id)
