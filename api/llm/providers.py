"""
LLM provider abstractions.

Every concrete backend (Anthropic, OpenAI, Ollama, mock) implements `LLMProvider`.
The orchestrator (`orchestrator.py`) routes traffic to whichever is configured —
swapping providers is a config change, never a code change. This is the MCP-style
hot-swap that the pre-prompt calls for.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMResponse:
    text: str
    usage: dict
    model: str
    structured: dict | None = None  # parsed JSON when the call requested it


class LLMProvider(Protocol):
    name: str

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse: ...


# ───────────────────────────────────────────────────────────────────────────
# Anthropic Claude
# ───────────────────────────────────────────────────────────────────────────

class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        # Coerce roles to anthropic's expected {role, content} shape
        anthropic_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        if json_mode:
            system = system + "\n\nRespond ONLY with valid JSON. No prose, no fences."

        resp = await self._client.messages.create(
            model=self._model,
            system=system,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        structured = None
        if json_mode:
            try:
                structured = json.loads(_strip_json_fences(text))
            except json.JSONDecodeError:
                structured = None

        return LLMResponse(
            text=text,
            usage={"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
            model=resp.model,
            structured=structured,
        )


# ───────────────────────────────────────────────────────────────────────────
# OpenAI
# ───────────────────────────────────────────────────────────────────────────

class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        full = [{"role": "system", "content": system}] + messages
        kwargs = dict(
            model=self._model,
            messages=full,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = await self._client.chat.completions.create(**kwargs)
        text = resp.choices[0].message.content or ""
        structured = None
        if json_mode:
            try:
                structured = json.loads(text)
            except json.JSONDecodeError:
                structured = None
        return LLMResponse(
            text=text,
            usage={
                "input_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "output_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
            model=resp.model,
            structured=structured,
        )


# ───────────────────────────────────────────────────────────────────────────
# Local Ollama (privacy mode)
# ───────────────────────────────────────────────────────────────────────────

class OllamaProvider:
    name = "local"

    def __init__(self, base_url: str, model: str):
        import httpx
        self._client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        full = [{"role": "system", "content": system}] + messages
        payload = {
            "model": self._model,
            "messages": full,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if json_mode:
            payload["format"] = "json"

        r = await self._client.post("/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
        text = data.get("message", {}).get("content", "")
        structured = None
        if json_mode:
            try:
                structured = json.loads(text)
            except json.JSONDecodeError:
                structured = None
        return LLMResponse(
            text=text,
            usage={
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
            model=self._model,
            structured=structured,
        )


# ───────────────────────────────────────────────────────────────────────────
# Mock — for tests and the "no API key configured" graceful degradation path
# ───────────────────────────────────────────────────────────────────────────

class MockProvider:
    """Returns deterministic, sensible responses so the platform demo runs without keys."""
    name = "mock"

    async def complete(
        self,
        system: str,
        messages: list[dict],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        last = messages[-1]["content"] if messages else ""
        if json_mode:
            # Best-effort intent extraction for the conversational endpoint
            structured = {
                "mood": _guess_mood(last),
                "genres": _guess_genres(last),
                "exclude": [],
                "length": "any",
            }
            return LLMResponse(
                text=json.dumps(structured),
                usage={"input_tokens": 0, "output_tokens": 0},
                model="nexus-mock-1",
                structured=structured,
            )
        return LLMResponse(
            text=(
                "I've got a few things that match. "
                "(Demo mode: add an API key to .env to enable rich conversational replies.)"
            ),
            usage={"input_tokens": 0, "output_tokens": 0},
            model="nexus-mock-1",
        )


def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[: -3]
        if t.startswith("json\n"):
            t = t[5:]
    return t.strip()


def _guess_mood(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("rough", "tired", "stressed", "exhausted", "long day")):
        return "comforting"
    if any(w in t for w in ("excited", "thrilling", "intense", "adrenaline")):
        return "intense"
    if any(w in t for w in ("funny", "laugh", "light", "fun")):
        return "playful"
    if any(w in t for w in ("think", "thoughtful", "deep", "complex")):
        return "contemplative"
    return "neutral"


def _guess_genres(text: str) -> list[str]:
    t = text.lower()
    out = []
    pairs = {
        "thriller": ["thriller", "suspense", "tense"],
        "drama":    ["drama", "emotional", "character"],
        "comedy":   ["comedy", "funny", "laugh"],
        "sci-fi":   ["sci-fi", "science fiction", "space"],
        "horror":   ["horror", "scary", "creepy"],
        "romance":  ["romance", "love", "romantic"],
        "action":   ["action", "fight", "chase"],
        "documentary": ["documentary", "real story", "true story"],
    }
    for g, kw in pairs.items():
        if any(k in t for k in kw):
            out.append(g)
    return out
