from abc import ABC, abstractmethod


class BaseStorage[K, V](ABC):
    @abstractmethod
    async def save(self, key: K, value: V, ttl: int | float | None = None) -> None: ...

    @abstractmethod
    async def get(self, key: K) -> V | None: ...
