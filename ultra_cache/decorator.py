import asyncio
from functools import partial, wraps
from typing import Any, Callable, ParamSpec, Union, TypeVar
from collections.abc import Coroutine
import inspect

import anyio
import anyio.to_thread
from dict_hash import dict_hash
from ultra_cache.build_cache_key import BuildCacheKey, DefaultBuildCacheKey
from ultra_cache.cache_control import CacheControl
from ultra_cache.main import get_storage
from ultra_cache.storage.base import BaseStorage
from fastapi import Request, Response

P = ParamSpec("P")
R = TypeVar("R")

S1 = TypeVar("S1")
S2 = TypeVar("S2")


def _extract_param_of_type(
    sig: inspect.Signature, param_type: type
) -> None | inspect.Parameter:
    for _, param in sig.parameters.items():
        if param.annotation == param_type:
            return param
    return None


def _default_hash_fn(x: Any) -> str:
    if isinstance(x, dict) or isinstance(x, list):
        return "W/" + str(dict_hash(x, maximal_recursion=10))

    return "W/" + str(hash(x))


def _extract(
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
            return args, kwargs
        args_copy = args[:request_index] + args[request_index + 1 :]
        return (args_copy, kwargs)


def _does_etag_match(etag: str, if_none_match: str | None) -> bool:
    if if_none_match is not None and (
        if_none_match == "*" or any(etag == x.strip() for x in if_none_match.split(","))
    ):
        return True
    return False


def cache(
    ttl: int | float | None = None,
    build_cache_key: BuildCacheKey = DefaultBuildCacheKey(),
    storage: BaseStorage | None = None,
    hash_fn: Callable[[Any], str] = _default_hash_fn,
):
    def _wrapper(
        func: Callable[P, Union[R, Coroutine[R, Any, Any]]],
    ) -> Callable[P, Coroutine[R, Any, Any]]:
        sig = inspect.signature(func)

        original_request_param = _extract_param_of_type(sig, Request)
        original_response_param = _extract_param_of_type(sig, Response)
        request_param = original_request_param
        response_param = original_response_param

        new_parameters = list(sig.parameters.values())
        if request_param is None:
            request_param = inspect.Parameter(
                "request", annotation=Request, kind=inspect.Parameter.KEYWORD_ONLY
            )
            new_parameters.append(request_param)
        if response_param is None:
            response_param = inspect.Parameter(
                "response", annotation=Response, kind=inspect.Parameter.KEYWORD_ONLY
            )
            new_parameters.append(response_param)

        func.__signature__ = sig.replace(parameters=new_parameters)

        # allows for the decorator to be used with fastapi params interospection
        @wraps(func)
        async def _decorator(*args: P.args, **kwargs: P.kwargs):
            nonlocal storage
            request: Request = kwargs.get(request_param.name)
            response: Response = kwargs.get(response_param.name)

            cache_control = CacheControl.from_string(
                request.headers.get("cache-control", None)
            )
            if_none_match = request.headers.get("if-none-match", None)

            args_for_key, kwargs_for_key = _extract(
                response_param, *(_extract(request_param, args, kwargs))
            )
            key = build_cache_key(func, args=args_for_key, kwargs=kwargs_for_key)

            if storage is None:
                storage = get_storage()

            cached = None
            if not cache_control.no_cache:
                cached = await storage.get(key)

            if ttl:
                cache_control.setdefault("max-age", ttl)

            response.headers["Cache-Control"] = cache_control.to_response_header()

            if cached is not None:
                response.headers["X-Cache"] = "HIT"
                response.headers["ETag"] = hash_fn(cached)

                if request.method in ["HEAD", "GET"]:
                    if _does_etag_match(response.headers["ETag"], if_none_match):
                        response.status_code = 304
                        return

                return cached
            else:
                response.headers["X-Cache"] = "MISS"

            if original_request_param is None:
                kwargs.pop("request")
            if original_response_param is None:
                kwargs.pop("response")

            # Note: inspect.iscoroutinefunction returns False for AsyncMock
            if asyncio.iscoroutinefunction(func):
                output = await func(*args, **kwargs)
            else:
                output = await anyio.to_thread.run_sync(partial(func, *args, **kwargs))

            response.headers["ETag"] = hash_fn(output)
            if request.method in ["HEAD", "GET"]:
                if _does_etag_match(response.headers["ETag"], if_none_match):
                    response.status_code = 304
                    return

            if not cache_control.no_store:
                await storage.save(
                    key=key, value=output, ttl=cache_control.max_age or ttl
                )

            return output

        return _decorator

    return _wrapper
