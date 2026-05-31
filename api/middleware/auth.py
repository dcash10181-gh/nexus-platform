"""
Authentication middleware — API key + tenant isolation.

Every request to /v1/* must carry:
  Authorization: Bearer <api_key>
  OR
  X-Nexus-Key: <api_key>

API keys are hashed with BLAKE2b before storage. Plaintext never persists.

Key format:  nxk_<tier>_<random_32_hex>
Examples:
  nxk_trial_a3f9...       — 30-day trial key
  nxk_comm_b7d1...        — commercial license
  nxk_ent_c2e8...         — enterprise license

Tenant isolation is enforced here: every authenticated request carries
a `tenant_id` that downstream services use to scope Qdrant collections
and Neo4j databases.
"""
from __future__ import annotations

import hashlib
import logging
import secrets
import time
from dataclasses import dataclass, field
from typing import Literal

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import get_settings

log = logging.getLogger(__name__)

# ── Tier definitions ──────────────────────────────────────────────────────

@dataclass
class ApiKey:
    key_hash:    str
    tenant_id:   str
    tier:        Literal["trial", "commercial", "enterprise"]
    created_at:  float
    expires_at:  float | None       # None = perpetual (enterprise)
    user_cap:    int | None         # None = unlimited
    active_users: int = 0
    label:       str = ""


# ── In-memory key store (swap for Redis/Postgres in production) ───────────

_KEY_STORE: dict[str, ApiKey] = {}


def _hash_key(plaintext: str) -> str:
    return hashlib.blake2b(plaintext.encode(), digest_size=32).hexdigest()


def generate_key(
    tenant_id: str,
    tier: Literal["trial", "commercial", "enterprise"],
    label: str = "",
) -> tuple[str, ApiKey]:
    """Generate a new API key. Returns (plaintext, ApiKey). Store only ApiKey."""
    settings = get_settings()

    prefix_map = {"trial": "nxk_trial_", "commercial": "nxk_comm_", "enterprise": "nxk_ent_"}
    plaintext = prefix_map[tier] + secrets.token_hex(16)
    key_hash = _hash_key(plaintext)

    now = time.time()
    ttl = settings.trial_duration_days * 86400 if tier == "trial" else None
    cap = settings.trial_user_cap if tier == "trial" else None

    record = ApiKey(
        key_hash=key_hash,
        tenant_id=tenant_id,
        tier=tier,
        created_at=now,
        expires_at=now + ttl if ttl else None,
        user_cap=cap,
        label=label,
    )
    _KEY_STORE[key_hash] = record
    return plaintext, record


def _bootstrap_dev_key() -> None:
    """Seed API keys on startup.

    If NEXUS_DEMO_KEY is set, register it as a fixed, stable trial key — this
    is what the deployed demo and the frontend use, so it survives restarts and
    the in-memory store. Otherwise fall back to a random per-boot dev key.
    """
    import os

    demo_key = os.getenv("NEXUS_DEMO_KEY", "").strip()
    if demo_key:
        h = _hash_key(demo_key)
        if h not in _KEY_STORE:
            _KEY_STORE[h] = ApiKey(
                key_hash=h,
                tenant_id="demo-tenant",
                tier="trial",
                created_at=time.time(),
                expires_at=None,
                user_cap=None,
                label="public-demo",
            )
            log.info("NEXUS demo API key registered from NEXUS_DEMO_KEY")
        return

    if _KEY_STORE:
        return
    plaintext, _ = generate_key("dev-tenant", "trial", label="local-dev")
    log.warning(
        "NEXUS dev API key generated (trial): %s  "
        "— Set NEXUS_DEMO_KEY in the environment to use a fixed key",
        plaintext,
    )


def lookup_key(plaintext: str) -> ApiKey | None:
    return _KEY_STORE.get(_hash_key(plaintext))


def revoke_key(plaintext: str) -> bool:
    h = _hash_key(plaintext)
    return bool(_KEY_STORE.pop(h, None))


# ── FastAPI dependency ────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)


async def require_auth(request: Request) -> ApiKey:
    """
    FastAPI dependency — use with Depends(require_auth).
    Returns the validated ApiKey; raises 401/403 on failure.
    """
    # Extract key from header
    plaintext: str | None = None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        plaintext = auth_header.removeprefix("Bearer ").strip()

    if not plaintext:
        plaintext = request.headers.get("X-Nexus-Key", "").strip() or None

    # Allow env-configured bypass key for internal seeder / tests
    settings = get_settings()
    if not plaintext:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Pass Authorization: Bearer <key> or X-Nexus-Key: <key>",
        )

    record = lookup_key(plaintext)
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    # Expiry check
    if record.expires_at and time.time() > record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key expired. Renew at nexus.ai/pricing",
        )

    # User cap check (trial gate)
    if record.user_cap and record.active_users >= record.user_cap:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Trial user cap ({record.user_cap}) reached. Upgrade at nexus.ai/pricing",
        )

    # Attach tenant_id to request state so routers can read it
    request.state.tenant_id = record.tenant_id
    request.state.tier = record.tier
    return record


# ── Starlette middleware (for health/docs bypass) ─────────────────────────

# Exact paths that bypass auth entirely
UNPROTECTED_EXACT = {"/", "/health", "/openapi.json"}
# Path prefixes that bypass auth (docs UI has sub-paths like /docs/oauth2-redirect)
UNPROTECTED_PREFIX = ("/docs", "/redoc")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Lightweight path-level guard. Routes not under /v1/* pass through.
    Actual key validation happens in the Depends(require_auth) dependency.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Exact-match or known doc prefix — never require auth
        if path in UNPROTECTED_EXACT or any(path.startswith(p) for p in UNPROTECTED_PREFIX):
            return await call_next(request)

        # /v1/* (including /api/v1/*) — check header exists (full validation in dependency)
        if "/v1/" in path:
            has_key = (
                request.headers.get("Authorization", "").startswith("Bearer ")
                or request.headers.get("X-Nexus-Key")
            )
            if not has_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing API key. See /docs for authentication."},
                )

        return await call_next(request)
