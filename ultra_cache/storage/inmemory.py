from ultra_cache.storage.base import BaseStorage
from datetime import timedelta
from typing import TypeVar, Union

from ultra_cache.utils import utc_now


K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class InMemoryStorageItem:
    def __init__(self, data: T, ttl: Union[int, float, None] = None) -> None:
        self._data = data
        self._ttl = ttl
        self._start = utc_now()

    def __str__(self) -> str:
        return f"InMemoryStorageItem(date={self._data}, expired={self.expired})"

    @property
    def expired(self) -> bool:
        if self._ttl is None:
            return False

        return (utc_now() - self._start) > timedelta(seconds=self._ttl)

    @property
    def value(self) -> Union[T, None]:
        if self.expired:
            return None

        return self._data


class InMemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self.storage: dict[K, InMemoryStorageItem[V]] = {}

    async def save(self, key: K, value: V, ttl: Union[int, float, None] = None) -> None:
        self.storage[key] = InMemoryStorageItem(value, ttl)

    async def get(self, key: K) -> Union[V, None]:
        item = self.storage.get(key, None)

        if item is None:
            return None

        return item.value

    async def clear(self) -> None:
        self.storage = {}
