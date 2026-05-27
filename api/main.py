"""
NEXUS API — FastAPI application entry point.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
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


@app.get("/", include_in_schema=False)
async def root():
    s = get_settings()
    from utils.licensing import get_license
    lic = get_license()
    return {"platform": "NEXUS", "version": "1.0.0", "env": s.nexus_env,
            "llm": s.llm_provider, "license": lic.tier, "docs": "/docs"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error("nexus.unhandled_error", path=str(request.url), error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
