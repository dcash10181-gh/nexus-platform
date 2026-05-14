"""
License enforcement — validates NEXUS_LICENSE_KEY and enforces tier limits.

Tiers:
  trial       — 30 days, 1,000 users, watermarked UI
  commercial  — annual, unlimited users, 5 tenants, no source
  enterprise  — perpetual, unlimited tenants, source escrow

The license key is validated against a signed payload. In production this
would call a licensing server; here it decodes a self-contained signed token
so the platform can validate offline (important for air-gapped deployments).
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from config import get_settings

log = logging.getLogger(__name__)

NEXUS_SIGNING_SECRET = "nexus-platform-license-signing-key-v1"

@dataclass
class LicenseInfo:
    tier:        Literal["trial", "commercial", "enterprise"]
    tenant_cap:  int        # max simultaneous tenants
    user_cap:    int | None # None = unlimited
    expires_at:  float | None
    licensee:    str
    valid:       bool
    reason:      str = ""

    @property
    def is_trial(self) -> bool:
        return self.tier == "trial"

    @property
    def ui_watermark(self) -> bool:
        return self.tier == "trial"


def _sign(payload: str) -> str:
    return hashlib.blake2b(
        (payload + NEXUS_SIGNING_SECRET).encode(), digest_size=16
    ).hexdigest()


def encode_license(
    tier: str,
    licensee: str,
    tenant_cap: int,
    user_cap: int | None,
    duration_days: int | None,
) -> str:
    """Generate a license key string (used by the licensing server)."""
    now = time.time()
    payload = {
        "tier": tier,
        "licensee": licensee,
        "tenant_cap": tenant_cap,
        "user_cap": user_cap,
        "issued_at": now,
        "expires_at": now + duration_days * 86400 if duration_days else None,
    }
    raw = json.dumps(payload, separators=(",", ":"))
    b64 = base64.urlsafe_b64encode(raw.encode()).decode()
    sig = _sign(raw)
    return f"nxl_{b64}_{sig}"


def decode_license(key: str) -> LicenseInfo:
    """Decode and verify a license key. Returns LicenseInfo(valid=False) on failure."""
    settings = get_settings()

    # Trial fallback
    if key in ("trial", "", None):
        now = time.time()
        return LicenseInfo(
            tier="trial",
            tenant_cap=1,
            user_cap=settings.trial_user_cap,
            expires_at=now + settings.trial_duration_days * 86400,
            licensee="Trial",
            valid=True,
            reason="Trial mode: 30 days, 1,000 users",
        )

    try:
        parts = key.split("_", 2)  # nxl_{b64}_{sig}
        if len(parts) != 3 or parts[0] != "nxl":
            raise ValueError("Bad format")

        raw = base64.urlsafe_b64decode(parts[1].encode()).decode()
        expected_sig = _sign(raw)
        if not hmac_compare(expected_sig, parts[2]):
            raise ValueError("Invalid signature")

        payload = json.loads(raw)
        expires = payload.get("expires_at")

        if expires and time.time() > expires:
            return LicenseInfo(
                tier=payload["tier"], tenant_cap=0, user_cap=0,
                expires_at=expires, licensee=payload["licensee"],
                valid=False, reason="License expired",
            )

        return LicenseInfo(
            tier=payload["tier"],
            tenant_cap=payload["tenant_cap"],
            user_cap=payload.get("user_cap"),
            expires_at=expires,
            licensee=payload["licensee"],
            valid=True,
        )
    except Exception as e:
        log.error("License decode failed: %s", e)
        return LicenseInfo(
            tier="trial", tenant_cap=0, user_cap=0,
            expires_at=None, licensee="Unknown",
            valid=False, reason=f"Invalid license key: {e}",
        )


def hmac_compare(a: str, b: str) -> bool:
    """Constant-time string comparison."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0


@lru_cache
def get_license() -> LicenseInfo:
    settings = get_settings()
    info = decode_license(settings.nexus_license_key)
    log.info(
        "License: tier=%s licensee=%s valid=%s reason=%s",
        info.tier, info.licensee, info.valid, info.reason,
    )
    return info


def enforce_license() -> LicenseInfo:
    """Call on startup. Raises if license is invalid."""
    info = get_license()
    if not info.valid:
        raise RuntimeError(f"NEXUS license invalid: {info.reason}. Visit nexus.ai/pricing")
    return info
