from ultra_cache.build_cache_key import DefaultBuildCacheKey
from pydantic import BaseModel


def test_build_cache_key_equal():
    def _sample_fn():
        pass

    build_cache_key = DefaultBuildCacheKey()
    args = (1, 2)
    kwargs = {}

    key1 = build_cache_key(_sample_fn, args, kwargs)
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn, args, kwargs)
    assert key1 == key2


def test_build_cache_key_different_func():
    def _sample_fn():
        pass

    def _sample_fn2():
        pass

    build_cache_key = DefaultBuildCacheKey()
    args = (1, 2)
    kwargs = {}

    key1 = build_cache_key(_sample_fn, args, kwargs)
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn2, args, kwargs)
    assert key1 != key2


def test_build_cache_key_different_args():
    def _sample_fn():
        pass

    build_cache_key = DefaultBuildCacheKey()
    kwargs = {}

    key1 = build_cache_key(_sample_fn, (1, 2), kwargs)
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn, (1), kwargs)
    assert key1 != key2

    key3 = build_cache_key(_sample_fn, (), kwargs)

    assert key1 != key3
    assert key2 != key3


def test_build_cache_key_different_kwargs():
    def _sample_fn():
        pass

    build_cache_key = DefaultBuildCacheKey()
    args = (1, 2)

    key1 = build_cache_key(_sample_fn, args, {"kw1": "kw1", "kw2": "kw2"})
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn, args, {})
    assert key1 != key2

    key3 = build_cache_key(_sample_fn, args, {"kw1": "kw1"})

    assert key1 != key3
    assert key2 != key3


def test_build_cache_key_different_pydantic_models():
    class Model(BaseModel):
        x: str
        y: int

    def _sample_fn():
        pass

    build_cache_key = DefaultBuildCacheKey()
    kwargs = {}

    key1 = build_cache_key(_sample_fn, (Model(x="1", y=1)), kwargs)
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn, (Model(x="2", y=1)), kwargs)
    assert key1 != key2


def test_build_cache_key_same_pydantic_models():
    class Model(BaseModel):
        x: str
        y: int

    def _sample_fn():
        pass

    build_cache_key = DefaultBuildCacheKey()
    kwargs = {}

    key1 = build_cache_key(_sample_fn, (Model(x="1", y=1)), kwargs)
    assert isinstance(key1, str)

    key2 = build_cache_key(_sample_fn, (Model(x="1", y=1)), kwargs)
    assert key1 == key2
