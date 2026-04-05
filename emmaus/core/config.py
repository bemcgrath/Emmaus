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

    model_config = SettingsConfigDict(
        env_prefix="EMMAUS_",
        env_file=".env",
        extra="ignore",
    )
