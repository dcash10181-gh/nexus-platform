"""
Tenant management — namespace isolation for multi-tenant deployments.

Each licensed tenant gets:
  - Isolated Qdrant collections:  {tenant_id}_content, {tenant_id}_users
  - Isolated Neo4j database:      nexus_{tenant_id}  (Community Edition uses labels)
  - Scoped API keys
  - Independent catalog + user data

The tenant_id flows through the request via request.state.tenant_id,
set by the auth middleware on every authenticated call.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Literal


_TENANT_STORE: dict[str, "Tenant"] = {}

TENANT_ID_RE = re.compile(r"^[a-z0-9_-]{3,40}$")


@dataclass
class Tenant:
    id:          str
    name:        str
    tier:        Literal["trial", "commercial", "enterprise"]
    created_at:  float = field(default_factory=time.time)
    catalog_size: int = 0
    user_count:  int = 0
    config:      dict = field(default_factory=dict)

    # Derived namespace helpers
    @property
    def qdrant_content_collection(self) -> str:
        return f"{self.id}_content"

    @property
    def qdrant_users_collection(self) -> str:
        return f"{self.id}_users"

    @property
    def neo4j_label_prefix(self) -> str:
        """Neo4j Community doesn't support multiple databases; we use label namespacing."""
        return self.id.upper().replace("-", "_")


def register_tenant(
    tenant_id: str,
    name: str,
    tier: Literal["trial", "commercial", "enterprise"] = "trial",
    config: dict | None = None,
) -> Tenant:
    if not TENANT_ID_RE.match(tenant_id):
        raise ValueError(f"tenant_id must match {TENANT_ID_RE.pattern!r}")
    if tenant_id in _TENANT_STORE:
        return _TENANT_STORE[tenant_id]

    t = Tenant(id=tenant_id, name=name, tier=tier, config=config or {})
    _TENANT_STORE[tenant_id] = t

    # Always ensure dev-tenant exists
    if "dev-tenant" not in _TENANT_STORE:
        _TENANT_STORE["dev-tenant"] = Tenant(
            id="dev-tenant", name="Local Development", tier="trial"
        )

    return t


def get_tenant(tenant_id: str) -> Tenant | None:
    return _TENANT_STORE.get(tenant_id)


def get_or_create_tenant(tenant_id: str) -> Tenant:
    if tenant_id not in _TENANT_STORE:
        register_tenant(tenant_id, name=tenant_id.replace("-", " ").title())
    return _TENANT_STORE[tenant_id]


def list_tenants() -> list[Tenant]:
    return list(_TENANT_STORE.values())


# Bootstrap the dev tenant on import
register_tenant("dev-tenant", "Local Development", tier="trial")
