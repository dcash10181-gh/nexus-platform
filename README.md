# NEXUS — AI-Native Video & Content Orchestration Platform

> *Production-ready AI recommendation, conversational discovery, and agentic personalization for streaming platforms.*

[![License: Commercial](https://img.shields.io/badge/License-Commercial-blue.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/Deploy-Docker-cyan.svg)](./docker-compose.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](./api)
[![React 18](https://img.shields.io/badge/React-18-blueviolet.svg)](./frontend)

---

## 30-Second Deploy

```bash
curl -sSL https://get.nexus.ai | bash
# Then open http://localhost:3000
```

Or clone and run locally:

```bash
git clone https://github.com/duanecash/nexus-platform
cd nexus-platform
cp .env.example .env          # add ANTHROPIC_API_KEY for full AI
docker compose up -d
```

---

## What NEXUS Does

NEXUS is a white-label AI recommendation and content discovery platform for video streaming companies. It ships five capabilities that most streaming platforms do not yet offer their users:

| Capability | Description |
|-----------|-------------|
| **Conversational Discovery** | Multi-turn LLM dialogue: "Something like Inception for a rainy evening" → curated results |
| **Explainable Recommendations** | Per-card signal breakdown: "87% match — pacing, director affinity, completion history" |
| **Proactive Agentic Push** | Background agent surfaces content before the user opens the app |
| **Content DNA** | Multi-modal fingerprint: tension curve, pacing score, visual style, audio mood, thematic tags |
| **Pluggable LLM Intelligence** | Hot-swap Claude / GPT-4o / Llama via `.env` — no code changes required |

---

## Architecture

```
┌─────────────────── NEXUS Platform ───────────────────────────┐
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │  React Frontend  :3000                               │    │
│   │  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│   │  │  Ask NEXUS   │  │Explainability│  │Content DNA │ │    │
│   │  │  (CRS Chat)  │  │   Panel      │  │  Modal     │ │    │
│   │  └──────────────┘  └─────────────┘  └────────────┘ │    │
│   └─────────────────────────────────────────────────────┘    │
│                           │ HTTP                              │
│   ┌─────────────────────────────────────────────────────┐    │
│   │  FastAPI  :8000                                      │    │
│   │  ┌───────────┐ ┌──────────┐ ┌──────────────────┐   │    │
│   │  │  /v1/recs │ │ /v1/chat │ │  /v1/agents      │   │    │
│   │  └───────────┘ └──────────┘ └──────────────────┘   │    │
│   │                                                      │    │
│   │  ┌──────────────────────────────────────────────┐   │    │
│   │  │  MCP Orchestrator — LLM Layer                │   │    │
│   │  │  Claude Sonnet │ GPT-4o │ Llama3 │ Mock      │   │    │
│   │  └──────────────────────────────────────────────┘   │    │
│   │                                                      │    │
│   │  ┌──────────────────┐  ┌──────────────────────────┐ │    │
│   │  │  Recommendation  │  │  LangGraph Proactive      │ │    │
│   │  │  Engine          │  │  Agent (4-node loop)      │ │    │
│   │  │  semantic+graph  │  │  gather→retrieve→reason   │ │    │
│   │  └──────────────────┘  └──────────────────────────┘ │    │
│   └─────────────────────────────────────────────────────┘    │
│              │                         │                      │
│   ┌──────────────────┐    ┌────────────────────────────┐     │
│   │  Qdrant  :6333   │    │  Neo4j  :7687              │     │
│   │  Content vectors │    │  Knowledge graph           │     │
│   │  User pref vecs  │    │  (User→Content→Genre→      │     │
│   │  384-dim cosine  │    │   Theme→Person)            │     │
│   └──────────────────┘    └────────────────────────────┘     │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │  HLS Streaming Proxy  :8001  (Node.js)               │    │
│   └─────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Core API Endpoints

### Recommendations
```http
POST /v1/recommendations/
{
  "user_id": "usr_123",
  "context": { "time_of_day": "evening", "device": "tv" },
  "limit": 24
}
```

### Conversational Discovery ("Ask NEXUS")
```http
POST /v1/conversations/chat
{
  "user_id": "usr_123",
  "message": "Something like Inception but for a rainy Tuesday night",
  "session_id": "sess_abc"
}
```

### Proactive Agent
```http
POST /v1/agents/proactive
{ "user_id": "usr_123" }

// Returns:
{
  "status": "ok",
  "content": { "title": "Severance", ... },
  "push_notification": { "body": "Severance is calling your name tonight ✦" },
  "reasoning": "Friday evening, completed Silo last Tuesday, 94% pacing match"
}
```

### Semantic Search
```http
GET /v1/search/?q=psychological+thriller+slow+burn+atmospheric
```

---

## Configuration

Edit `.env` to configure:

```env
# LLM — swap at runtime without code changes
LLM_PROVIDER=anthropic          # anthropic | openai | local | mock
ANTHROPIC_API_KEY=sk-ant-...    # required for anthropic provider
OPENAI_API_KEY=sk-...           # optional alternative

# Licensing
NEXUS_LICENSE_KEY=trial         # 30 days / 1,000 users free
                                # purchase at nexus.ai/pricing for production

# Infrastructure (Docker defaults)
QDRANT_URL=http://qdrant:6333
NEO4J_URI=bolt://neo4j:7687
```

---

## Project Structure

```
nexus-platform/
├── api/                     # FastAPI recommendation engine
│   ├── main.py              # App entrypoint, lifespan, routers
│   ├── config.py            # Pydantic settings, env vars
│   ├── models.py            # Type contracts (Content, Signal, Recommendation)
│   ├── catalog/
│   │   ├── vector_store.py  # Qdrant async wrapper
│   │   ├── graph.py         # Neo4j knowledge graph
│   │   └── seed.py          # Curated catalog seed (40 titles)
│   ├── recommendations/
│   │   └── engine.py        # Multi-signal scoring + MMR diversity
│   ├── agents/
│   │   └── proactive.py     # 4-node proactive recommendation agent
│   ├── routers/             # FastAPI route handlers
│   └── llm/
│       ├── orchestrator.py  # MCP-style LLM router
│       └── providers.py     # Anthropic, OpenAI, Ollama, Mock
├── frontend/                # React 18 + Tailwind + Framer Motion
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── Navbar.jsx
│           ├── HeroSection.jsx
│           ├── ContentRow.jsx           # Horizontal scroll with content cards
│           ├── AskNexus.jsx             # Conversational discovery overlay
│           ├── ExplainabilityPanel.jsx  # Signal breakdown ("Why this?")
│           ├── ContentDNAModal.jsx      # Tension curve + full DNA view
│           └── ProactiveAlert.jsx       # Agent push notification UI
├── streaming/               # Node.js HLS proxy
├── docker-compose.yml       # Full stack (API, DBs, Frontend, Seeder)
├── install.sh               # Single-command installer
└── LICENSE                  # Commercial license terms
```

---

## Licensing

NEXUS is available in three tiers:

| Tier | Price | Users | Tenants | Source |
|------|-------|-------|---------|--------|
| **Trial** (GitHub default) | Free | 1,000 / 30 days | 1 | ❌ |
| **Commercial Annual** | $250K/year | Unlimited | 5 | ❌ |
| **Enterprise Perpetual** | $2.5M | Unlimited | Unlimited | ✅ |

Production use without a valid license key is prohibited. See [`LICENSE`](./LICENSE) for full terms.

---

*Built by Duane Cash · duanecash@nexus.ai*
