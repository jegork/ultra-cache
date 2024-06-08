from abc import ABC, abstractmethod
from typing import TypeVar, Union

K = TypeVar("K")
V = TypeVar("V")


class BaseStorage(ABC):
    @abstractmethod
    async def save(
        self, key: K, value: V, ttl: Union[int, float, None] = None
    ) -> None: ...

    @abstractmethod
    async def get(self, key: K) -> Union[V, None]: ...

    @abstractmethod
    async def clear(self) -> None: ...
