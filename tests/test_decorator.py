from ultra_cache.build_cache_key import DefaultBuildCacheKey
from ultra_cache.decorator import cache
from ultra_cache.storage.inmemory import InMemoryStorage
import pytest
from fastapi import Request, Response
from pytest_mock.plugin import MockerFixture


class FnWithArgs:
    "Utility class for testing and mocking"

    def __init__(self, fn, args, kwargs) -> None:
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"{self.fn}(*{self.args}, **{self.kwargs})"


def _fn_sync(p1, p2):
    return p1 == p2


async def _fn_async(p1, p2):
    return p1 == p2


def _fn_sync_request_1(r: Request, p1, p2):
    return p1 == p2


def _fn_sync_request_2(p1, p2, request: Request):
    return p1 == p2


def _fn_sync_request_3(p1, p2, r: Request):
    return p1 == p2


def _fn_sync_response_1(r: Response, p1, p2):
    return p1 == p2


def _fn_sync_response_2(p1, p2, response: Response):
    return p1 == p2


def _fn_sync_response_3(p1, p2, r: Response):
    return p1 == p2


@pytest.fixture
def storage():
    return InMemoryStorage()


@pytest.fixture
def key_builder():
    return DefaultBuildCacheKey()


sample_args = (1, 2)
sample_request = Request({"type": "http"})
sample_response = Response()


@pytest.fixture(
    params=[
        FnWithArgs(_fn_sync, sample_args, {}),
        FnWithArgs(_fn_async, sample_args, {}),
        FnWithArgs(_fn_sync_request_1, (sample_request, *sample_args), {}),
        FnWithArgs(_fn_sync_request_2, sample_args, {"request": sample_request}),
        FnWithArgs(_fn_sync_request_3, sample_args, {"r": sample_request}),
        FnWithArgs(_fn_sync_response_1, (sample_response, *sample_args), {}),
        FnWithArgs(_fn_sync_response_2, sample_args, {"response": sample_response}),
        FnWithArgs(_fn_sync_response_3, sample_args, {"r": sample_response}),
    ]
)
def fn_with_args(request):
    return request.param


# TODO: Test TTL


@pytest.mark.anyio
async def test_decorator_cached(
    fn_with_args: FnWithArgs,
    storage: InMemoryStorage,
    key_builder: DefaultBuildCacheKey,
    mocker: MockerFixture,
):
    spy_on_save = mocker.spy(storage, "save")
    spy_on_get = mocker.spy(storage, "get")
    spy_on_fn = mocker.spy(
        fn_with_args, "fn"
    )  # Weird syntax, but did not find any alternative

    cached_fn = cache(storage=storage)(fn_with_args.fn)
    result = await cached_fn(*fn_with_args.args, **fn_with_args.kwargs)

    # Note: no request and response in args/kwargs
    key = key_builder(fn_with_args.fn, sample_args, kwargs={})
    await cached_fn(*fn_with_args.args, **fn_with_args.kwargs)

    assert spy_on_get.call_count == 2

    spy_on_save.assert_called_once_with(key=key, value=(False), ttl=None)
    spy_on_fn.assert_called_once_with(*fn_with_args.args, **fn_with_args.kwargs)

    expected = await storage.get(key)
    assert result is False
    assert expected is False
