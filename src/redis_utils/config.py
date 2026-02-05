from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", extra="ignore"
    )

    @property
    def REDIS_URL(self):
        # redis://[[username]:password@]host[:port][/db-number]
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"


redis_config = RedisConfig()
