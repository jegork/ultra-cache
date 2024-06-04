from typing import Protocol, Callable
import hashlib


class BuildCacheKey(Protocol):
    def __call__(self, func: Callable, args, kwargs) -> bytes | str: ...


class DefaultBuildCacheKey(BuildCacheKey):
    def __call__(self, func: Callable, args, kwargs) -> bytes | str:
        cache_key = hashlib.md5(  # noqa: S324
            f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode()
        ).hexdigest()
        return cache_key
