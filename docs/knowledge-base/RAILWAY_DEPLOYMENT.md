# Railway Deployment Runbook — NEXUS conversational demo

**Goal:** one public URL to point a prospect at, running real LLM inference, on free tiers, as a single Railway service.

## Architecture (why one service)

The demo ships as a **single container**: FastAPI serves both the API and the
built React SPA. This avoids cross-service networking, CORS, and the multi-DB
resource blowout that makes the 5-service Compose stack unsuitable for Railway's
free tier. Neo4j and the seeder are dropped (the conversational layer doesn't
need the graph). Qdrant runs on its own Cloud free tier, external to Railway.

- `Dockerfile` (repo root): builds the frontend, copies `dist/` into the API
  image, serves both. Controlled by `SERVE_FRONTEND=true`.
- `railway.json`: tells Railway to build from the Dockerfile, health-check `/health`.
- `.env.railway.example`: the variables to set in Railway.

## One-time setup

1. **Generate a demo API key:**
   ```
   python3 -c "import secrets; print('nxk_trial_'+secrets.token_hex(16))"
   ```
   Save it — you'll use the SAME value in two places below.

2. **Get a free Groq key** at console.groq.com (OpenAI-compatible, real inference, $0).

3. **Qdrant Cloud free tier** — create a cluster, copy its URL and API key.

## Deploy

1. Push this branch to GitHub (the Dockerfile + railway.json must be in the repo).
2. In Railway: New Project → Deploy from GitHub repo → select `nexus-platform`.
3. Railway detects `railway.json` and builds from the Dockerfile.
4. Set **Variables** (from `.env.railway.example`):
   - `NEXUS_ENV=production`
   - `SERVE_FRONTEND=true`
   - `NEXUS_DEMO_KEY=<the key from step 1>`
   - `LLM_PROVIDER=openai`
   - `OPENAI_API_KEY=<groq key>`
   - `OPENAI_BASE_URL=https://api.groq.com/openai/v1`
   - `OPENAI_MODEL=llama-3.3-70b-versatile`
   - `QDRANT_URL=<your qdrant cloud url>`
   - `QDRANT_API_KEY=<your qdrant cloud key>`
5. Set the **build arg** `VITE_NEXUS_DEMO_KEY` = the SAME value as `NEXUS_DEMO_KEY`.
   (Railway: service → Settings → Build → Build Args. This bakes the key into the
   SPA so it can authenticate to the chat endpoint.)
6. Deploy. Railway assigns a public URL.

## Seed the catalog (one-time, after first deploy)

Qdrant starts empty. Run the seeder against your Cloud Qdrant once:
```
# locally, pointing at the cloud Qdrant:
QDRANT_URL=<cloud url> QDRANT_API_KEY=<cloud key> python3 -m catalog.seed
```

## Verify the live deploy

- `https://<app>.railway.app/health` → `{"status":"ok"}`
- `https://<app>.railway.app/` → the NEXUS SPA loads
- Open Ask Nexus, type a free-form query ("something tense and slow") →
  a real LLM response (NOT canned). If it's canned, `LLM_PROVIDER` is still mock.
- Say/type "watch Aftersun" → jumps to the open-confirmation flow.

## Gotchas (learned the hard way)

- **Auth on the chat endpoint:** `/api/v1/*` requires a key. The SPA sends
  `X-Nexus-Key` from `VITE_NEXUS_DEMO_KEY` (build-time). If the build arg is
  missing, every chat call 401s — and the title matcher still works (it's
  client-side), so the demo looks fine until someone types a real query.
- **Demo key must be stable:** the old code generated a random key per boot.
  `NEXUS_DEMO_KEY` pins it so it survives restarts.
- **Mock provider is a deal-killer live:** canned responses expose the demo the
  moment a prospect goes off-script. Always use the Groq path for buyer demos.
- **Free-tier sleep:** Railway free services sleep when idle; first request after
  sleep is slow. Warn the prospect, or hit the URL right before a call.
