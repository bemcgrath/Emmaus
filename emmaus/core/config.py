from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Emmaus API"
    data_dir: Path = Field(default=Path("data"))
    database_path: Path = Field(default=Path("data/emmaus.sqlite3"))
    default_text_source: str = "sample_local"
    default_commentary_source: str = "notes_placeholder"
    study_history_limit: int = 30
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "phi3.5"
    ollama_connect_timeout_seconds: float = 0.25
    ollama_request_timeout_seconds: float = 20.0
    esv_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="EMMAUS_",
        env_file=".env",
        extra="ignore",
    )
