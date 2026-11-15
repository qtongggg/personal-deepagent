from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    JEV_API_KEY: Optional[str] = None

    DEFAULT_MODEL: str = "gpt-4o"

    MEM0_API_KEY: Optional[str] = None

    CATALOG_CSV_PATH: str = "data/catalog.csv"
    CHROMA_PERSIST_DIR: str = ".chroma/"

    SIMILARITY_THRESHOLD: float = 0.4
    MAX_REFERENCES: int = 25


@lru_cache()
def get_settings() -> Settings:
    return Settings()
