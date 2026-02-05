from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleAuthConfig(BaseSettings):
    CLIENT_SECRET: str
    CLIENT_ID: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_AUTH_FORM_BASE_URL: str
    REDIRECT_URI: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore"
    )


google_auth_config = GoogleAuthConfig()
