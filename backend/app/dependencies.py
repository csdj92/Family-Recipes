from .models.database import SessionLocal
from redis import asyncio as aioredis
from .config import get_settings

settings = get_settings()

async def get_redis():
    """Get Redis connection"""
    redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    return redis

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 