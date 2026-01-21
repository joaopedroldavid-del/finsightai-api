from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "Financial Agent API"
    environment: str = "development"
    debug: bool = True

    openai_api_key: Optional[str] = None
    default_agent: str = "financial_manager"

    news_api_key: Optional[str] = None

    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    api_prefix: str = "/api/v1"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )

settings = Settings()

if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
else:
    print("⚠️ OpenAI API key not found in settings")

if settings.news_api_key:
    os.environ["NEWS_API_KEY"] = settings.news_api_key
else:
    print("⚠️ NewsAPI key not found in settings")