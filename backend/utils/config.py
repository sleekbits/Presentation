from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_token: str = "change-me"
    temp_dir: Path = Path("/tmp/pptx-jobs")
    max_upload_mb: int = 20
    file_ttl_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
settings.temp_dir.mkdir(parents=True, exist_ok=True)
