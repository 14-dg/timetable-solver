from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_CLIENT_URL: str = Field(
        default="redis://localhost:6379/0"
    )

    REDIS_QUEUE_URL: str = Field(
        default="redis://localhost:6379/1"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


SETTINGS = Settings()