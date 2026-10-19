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
        description="The prefix of every Redis-Key, that belongs to this App.",
    )
    SECRET_KEY: SecretStr = Field(
        min_length=32,
        frozen=True,
    )
    APP_PORT: int = Field(
        description="The port the uvicorn server uses to run the App.",
        default=7000,
        ge=7000,
        le=8000,
        validate_default=True,
    )


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


SETTINGS = Settings() # type: ignore