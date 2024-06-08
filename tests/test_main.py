from fakeredis import FakeAsyncRedis
from ultra_cache.decorator import UltraCache
from ultra_cache.storage.inmemory import InMemoryStorage
import pytest

from ultra_cache.storage.redis import RedisStorage


@pytest.fixture(params=[InMemoryStorage(), RedisStorage(FakeAsyncRedis())])
def storage(request):
    return request.param


def test_init_cache(storage):
    cache = UltraCache(storage=storage)

    assert isinstance(cache.storage, type(storage))
