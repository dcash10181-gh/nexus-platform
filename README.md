# NEXUS — Conversational AI for Video Discovery

A solo-built, production-shaped recommendation and conversational-discovery system for video catalogs. Natural-language discovery ("something like *Inception* for a rainy night"), explainable recommendations, and a pluggable LLM layer — running locally with one command, no API keys required.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](./api)
[![React 18](https://img.shields.io/badge/React-18-blueviolet.svg)](./frontend)
[![Tests](https://img.shields.io/badge/Tests-55%2F55_passing-brightgreen.svg)](./api/tests)
[![Docker](https://img.shields.io/badge/Run-one_command-cyan.svg)](#run-it)

> **What this is:** a personal engineering project exploring how LLMs, vector search, and a knowledge graph combine into a conversational recommendation system — the problem space Netflix, Spotify, and Amazon staff entire research teams against. Built end-to-end (backend, frontend, infra, tests) by one person to demonstrate that.

---

## Why this project exists

Content discovery is the core retention problem for any streaming catalog: the titles that dominate conversation draw a small fraction of traffic, and everything else needs to be *discovered*. The interesting engineering question is how to turn a vague human intent — "something tense but not violent, like early *True Detective*" — into a ranked, explainable set of results.

NEXUS is my exploration of that question, built as a complete system rather than a notebook:

- A **conversational discovery** layer that parses free-form intent into structured preferences and grounds responses in the actual catalog.
- A **multi-signal recommendation engine** (semantic similarity + graph relationships + session context) rather than a single embedding lookup.
- An **explainability layer** that exposes *why* each title was surfaced — pacing, thematic overlap, completion patterns.
- A **provider-agnostic LLM abstraction** so the intelligence layer is swappable (Claude / GPT / local Llama / a deterministic mock) via config, never code.

---

## Run it

**Requires:** Docker Desktop. Nothing else.

```bash
curl -sSL https://raw.githubusercontent.com/dcash10181-gh/nexus-platform/main/install.sh | bash
```

This clones the repo, builds and starts the stack, seeds a 98-title catalog, and opens the app. First run takes ~2 minutes (image build + model download). It runs **entirely on your machine with no API keys** — the LLM layer defaults to a deterministic mock provider so the system is fully functional offline.

Then open **http://localhost:3000** · API docs at **http://localhost:8000/docs**

To stop: `docker compose down`

### Enabling real LLM inference (optional)

The mock provider demonstrates the full flow deterministically. To use real inference, set one env var — no code changes:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.groq.com/openai/v1   # or any OpenAI-compatible endpoint
OPENAI_MODEL=llama-3.3-70b-versatile
```

---

## What's real vs. simulated

Being explicit, because it matters for reading the code honestly:

| Component | Status |
|-----------|--------|
| Conversational intent parsing, orchestration, multi-turn session state | **Real** |
| Multi-signal recommendation scoring (semantic + graph + context) | **Real** |
| Vector search (Qdrant), knowledge graph (Neo4j) | **Real**, runs in the stack |
| LLM provider abstraction (Claude / OpenAI-compatible / Ollama / Mock) | **Real**; mock is the zero-config default |
| Catalog (98 titles, full metadata + "content DNA") | **Real**, curated/seeded |
| User behavior, completion history, A/B metrics | **Simulated** — no real user base |
| Licensing / multi-tenancy scaffolding | **Real code, illustrative** — not a deployed product |

The mock LLM provider is a deliberate design choice, not a shortcut: the provider interface is the seam that makes the intelligence layer swappable, and a deterministic mock makes the system runnable offline and testable in CI without paid keys.

---

## Architecture

```
+------------------- NEXUS --------------------------------------+
|  React Frontend  :3000                                         |
|   Ask NEXUS (chat)  .  Explainability Panel  .  Content DNA    |
|                          | HTTP                                |
|  FastAPI  :8000                                                |
|   LLM Orchestrator  -  Claude | OpenAI-compat | Llama | Mock   |
|   Recommendation Engine  (semantic + graph + context)         |
|   LangGraph proactive agent  (multi-node pipeline)            |
|           |                              |                     |
|  Qdrant :6333                    Neo4j :7687                   |
|  Vector search                   Knowledge graph               |
+----------------------------------------------------------------+
```

**Stack:** FastAPI (Python 3.12), React 18 + Tailwind, Qdrant (vectors), Neo4j (graph), LangGraph (agent), Docker Compose. ~900 lines of core AI logic across the orchestrator, engine, providers, and agent; 55 tests passing in CI.

---

## Design decisions

The non-obvious choices, with reasoning recorded as ADRs in [`docs/knowledge-base/`](./docs/knowledge-base):

- **Provider-agnostic LLM layer over a hardcoded SDK call.** The orchestrator depends on an `LLMProvider` protocol; concrete backends (Anthropic, OpenAI-compatible, Ollama, Mock) are interchangeable via config. Swapping Claude to a free Groq endpoint is an env change. ([providers.py](./api/llm/providers.py))
- **Multi-signal scoring, not a single embedding lookup.** Recommendations blend semantic similarity, knowledge-graph relationships, and session context, each contributing an explainable signal — which is what makes the "87% match because..." breakdown possible. ([engine.py](./api/recommendations/engine.py))
- **Graceful degradation on startup.** The API boots and serves even if Qdrant or Neo4j are slow or unavailable — it warns rather than crashes — so a partial stack still demos. ([main.py](./api/main.py))
- **Single source of truth for the catalog.** Defined once in the backend seed and exported to the frontend, after an incident where the frontend, the mock responses, and the graph edges had drifted to three different title sets. Write-up: [CATALOG_INTEGRITY.md](./docs/knowledge-base/CATALOG_INTEGRITY.md).

---

## Project structure

```
api/
  main.py            App entrypoint, startup lifecycle
  llm/               Provider-agnostic LLM orchestration
  recommendations/   Multi-signal scoring engine
  agents/            LangGraph proactive recommendation agent
  catalog/           Qdrant + Neo4j + seeder
  routers/           HTTP handlers
  tests/             55 tests
frontend/src/        React 18 + Tailwind components
docs/knowledge-base/ Architecture decision records & runbooks
docker-compose.yml   Self-contained stack
install.sh           One-command installer
```

---

## Known limitations & next steps

Honest about the gaps:

- **No real user data**, so collaborative-filtering signals are simulated. The architecture supports it; the data doesn't exist.
- **Mock LLM is the default.** Real inference works but isn't wired to a hosted demo (cost-constrained, solo).
- **Conversational quality is bounded by the mock** unless a real provider is configured — the orchestration and grounding are real, the language generation is canned offline.
- **Next:** swap the mock for a hosted free-tier model on a public demo URL; add fuzzy title matching to absorb speech-to-text drift; replace the in-memory session/key stores with Redis.

---

*Built by Duane Cash. This is a personal engineering project, not a commercial product.*
