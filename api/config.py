"""
Configuration — single source of truth for runtime settings.
Reads from environment variables, validates types, exposes a singleton.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    nexus_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # Vector store (Qdrant)
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""           # Required for Qdrant Cloud; empty for local
    qdrant_collection: str = "nexus_content"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Knowledge graph (Neo4j)
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "nexus-dev-password"

    # LLM orchestration
    llm_provider: Literal["anthropic", "openai", "local", "azure", "mock"] = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = ""           # set for OpenAI-compatible providers (e.g. Groq)
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.1:8b"

    # Licensing
    nexus_license_key: str = "trial"
    trial_user_cap: int = 1000
    trial_duration_days: int = 30

    # Recommendation engine
    rec_candidate_pool_size: int = 200
    rec_final_count: int = 24
    rec_diversity_weight: float = 0.3
    rec_recency_weight: float = 0.15

    # Signals & explainability
    enable_explainability: bool = True
    enable_proactive_agent: bool = True

    # TMDB integration (optional — enables real poster/metadata enrichment)
    tmdb_api_key: str = ""

    # Admin API secret (change in production)
    nexus_admin_secret: str = "nexus-admin-dev"

    # Demo mode — pre-loads a demo user profile for live demo deployments
    demo_mode: bool = False
    demo_user_id: str = "demo-user-nexus"

    @property
    def llm_configured(self) -> bool:
        """True if the active provider has the credentials it needs."""
        match self.llm_provider:
            case "anthropic": return bool(self.anthropic_api_key)
            case "openai":    return bool(self.openai_api_key)
            case "local":     return True
            case "mock":      return True
            case _:           return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
