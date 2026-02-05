from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTAuthConfig(BaseSettings):
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


jwt_auth_config = JWTAuthConfig()
