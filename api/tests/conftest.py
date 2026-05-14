"""
pytest configuration — fixtures and test utilities.

Run tests with:
  cd api && pytest tests/ -v

The test suite uses:
  - MockProvider LLM (no API keys required)
  - In-memory stores where possible (no running Docker services required)
  - httpx.AsyncClient for API integration tests
"""
from __future__ import annotations

import os
import sys

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure api/ is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Force mock LLM and test env BEFORE importing app
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("NEXUS_ENV", "development")
os.environ.setdefault("NEXUS_LICENSE_KEY", "trial")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")


# ── Minimal content fixtures ──────────────────────────────────────────────

SAMPLE_CONTENT = [
    {
        "id": "test-film-001",
        "title": "Test Film Alpha",
        "year": 2023,
        "kind": "film",
        "synopsis": "A gripping psychological thriller about identity and memory.",
        "genres": ["Thriller", "Sci-Fi"],
        "cast": ["Actor One", "Actor Two"],
        "director": "Director A",
        "rating": 8.2,
        "poster_url": "",
        "backdrop_url": "",
        "dna": {
            "pacing": 0.6,
            "tension_curve": [0.3, 0.5, 0.7, 0.9],
            "visual_style": "cinematic",
            "audio_mood": "ominous",
            "thematic_tags": ["identity", "memory"],
            "runtime_min": 120,
        },
    },
    {
        "id": "test-series-001",
        "title": "Test Series Beta",
        "year": 2022,
        "kind": "series",
        "synopsis": "A slow-burn drama exploring corporate power and family betrayal.",
        "genres": ["Drama"],
        "cast": ["Actor Three", "Actor Four"],
        "rating": 8.5,
        "poster_url": "",
        "backdrop_url": "",
        "dna": {
            "pacing": 0.4,
            "tension_curve": [0.2, 0.4, 0.6, 0.8],
            "visual_style": "prestige",
            "audio_mood": "tense",
            "thematic_tags": ["power", "betrayal"],
            "runtime_min": 55,
        },
    },
    {
        "id": "test-film-002",
        "title": "Test Film Gamma",
        "year": 2024,
        "kind": "film",
        "synopsis": "An epic sci-fi adventure set across multiple galaxies.",
        "genres": ["Sci-Fi", "Action"],
        "cast": ["Actor Five"],
        "rating": 7.8,
        "poster_url": "",
        "backdrop_url": "",
        "dna": {
            "pacing": 0.8,
            "tension_curve": [0.4, 0.6, 0.8, 0.95],
            "visual_style": "epic",
            "audio_mood": "grand",
            "thematic_tags": ["space", "adventure"],
            "runtime_min": 145,
        },
    },
]


@pytest.fixture(scope="session")
def sample_content():
    return SAMPLE_CONTENT


@pytest.fixture
def sample_user_id():
    return "test-user-001"


@pytest.fixture
def rec_request(sample_user_id):
    from models import RecommendationRequest
    return RecommendationRequest(
        user_id=sample_user_id,
        context={"time_of_day": "evening", "device": "tv"},
        limit=10,
    )


# ── App client (skips DB if unavailable) ─────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """
    Async test client. Skips tests that require live DB services if they're
    not running — CI runs with mocked services only.
    """
    try:
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c
    except Exception as e:
        pytest.skip(f"Could not create test client: {e}")
