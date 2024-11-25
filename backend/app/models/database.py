from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse
from ..config import get_settings

settings = get_settings()

# Handle special characters in database password
parsed = urllib.parse.urlparse(settings.DATABASE_URL)
password = urllib.parse.quote(parsed.password, safe='')
db_url = parsed._replace(
    netloc=f"{parsed.username}:{password}@{parsed.hostname}:{parsed.port}"
).geturl()

# Create database engine with connection pooling settings
engine = create_engine(
    db_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for all database models
Base = declarative_base()