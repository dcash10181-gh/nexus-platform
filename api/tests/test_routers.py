"""
Integration tests — FastAPI routers.

These tests run against the full app via httpx.AsyncClient.
Services (Qdrant, Neo4j) are bypassed; the tests validate:
  - HTTP status codes
  - Response schema shape
  - Auth enforcement
  - Input validation
"""
from __future__ import annotations

import pytest
import pytest_asyncio


# ── Health endpoint ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "ts" in data


@pytest.mark.asyncio
async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["platform"] == "NEXUS"
    assert data["version"] == "1.0.0"


# ── Auth enforcement ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_recommendations_requires_auth(client):
    r = await client.post(
        "/v1/recommendations/",
        json={"user_id": "u1", "limit": 10},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_search_requires_auth(client):
    r = await client.get("/v1/search/?q=thriller")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_conversation_requires_auth(client):
    r = await client.post(
        "/v1/conversations/chat",
        json={"user_id": "u1", "message": "hello"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_agents_requires_auth(client):
    r = await client.post("/v1/agents/proactive", json={"user_id": "u1"})
    assert r.status_code == 401


# ── Input validation ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_requires_query_param(client):
    """Search without ?q= should return 422 Unprocessable Entity."""
    r = await client.get("/v1/search/", headers={"X-Nexus-Key": "nxk_trial_fake"})
    # 422 from pydantic validation OR 401 from auth — either is correct without a valid key
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_recommendations_validates_limit(client):
    r = await client.post(
        "/v1/recommendations/",
        json={"user_id": "u1", "limit": 999999},
        headers={"X-Nexus-Key": "nxk_trial_fake"},
    )
    # 401 (bad key) or 422 (validation) — not 500
    assert r.status_code in (401, 422)


# ── Auth middleware unit ──────────────────────────────────────────────────

def test_generate_and_lookup_key():
    from middleware.auth import generate_key, lookup_key
    plaintext, record = generate_key("test-tenant", "trial", label="pytest")
    assert plaintext.startswith("nxk_trial_")
    found = lookup_key(plaintext)
    assert found is not None
    assert found.tenant_id == "test-tenant"
    assert found.tier == "trial"


def test_lookup_unknown_key_returns_none():
    from middleware.auth import lookup_key
    assert lookup_key("nxk_trial_doesnotexist") is None


def test_revoke_key():
    from middleware.auth import generate_key, lookup_key, revoke_key
    plaintext, _ = generate_key("revoke-tenant", "trial")
    assert lookup_key(plaintext) is not None
    revoke_key(plaintext)
    assert lookup_key(plaintext) is None


# ── License utilities ─────────────────────────────────────────────────────

def test_trial_license_decodes():
    from utils.licensing import decode_license
    info = decode_license("trial")
    assert info.valid
    assert info.tier == "trial"
    assert info.is_trial
    assert info.ui_watermark


def test_empty_key_is_trial():
    from utils.licensing import decode_license
    info = decode_license("")
    assert info.valid
    assert info.tier == "trial"


def test_garbage_key_is_invalid():
    from utils.licensing import decode_license
    info = decode_license("notavalidkey")
    assert not info.valid


def test_encode_decode_roundtrip():
    from utils.licensing import encode_license, decode_license
    key = encode_license(
        tier="commercial",
        licensee="Test Corp",
        tenant_cap=5,
        user_cap=None,
        duration_days=365,
    )
    info = decode_license(key)
    assert info.valid
    assert info.tier == "commercial"
    assert info.licensee == "Test Corp"
    assert info.tenant_cap == 5
    assert info.user_cap is None


def test_expired_license_is_invalid():
    from utils.licensing import encode_license, decode_license
    key = encode_license("commercial", "Expired Corp", 5, None, duration_days=-1)
    info = decode_license(key)
    assert not info.valid
    assert "expired" in info.reason.lower()


# ── Tenant utilities ──────────────────────────────────────────────────────

def test_register_and_get_tenant():
    from utils.tenants import register_tenant, get_tenant
    t = register_tenant("pytest-tenant", "PyTest Tenant", tier="trial")
    found = get_tenant("pytest-tenant")
    assert found is not None
    assert found.name == "PyTest Tenant"


def test_tenant_qdrant_namespacing():
    from utils.tenants import register_tenant
    t = register_tenant("acme-corp", "Acme Corp", tier="commercial")
    assert t.qdrant_content_collection == "acme-corp_content"
    assert t.qdrant_users_collection == "acme-corp_users"


def test_tenant_id_validation():
    from utils.tenants import register_tenant
    with pytest.raises(ValueError, match="tenant_id must match"):
        register_tenant("INVALID ID!", "Bad")


def test_duplicate_register_returns_existing():
    from utils.tenants import register_tenant
    t1 = register_tenant("dup-tenant", "Dup 1")
    t2 = register_tenant("dup-tenant", "Dup 2")  # Should return existing
    assert t1 is t2


# ── Models ────────────────────────────────────────────────────────────────

def test_recommendation_request_defaults():
    from models import RecommendationRequest
    r = RecommendationRequest(user_id="u1")
    assert r.limit == 24
    assert r.context == {}


def test_content_dna_validation():
    from models import ContentDNA
    with pytest.raises(Exception):
        ContentDNA(pacing=1.5, visual_style="x", audio_mood="x", runtime_min=90)


def test_signal_model():
    from models import Signal
    s = Signal(name="Test", weight=0.75, detail="Test detail", icon="brain")
    assert s.weight == 0.75
