from abc import ABC, abstractmethod
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


class BaseStorage(ABC):
    @abstractmethod
    async def save(self, key: K, value: V, ttl: int | float | None = None) -> None: ...

    @abstractmethod
    async def get(self, key: K) -> V | None: ...

    @abstractmethod
    async def clear(self) -> None: ...
