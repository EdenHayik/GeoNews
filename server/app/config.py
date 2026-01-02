"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./geonews.db"
    
    # Database retention (days)
    data_retention_days: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Frontend URL for CORS
    frontend_url: str = "http://localhost:5173"
    
    # Scraping intervals (seconds)
    rss_scrape_interval: int = 300  # 5 minutes
    
    # CORS origins
    @property
    def cors_origins(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            self.frontend_url
        ]
        # Remove duplicates
        return list(set(origins))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env for backward compatibility


@lru_cache()
def get_settings() -> Settings:
    return Settings()

