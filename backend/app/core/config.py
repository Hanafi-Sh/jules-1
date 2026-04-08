from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Aethera API"
    API_V1_STR: str = "/api/v1"
    DEEPSEEK_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
