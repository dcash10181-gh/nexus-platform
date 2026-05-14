"""
LLMOrchestrator — the MCP-style routing layer.

Every part of NEXUS that needs language understanding (conversational discovery,
intent extraction, content DNA enrichment, explainability narratives, proactive
agent reasoning) calls this orchestrator. Provider selection is config-driven;
swapping Anthropic → OpenAI → local Llama is a one-line .env change.

The "MCP" framing in the project brief refers to this provider-abstraction pattern:
the platform treats LLMs as interchangeable tools, exposing a uniform contract so
licensees can plug in their preferred model without code changes.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from config import get_settings
from .providers import (
    AnthropicProvider,
    LLMProvider,
    LLMResponse,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)

log = logging.getLogger(__name__)


class LLMOrchestrator:
    """Single entry point for all LLM calls in NEXUS."""

    def __init__(self, primary: LLMProvider, fallback: LLMProvider | None = None):
        self._primary = primary
        self._fallback = fallback

    @property
    def provider_name(self) -> str:
        return self._primary.name

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        try:
            return await self._primary.complete(
                system, messages,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )
        except Exception as exc:
            log.warning("primary LLM failed: %s — falling back", exc)
            if self._fallback is None:
                # Last resort: mock keeps the demo alive even on outages
                return await MockProvider().complete(
                    system, messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
            return await self._fallback.complete(
                system, messages,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )

    async def extract_intent(self, user_message: str, history: list[dict]) -> dict:
        """Parse a user's natural-language query into a structured intent dict.

        Output schema:
          { mood: str, genres: [str], exclude: [str], length: "short|medium|long|any" }
        """
        system = (
            "You parse a viewer's casual request into a recommendation intent. "
            "Return a JSON object with: mood (one word), genres (array of common genres), "
            "exclude (array of titles/keywords they don't want), length "
            "(short|medium|long|any). Keep it terse."
        )
        msgs = history + [{"role": "user", "content": user_message}]
        resp = await self.complete(
            system, msgs, temperature=0.2, max_tokens=256, json_mode=True
        )
        return resp.structured or {"mood": "neutral", "genres": [], "exclude": [], "length": "any"}

    async def converse(
        self,
        user_message: str,
        history: list[dict],
        candidates_summary: str,
    ) -> str:
        """Generate the conversational reply, grounded in retrieved candidates."""
        system = (
            "You are NEXUS, a thoughtful film and series concierge. "
            "Given a viewer's message and a short list of candidate titles, "
            "reply in 2-3 sentences. Reference 1-2 titles by name, explain *why* in "
            "specific terms (pacing, mood, what reminded you of their request). "
            "Never list more than 3 titles. Conversational, warm, never salesy."
            f"\n\nCandidates:\n{candidates_summary}"
        )
        msgs = history + [{"role": "user", "content": user_message}]
        resp = await self.complete(system, msgs, temperature=0.6, max_tokens=400)
        return resp.text


# ───────────────────────────────────────────────────────────────────────────
# Factory
# ───────────────────────────────────────────────────────────────────────────

def _build_provider(name: str) -> LLMProvider:
    s = get_settings()
    match name:
        case "anthropic" if s.anthropic_api_key:
            return AnthropicProvider(s.anthropic_api_key, s.anthropic_model)
        case "openai" if s.openai_api_key:
            return OpenAIProvider(s.openai_api_key, s.openai_model)
        case "local":
            return OllamaProvider(s.ollama_base_url, s.ollama_model)
        case "mock":
            return MockProvider()
        case _:
            log.warning("LLM provider %s not configured — using mock", name)
            return MockProvider()


@lru_cache
def get_orchestrator() -> LLMOrchestrator:
    s = get_settings()
    primary = _build_provider(s.llm_provider)
    # Mock fallback ensures the demo never hard-fails
    fallback = MockProvider() if primary.name != "mock" else None
    return LLMOrchestrator(primary=primary, fallback=fallback)
