from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    SECRET_KEY: str
    ADMIN_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    REDIS_URL: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings() 