# NEXUS — AI-Native Video & Content Orchestration Platform

> *Production-ready AI recommendation, conversational discovery, and agentic personalization for streaming platforms.*

[![License: Commercial](https://img.shields.io/badge/License-Commercial-blue.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/Deploy-Docker-cyan.svg)](./docker-compose.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](./api)
[![React 18](https://img.shields.io/badge/React-18-blueviolet.svg)](./frontend)
[![Tests](https://img.shields.io/badge/Tests-55%2F55-brightgreen.svg)](./api/tests)

---

## Quick Start

**Requirements:** [Docker Desktop](https://docs.docker.com/get-docker/) — nothing else.

### One-command install

```bash
curl -sSL https://raw.githubusercontent.com/dcash10181-gh/nexus-platform/main/install.sh | bash
```

This clones the repo, starts all services, seeds the catalog, and opens the browser. No API keys required.

### Manual install

```bash
git clone https://github.com/dcash10181-gh/nexus-platform
cd nexus-platform
cp .env.example .env
docker compose up -d
```

Open **http://localhost:3000**

### To stop

```bash
docker compose down
```

### To enable real AI (optional)

Edit `.env`:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```
Restart: `docker compose up -d`

---

## What NEXUS Does

NEXUS is a white-label AI recommendation and content discovery platform for video streaming companies. Five capabilities most streaming platforms don't offer:

| Capability | Description |
|-----------|-------------|
| **Conversational Discovery** | Multi-turn dialogue: "Something like Inception for a rainy evening" → curated results |
| **Explainable Recommendations** | Per-card signal breakdown: "87% match — pacing, director affinity, completion history" |
| **Proactive Agentic Push** | Background agent surfaces content before the user opens the app |
| **Content DNA** | Fingerprint: tension curve, pacing score, visual style, audio mood, thematic tags |
| **Pluggable LLM Intelligence** | Hot-swap Claude / GPT-4o / Llama via one `.env` change — no code required |

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
│   │  MCP Orchestrator — Claude │ GPT-4o │ Llama │ Mock  │    │
│   │  Recommendation Engine (semantic + graph + context) │    │
│   │  LangGraph Proactive Agent (4-node pipeline)        │    │
│   └─────────────────────────────────────────────────────┘    │
│              │                         │                      │
│   ┌──────────────────┐    ┌────────────────────────────┐     │
│   │  Qdrant  :6333   │    │  Neo4j  :7687              │     │
│   │  Vector search   │    │  Knowledge graph           │     │
│   └──────────────────┘    └────────────────────────────┘     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Core API Endpoints

### Recommendations
```http
POST /v1/recommendations/
Authorization: Bearer <api_key>
{"user_id": "usr_123", "context": {"time_of_day": "evening"}, "limit": 24}
```

### Conversational Discovery
```http
POST /v1/conversations/chat
{"user_id": "usr_123", "message": "Something like Inception for a rainy Tuesday night"}
```

### Proactive Agent
```http
POST /v1/agents/proactive
{"user_id": "usr_123"}
```

### Semantic Search
```http
GET /v1/search/?q=psychological+thriller+slow+burn
```

Full interactive docs at **http://localhost:8000/docs**

---

## Configuration

All settings in `.env` (copied from `.env.example` on install):

```env
# LLM — swap without code changes
LLM_PROVIDER=mock              # mock | anthropic | openai | local
ANTHROPIC_API_KEY=             # add key to enable Claude

# Everything else works with defaults
NEO4J_PASSWORD=nexus-dev-password
NEXUS_LICENSE_KEY=trial
```

---

## Project Structure

```
nexus-platform/
├── api/                     # FastAPI recommendation engine
│   ├── main.py              # App entrypoint
│   ├── config.py            # Settings
│   ├── models.py            # Type contracts
│   ├── catalog/             # Qdrant + Neo4j + seeder
│   ├── recommendations/     # Multi-signal scoring engine
│   ├── agents/              # Proactive recommendation agent
│   ├── routers/             # HTTP route handlers
│   ├── llm/                 # MCP-style LLM orchestration
│   └── tests/               # 55 tests, all passing
├── frontend/                # React 18 + Tailwind
│   └── src/components/      # Navbar, HeroSection, AskNexus,
│                            # ExplainabilityPanel, ContentDNAModal
├── docker-compose.yml       # Full self-contained stack
├── api/Dockerfile           # Production Dockerfile
├── install.sh               # One-command installer
└── .env.example             # Default configuration
```

---

## Licensing

| Tier | Price | Users | Tenants |
|------|-------|-------|---------|
| **Trial** (default) | Free | 1,000 / 30 days | 1 |
| **Commercial Annual** | $250K/year | Unlimited | 5 |
| **Enterprise Perpetual** | $2.5M | Unlimited | Unlimited |

See [`LICENSE`](./LICENSE) for full terms.

---

*Built by Duane Cash*
