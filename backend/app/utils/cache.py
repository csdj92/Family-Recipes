from functools import wraps
from fastapi import Request
import json
from ..dependencies import get_redis
import logging

logger = logging.getLogger(__name__)

def cache_response(expire_time_seconds: int = 300):
    """
    Cache decorator for FastAPI endpoint responses
    Args:
        expire_time_seconds: How long to cache the response (default 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from args
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                return await func(*args, **kwargs)

            # Generate cache key from path and query params
            cache_key = f"cache:{request.url.path}"
            if request.query_params:
                cache_key += f":{str(request.query_params)}"

            try:
                # Try to get cached response
                redis = await get_redis()
                cached_response = await redis.get(cache_key)
                if cached_response:
                    return json.loads(cached_response)

                # Generate new response
                response = await func(*args, **kwargs)

                # Cache the response
                await redis.set(
                    cache_key,
                    json.dumps(response),
                    ex=expire_time_seconds
                )
                return response

            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
                # If caching fails, just return the response
                return await func(*args, **kwargs)

        return wrapper
    return decorator 