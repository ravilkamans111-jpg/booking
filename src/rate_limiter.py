from redis.asyncio import Redis

from time import time
import random
from typing import Annotated
from fastapi.params import Depends
from fastapi import Request, HTTPException, status
from functools import lru_cache


@lru_cache
def get_redis():
    return Redis(host="localhost", port=6379)


class RateLimiter:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def is_limited(self, ip_address, endpoint, max_request, window_seconds):
        key = f"rate_limiter:{endpoint}:{ip_address}"
        current_ms = time() * 1000
        window_start = current_ms - window_seconds * 1000
        current_request = f"{time() * 1000} - {random.randint(0, 100000)}"

        async with self._redis.pipeline(transaction=True) as pipe:
            await pipe.zremrangebyscore(key, 0, window_start)

            await pipe.zcard(key)

            await pipe.zadd(key, {current_request: current_ms})

            await pipe.expire(key, window_seconds)

            res = await pipe.execute()
        _, current_count, _, _ = res

        return current_count >= max_request


@lru_cache
def get_rate_limiter():
    return RateLimiter(get_redis())


def rate_limiter_factory(endpoint, max_request, window_seconds):
    async def dependency(
        request: Request,
        rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    ):
        ip_address = request.client.host

        limited = await rate_limiter.is_limited(
            ip_address, endpoint, max_request, window_seconds
        )

        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Будешь спамить мы тебе рот порвем",
            )

    return dependency


rate_limit_get_user_info = rate_limiter_factory("all-hotels", 5, 5)
