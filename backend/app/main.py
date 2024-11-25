from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routers import auth, recipes, groups
from .models import create_tables, User
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from .config import get_settings

settings = get_settings()

async def get_redis():
    return await aioredis.from_url(
        settings.REDIS_URL or "redis://localhost",
        encoding="utf8",
        decode_responses=True
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - Initialize FastAPILimiter with Redis
    try:
        redis = await get_redis()
        await FastAPILimiter.init(redis)
        yield
    except Exception as e:
        # Log the error but allow the application to start
        print(f"Warning: Rate limiting is disabled - {str(e)}")
        yield
    finally:
        # Cleanup
        if 'redis' in locals():
            await redis.close()

app = FastAPI(
    title="Recipe Sharing API",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "https://your-frontend-domain.com",
    "https://staging.your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
app.include_router(groups.router, prefix="/groups", tags=["Family Groups"])

# Add TrustedHost middleware after routers
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.yourdomain.com",
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Recipe Sharing API"}

@app.get("/health")
async def health_check():
    try:
        # Test Redis connection
        redis = await get_redis()
        await redis.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    finally:
        if 'redis' in locals():
            await redis.close()
            
    return {
        "status": "healthy",
        "version": "1.0.0",
        "redis": redis_status
    }

@app.get("/test-redis")
async def test_redis():
    try:
        redis = await get_redis()
        # Test setting a value
        await redis.set("test_key", "test_value", ex=60)
        # Test getting the value
        value = await redis.get("test_key")
        return {
            "status": "success",
            "test_value": value
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if 'redis' in locals():
            await redis.close()
