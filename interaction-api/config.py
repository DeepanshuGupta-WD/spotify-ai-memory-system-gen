# """
# Central configuration for interaction-api.

# Reads from environment variables (see .env.example at project root).
# """
# from functools import lru_cache
# from pydantic_settings import BaseSettings



# class Settings(BaseSettings):
#     # --- API ---
#     api_title: str = "Spotify AI Memory - Interaction API"
#     api_version: str = "0.1.0"
#     debug: bool = True  # when True, enables dev-mode auth/consent bypasses for local testing

#     # --- Postgres (Raw Immutable Events) ---
#     postgres_dsn: str = "postgresql://postgres:postgres@localhost:5433/spotify_interactions"
#     postgres_pool_min_size: int = 1
#     postgres_pool_max_size: int = 10

#     # --- Auth ---
#     jwt_secret: str = "dev-secret-change-me"
#     jwt_algorithm: str = "HS256"
#     allow_dev_auth_header: bool = True  # if True + debug, accept `X-User-Id` header instead of a JWT

#     # --- Consent ---
#     consent_required_scopes: dict[str, list[str]] = {
#         "playback": ["memory_capture"],
#         "chat": ["memory_capture", "personalization"],
#         "ui_action": ["memory_capture"],
#     }
#     allow_dev_consent_bypass: bool = True  # if True + debug, treat every user as fully consented

#     # --- Event contract ---
#     current_event_schema_version: str = "1.0.0"
#     supported_event_schema_versions: list[str] = ["1.0.0"]

#     # --- Memory Decision Engine (inline placeholder until memory-decision-engine service exists) ---
#     importance_threshold: float = 0.5

#     # --- Graph integration (bridges into the sibling `graph` package) ---
#     # `graph` and `spotify_mcp` are sibling top-level folders under spotify-mem-sys/.
#     # For imports like `from graph.services...` to resolve, either:
#     #   1) run uvicorn from the spotify-mem-sys/ root, or
#     #   2) add spotify-mem-sys/ to PYTHONPATH, or
#     #   3) `pip install -e ../graph` if it exposes a setup.py/pyproject.toml
#     enable_graph_writeback: bool = True

#     class Config:
#         env_file = ".env"
#         env_prefix = "INTERACTION_API_"


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


# settings = get_settings()


"""
Central configuration for interaction-api.

Reads from environment variables (see .env.example at project root).
"""
from functools import lru_cache
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- API ---
    api_title: str = "Spotify AI Memory - Interaction API"
    api_version: str = "0.1.0"
    debug: bool = True  # Enables dev-mode auth/consent bypasses for local testing

    # --- Postgres (Raw Immutable Events) ---
    postgres_dsn: str = (
        "postgresql://postgres:postgres@localhost:5433/spotify_interactions"
    )
    postgres_pool_min_size: int = 1
    postgres_pool_max_size: int = 10

    # --- Auth ---
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    allow_dev_auth_header: bool = True

    # --- CORS ---
    # The Vue development server runs on port 5173. Keep this configurable so
    # deployed clients can be allow-listed without changing application code.
    cors_allowed_origins: list[str] =  [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
   "https://spotify-memory-frontend.onrender.com"
 
    
]
    cors_allowed_origin_regex: str = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"

    # --- Consent ---
    consent_required_scopes: dict[str, list[str]] = {
        "playback": ["memory_capture"],
        "chat": ["memory_capture", "personalization"],
        "ui_action": ["memory_capture"],
    }
    allow_dev_consent_bypass: bool = True

    # --- Event contract ---
    current_event_schema_version: str = "1.1.0"
    supported_event_schema_versions: list[str] = ["1.0.0", "1.1.0"]

    # --- Memory Decision Engine ---
    # A decision must reach this score before it becomes retrievable memory.
    # The same score is passed to the graph as memory importance and to the
    # recommendation workflow as a preference weight.
    memory_retention_threshold: float = 0.55

    # --- Graph integration ---
    # Neo4j configuration is handled by the existing `graph` package.
    # The Interaction API simply imports and uses that package.
    enable_graph_writeback: bool = True

    # --- Gemini chat understanding ---
    # Leave the key unset for deterministic local development.  The chat
    # service falls back safely, while production uses Gemini structured JSON.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="INTERACTION_API_",
        extra="ignore",  # Ignore unrelated env vars such as NEO4J_*
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
