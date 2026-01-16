from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_env: str = Field(default="dev", alias="APP_ENV")

    # Postgres
    postgres_dsn: str = Field(default="postgresql://postgres:postgres@localhost:5432/rag", alias="POSTGRES_DSN")

    # Retrieval defaults
    default_top_k: int = Field(default=8, alias="DEFAULT_TOP_K")
    vector_top_k: int = Field(default=12, alias="VECTOR_TOP_K")
    bm25_top_k: int = Field(default=12, alias="BM25_TOP_K")

    # Embeddings / LLM (via LangChain)
    embeddings_provider: str = Field(default="openai", alias="EMBEDDINGS_PROVIDER")
    embeddings_model: str = Field(default="text-embedding-3-small", alias="EMBEDDINGS_MODEL")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")

    # Self-check thresholds
    min_evidence_items: int = Field(default=3, alias="MIN_EVIDENCE_ITEMS")
    min_max_score: float = Field(default=0.35, alias="MIN_MAX_SCORE")

    # Optional
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
