"""
NEXUS API — FastAPI application entry point.
"""
from __future__ import annotations

import logging
import os as _os
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from catalog.vector_store import get_vector_store
from catalog.graph import get_graph
from middleware.auth import AuthMiddleware, _bootstrap_dev_key
from utils.licensing import enforce_license
from routers import recommendations, search, conversations, users, content, agents
from routers import admin
from routers import live as live_router
from routers.federated import router as federated_router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    log.info("nexus.startup", env=settings.nexus_env, llm=settings.llm_provider)

    enforce_license()
    _bootstrap_dev_key()

    # Vector store — warn but don't crash
    try:
        vs = get_vector_store()
        await vs.ensure_collection()
        log.info("nexus.vector_store.ready")
    except Exception as e:
        log.warning("nexus.vector_store.unavailable", error=str(e))

    # Knowledge graph — warn but don't crash
    # Neo4j takes 60-90s on first boot; API retries per-request
    try:
        g = get_graph()
        await g.ensure_schema()
        log.info("nexus.graph.ready")
    except Exception as e:
        log.warning("nexus.graph.unavailable", error=str(e))

    yield

    log.info("nexus.shutdown")
    try:
        await get_graph().close()
    except Exception:
        pass


app = FastAPI(
    title="NEXUS Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(recommendations.router, prefix="/v1/recommendations", tags=["Recommendations"])
app.include_router(search.router,          prefix="/v1/search",          tags=["Search"])
app.include_router(conversations.router,   prefix="/v1/conversations",   tags=["Conversational AI"])
app.include_router(users.router,           prefix="/v1/users",           tags=["Users"])
app.include_router(content.router,         prefix="/v1/content",         tags=["Content"])
app.include_router(agents.router,          prefix="/v1/agents",          tags=["Agents"])
app.include_router(admin.router,           prefix="/v1/admin",           tags=["Admin"])
app.include_router(live_router.router,     prefix="/v1/live",            tags=["Live AI"])
app.include_router(federated_router,       prefix="/v1/federated",       tags=["Federated"])


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok", "ts": int(time.time())}


@app.get("/api-info", include_in_schema=False)
async def api_info():
    s = get_settings()
    from utils.licensing import get_license
    lic = get_license()
    return {"platform": "NEXUS", "version": "1.0.0", "env": s.nexus_env,
            "llm": s.llm_provider, "license": lic.tier, "docs": "/docs"}


# Serve the platform JSON at "/" only when NOT serving the frontend SPA there.
if _os.getenv("SERVE_FRONTEND", "").lower() not in ("1", "true", "yes"):
    @app.get("/", include_in_schema=False)
    async def root():
        return await api_info()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error("nexus.unhandled_error", path=str(request.url), error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Single-service deploy (Railway): serve the built SPA + alias API under /api ──
# Frontend ships in the same container and calls "/api/v1/...". We register the
# same routers under /api/v1 and serve the static SPA for everything else.
# Toggled by SERVE_FRONTEND so local Docker Compose (separate nginx) is unaffected.
if _os.getenv("SERVE_FRONTEND", "").lower() in ("1", "true", "yes"):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    for _r, _p, _t in (
        (recommendations.router, "/api/v1/recommendations", "Recommendations"),
        (search.router, "/api/v1/search", "Search"),
        (conversations.router, "/api/v1/conversations", "Conversational AI"),
        (users.router, "/api/v1/users", "Users"),
        (content.router, "/api/v1/content", "Content"),
        (agents.router, "/api/v1/agents", "Agents"),
        (admin.router, "/api/v1/admin", "Admin"),
        (live_router.router, "/api/v1/live", "Live AI"),
    ):
        app.include_router(_r, prefix=_p, tags=[_t])
    app.include_router(federated_router, prefix="/api/v1/federated", tags=["Federated"])

    _frontend_dist = _os.getenv("FRONTEND_DIST", "/app/static")
    if _os.path.isdir(_os.path.join(_frontend_dist, "assets")):
        app.mount(
            "/assets",
            StaticFiles(directory=_os.path.join(_frontend_dist, "assets")),
            name="assets",
        )

    # Catch-all SPA fallback — MUST be the last route registered.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith(
            ("api/", "v1/", "docs", "redoc", "openapi.json", "health", "api-info", "assets/")
        ):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = _os.path.join(_frontend_dist, full_path)
        if full_path and _os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(_os.path.join(_frontend_dist, "index.html"))
