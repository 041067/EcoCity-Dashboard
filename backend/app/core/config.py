from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: Optional[str] = None
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
