from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0"
    )
    REDIS_QUEUE_URL: str = Field(
        default="redis://localhost:6379/1"
    )
    REDIS_KEY_PREFIX: str = Field(
        default="solver",
        description="Das prefix jedes Redis-Keys, der zu dieser Anwendung gehört.",
    )
    SECRET_KEY: SecretStr = Field(
        min_length=32,
        frozen=True,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


SETTINGS = Settings() # type: ignore