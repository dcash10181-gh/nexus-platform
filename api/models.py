"""
Shared Pydantic models. The typed contract between every layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ─── Content domain ────────────────────────────────────────────────────────

class ContentDNA(BaseModel):
    """The multi-modal fingerprint of a title. Section 4 of the pre-prompt."""
    pacing: float = Field(..., ge=0, le=1, description="0=slow burn, 1=relentless")
    tension_curve: list[float] = Field(default_factory=list, description="Normalized intensity per act")
    visual_style: str  # "cinematic" | "gritty" | "stylized" | "naturalistic" | etc.
    audio_mood: str    # "ominous" | "uplifting" | "melancholic" | "playful" | etc.
    thematic_tags: list[str] = Field(default_factory=list)
    runtime_min: int


class Content(BaseModel):
    id: str
    title: str
    year: int
    kind: Literal["film", "series", "limited", "live"]
    synopsis: str
    genres: list[str]
    cast: list[str] = Field(default_factory=list)
    director: Optional[str] = None
    poster_url: str = ""
    backdrop_url: str = ""
    rating: float = 0.0
    dna: Optional[ContentDNA] = None


# ─── Recommendations ───────────────────────────────────────────────────────

class Signal(BaseModel):
    """A single explainable contribution to a recommendation score."""
    name: str             # "Semantic match", "Director affinity", "Tuesday-night pattern"
    weight: float         # contribution to final score, 0..1
    detail: str           # human-readable specifics
    icon: str = "pulse"   # frontend icon hint


class Recommendation(BaseModel):
    content: Content
    score: float
    rank: int
    signals: list[Signal] = Field(default_factory=list)
    confidence: float = 0.0  # model's calibrated confidence


class RecommendationRequest(BaseModel):
    user_id: str
    context: dict = Field(default_factory=dict)
    # context can carry: time_of_day, device, mood_hint, exclude_ids, etc.
    limit: int = 24


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
    generated_at: datetime
    model_version: str
    latency_ms: int


# ─── Conversational discovery ──────────────────────────────────────────────

class ConversationTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None


class ConversationRequest(BaseModel):
    user_id: str
    message: str
    history: list[ConversationTurn] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    extracted_intent: dict = Field(default_factory=dict)
    follow_up_suggestions: list[str] = Field(default_factory=list)


# ─── User preferences (transparency panel) ─────────────────────────────────

class SignalWeight(BaseModel):
    """A user-adjustable weight on a recommendation signal."""
    signal: str
    weight: float = Field(..., ge=0, le=1)
    enabled: bool = True


class UserPreferences(BaseModel):
    user_id: str
    signal_weights: list[SignalWeight] = Field(default_factory=list)
    privacy_mode: Literal["full", "federated", "local_only"] = "full"
    proactive_push_enabled: bool = True


# ─── System & licensing ────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "down"]
    version: str
    llm_provider: str
    llm_configured: bool
    vector_store: bool
    knowledge_graph: bool
    license_tier: str


class LicenseInfo(BaseModel):
    tier: Literal["trial", "saas", "enterprise"]
    expires_at: Optional[datetime] = None
    user_cap: Optional[int] = None
    features: list[str]
    watermark: bool
