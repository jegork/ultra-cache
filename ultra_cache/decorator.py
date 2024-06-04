import asyncio
from functools import partial
from typing import Any, Callable
from collections.abc import Coroutine
import inspect

import anyio
import anyio.to_thread

from ultra_cache.build_cache_key import BuildCacheKey, DefaultBuildCacheKey
from ultra_cache.main import get_storage
from ultra_cache.storage.base import BaseStorage
from fastapi import Request, Response


def _extract_special_param(_fn, param_type: type) -> None | inspect.Parameter:
    sig = inspect.signature(_fn)
    for _, param in sig.parameters.items():
        if param.annotation == param_type:
            return param
    return None


def _extract[S1, S2](
    param: inspect.Parameter | None, args: tuple[S1, ...], kwargs: dict[str, S2]
) -> tuple[tuple[S1, ...], dict[str, S2]]:
    if param is None:
        return args, kwargs

    if param.name in kwargs:
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop(param.name)
        return (args, kwargs_copy)
    else:
        request_index = next(
            (i for i, p in enumerate(args) if isinstance(p, param.annotation)), -1
        )
        if request_index == -1:
            raise ValueError(f"No argument of type {param.annotation} found in args")
        args_copy = args[:request_index] + args[request_index + 1 :]
        return (args_copy, kwargs)


def _merge_args[T](value: T, index: int, *tup: T) -> tuple[T, ...]:
    return tup[:index] + (value,) + tup[index:]


def cache(
    ttl: int | float | None = None,
    build_cache_key: BuildCacheKey = DefaultBuildCacheKey(),
    storage: BaseStorage | None = None,
):
    def _wrapper[**P, R](
        func: Callable[P, R | Coroutine[R, Any, Any]],
    ) -> Callable[P, Coroutine[R, Any, Any]]:
        async def _decorator(*args: P.args, **kwargs: P.kwargs):
            nonlocal storage

            request_param = _extract_special_param(func, Request)
            response_param = _extract_special_param(func, Response)

            args_for_key, kwargs_for_key = _extract(
                response_param, *(_extract(request_param, args, kwargs))
            )
            key = build_cache_key(func, args=args_for_key, kwargs=kwargs_for_key)

            if storage is None:
                storage = get_storage()

            cached = await storage.get(key)

            if cached is not None:
                return cached

            # Note: inspect.iscoroutinefunction returns False for AsyncMock
            if asyncio.iscoroutinefunction(func):
                output = await func(*args, **kwargs)
            else:
                output = await anyio.to_thread.run_sync(partial(func, *args, **kwargs))

            await storage.save(key=key, value=output, ttl=ttl)

            return output

        return _decorator

    return _wrapper
