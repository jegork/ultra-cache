from typing import TypeVar
from ultra_cache.storage.base import BaseStorage
from redis import asyncio as redis

K = TypeVar("K")
V = TypeVar("V")


class RedisStorage(BaseStorage):
    def __init__(self, redis: redis.Redis, prefix: str = "ultra-cache"):
        self.redis = redis
        self.prefix = prefix

    @classmethod
    def from_url(
        cls, connection_string: str, prefix: str = "ultra-cache"
    ) -> "RedisStorage":
        return cls(redis=redis.from_url(connection_string), prefix=prefix)

    async def save(self, key: K, value: V, ttl: int | float | None = None) -> None:
        full_key = f"{self.prefix}:{key}"
        await self.redis.set(full_key, value, ex=ttl)

    async def get(self, key: K) -> V | None:
        full_key = f"{self.prefix}:{key}"
        value = await self.redis.get(full_key)
        return value

    async def clear(self) -> None:
        keys = await self.redis.keys(f"{self.prefix}:*")
        if keys:
            await self.redis.delete(*keys)
