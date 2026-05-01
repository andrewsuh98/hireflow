from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    db_path: Path = Path("data/tracker.db")
    google_credentials_path: Path = Path("credentials.json")
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
