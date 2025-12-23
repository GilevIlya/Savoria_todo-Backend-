from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class DataBaseConfig(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env'
    )

    @property
    def DATABASE_url_asyncpg(self):
        # DSN
        # postgresql+asyncpg://postgres:password@localhost:5432/mydb
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@postgres:5432/{self.POSTGRES_DB}"


data_base_config = DataBaseConfig()