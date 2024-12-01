from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings
from redis import asyncio as aioredis
import urllib.parse

settings = get_settings()

# Parse database URL to handle special characters in password
parsed = urllib.parse.urlparse(settings.DATABASE_URL)
password = urllib.parse.quote(parsed.password, safe='')
db_url = parsed._replace(
    netloc=f"{parsed.username}:{password}@{parsed.hostname}:{parsed.port}"
).geturl()

# Create database engine
engine = create_engine(
    db_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_redis():
    """Get Redis connection"""
    redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    return redis

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 