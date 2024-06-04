from ultra_cache.storage.base import BaseStorage
from datetime import datetime, timedelta, UTC


class InMemoryStorageItem[T]:
    def __init__(self, data: T, ttl: float | None) -> None:
        self._data = data
        self._ttl = ttl
        self._start = datetime.now(UTC)

    def __str__(self) -> str:
        return f"InMemoryStorageItem(date={self._data}, expired={self.expired})"

    @property
    def expired(self) -> bool:
        if self._ttl is None:
            return False

        return (datetime.now(UTC) - self._start) > timedelta(seconds=self._ttl)

    @property
    def value(self) -> T | None:
        if self.expired:
            return None

        return self._data


class InMemoryStorage[K, V](BaseStorage):
    def __init__(self) -> None:
        self.storage: dict[K, InMemoryStorageItem[V]] = {}

    async def save(self, key: K, value: V, ttl: int | float | None = None) -> None:
        self.storage[key] = InMemoryStorageItem(value, ttl)

    async def get(self, key: K) -> V | None:
        item = self.storage.get(key, None)

        if item is None:
            return None

        return item.value
