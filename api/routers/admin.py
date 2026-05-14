"""
Admin router — tenant management, API key issuance, and platform stats.
All admin endpoints additionally require the X-Nexus-Admin header.

POST /v1/admin/keys/generate      — Issue a new API key for a tenant
GET  /v1/admin/tenants            — List all tenants
GET  /v1/admin/tenants/{id}/stats — Catalog + user counts for a tenant
GET  /v1/admin/license            — Current license info
GET  /v1/admin/health/deep        — Deep health: all services
"""
from __future__ import annotations

import time
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from typing import Literal

from middleware.auth import require_auth, generate_key, ApiKey
from utils.tenants import register_tenant, list_tenants, get_tenant
from utils.licensing import get_license
from config import get_settings

log = logging.getLogger(__name__)
router = APIRouter()


# ── Admin auth guard ──────────────────────────────────────────────────────

ADMIN_SECRET_HEADER = "X-Nexus-Admin"

def _require_admin(request: Request) -> None:
    settings = get_settings()
    secret = request.headers.get(ADMIN_SECRET_HEADER, "")
    admin_secret = getattr(settings, "nexus_admin_secret", "nexus-admin-dev")
    if secret != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access requires X-Nexus-Admin header",
        )


# ── API Key issuance ──────────────────────────────────────────────────────

class KeyGenRequest(BaseModel):
    tenant_id: str
    tier: Literal["trial", "commercial", "enterprise"] = "trial"
    label: str = ""


class KeyGenResponse(BaseModel):
    api_key: str
    tenant_id: str
    tier: str
    warning: str = ""


@router.post("/keys/generate", response_model=KeyGenResponse)
async def generate_api_key(req: KeyGenRequest, request: Request):
    """
    Issue a new API key for a tenant.
    The plaintext key is returned ONCE — store it securely.
    """
    _require_admin(request)
    license_info = get_license()

    # Enforce tenant cap
    tenants = list_tenants()
    non_dev_tenants = [t for t in tenants if t.id != "dev-tenant"]
    if len(non_dev_tenants) >= license_info.tenant_cap:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant cap ({license_info.tenant_cap}) reached for license tier '{license_info.tier}'. "
                   f"Upgrade at nexus.ai/pricing",
        )

    register_tenant(req.tenant_id, req.tenant_id.replace("-", " ").title(), tier=req.tier)
    plaintext, record = generate_key(req.tenant_id, req.tier, label=req.label)

    warning = ""
    if license_info.is_trial:
        warning = "Trial mode: key expires in 30 days and is capped at 1,000 users."

    log.info("API key issued: tenant=%s tier=%s", req.tenant_id, req.tier)
    return KeyGenResponse(
        api_key=plaintext,
        tenant_id=req.tenant_id,
        tier=req.tier,
        warning=warning,
    )


# ── Tenant listing ────────────────────────────────────────────────────────

@router.get("/tenants")
async def list_all_tenants(request: Request):
    _require_admin(request)
    return {
        "tenants": [
            {
                "id": t.id,
                "name": t.name,
                "tier": t.tier,
                "catalog_size": t.catalog_size,
                "user_count": t.user_count,
            }
            for t in list_tenants()
        ]
    }


@router.get("/tenants/{tenant_id}/stats")
async def tenant_stats(tenant_id: str, request: Request):
    _require_admin(request)
    t = get_tenant(tenant_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    # Pull live counts from services
    try:
        from catalog.vector_store import get_vector_store
        vs = get_vector_store()
        # Override collection name with tenant namespace
        vs._client._prefix = t.qdrant_content_collection
        vector_count = await vs.count()
    except Exception:
        vector_count = -1

    return {
        "tenant_id": t.id,
        "name": t.name,
        "tier": t.tier,
        "catalog_vectors": vector_count,
        "user_count": t.user_count,
        "qdrant_collections": {
            "content": t.qdrant_content_collection,
            "users": t.qdrant_users_collection,
        },
        "neo4j_label_prefix": t.neo4j_label_prefix,
    }


# ── License info ──────────────────────────────────────────────────────────

@router.get("/license")
async def license_info(request: Request):
    _require_admin(request)
    info = get_license()
    return {
        "tier":        info.tier,
        "licensee":    info.licensee,
        "valid":       info.valid,
        "tenant_cap":  info.tenant_cap,
        "user_cap":    info.user_cap,
        "expires_at":  info.expires_at,
        "ui_watermark": info.ui_watermark,
        "reason":      info.reason,
    }


# ── Deep health ───────────────────────────────────────────────────────────

@router.get("/health/deep")
async def deep_health():
    """Service-by-service health check. Does not require admin — safe to expose."""
    results = {}
    t0 = time.monotonic()

    try:
        from catalog.vector_store import get_vector_store
        vs = get_vector_store()
        count = await vs.count()
        results["qdrant"] = {"status": "ok", "vectors": count}
    except Exception as e:
        results["qdrant"] = {"status": "error", "detail": str(e)}

    try:
        from catalog.graph import get_graph
        g = get_graph()
        stats = await g.graph_stats()
        results["neo4j"] = {"status": "ok", **stats}
    except Exception as e:
        results["neo4j"] = {"status": "error", "detail": str(e)}

    try:
        from llm.orchestrator import get_orchestrator
        orch = get_orchestrator()
        results["llm"] = {"status": "ok", "provider": orch.provider_name}
    except Exception as e:
        results["llm"] = {"status": "error", "detail": str(e)}

    results["latency_ms"] = int((time.monotonic() - t0) * 1000)
    results["overall"] = "ok" if all(
        v.get("status") == "ok" for v in results.values() if isinstance(v, dict)
    ) else "degraded"

    return results
