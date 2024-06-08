from ultra_cache.storage.redis import RedisStorage
from fakeredis import FakeAsyncRedis
import pytest
from datetime import timedelta
from freezegun import freeze_time

from ultra_cache.utils import utc_now


@pytest.fixture
async def storage(mocker):
    redis_instance = FakeAsyncRedis(decode_responses=True)
    mocker.spy(redis_instance, "set")
    mocker.spy(redis_instance, "get")
    mocker.spy(redis_instance, "keys")
    mocker.spy(redis_instance, "delete")
    return RedisStorage(redis_instance)


@pytest.mark.anyio
async def test_save_and_get(storage: RedisStorage):
    key = "key"
    value = "value"
    await storage.save(key, value)

    storage.redis.set.assert_called_once_with(f"ultra-cache:{key}", value, ex=None)
    assert await storage.get(key) == value
    storage.redis.get.assert_called_once_with(f"ultra-cache:{key}")


@pytest.mark.anyio
async def test_save_and_get_with_ttl(storage: RedisStorage):
    key = "key"
    value = "value"
    ttl = 60
    await storage.save(key, value, ttl=ttl)

    storage.redis.set.assert_called_once_with(f"ultra-cache:{key}", value, ex=ttl)
    assert await storage.get(key) == value
    storage.redis.get.assert_called_once_with(f"ultra-cache:{key}")


@pytest.mark.anyio
async def test_save_and_get_with_ttl_expired(storage: RedisStorage):
    key = "key"
    value = "value"
    ttl = 60
    save_time = utc_now()
    await storage.save(key, value, ttl=ttl)

    storage.redis.set.assert_called_once_with(f"ultra-cache:{key}", value, ex=ttl)

    with freeze_time(save_time + timedelta(seconds=100)):
        assert await storage.get(key) is None
        storage.redis.get.assert_called_once_with(f"ultra-cache:{key}")


@pytest.mark.anyio
async def test_clear(storage: RedisStorage):
    key1 = "key1"
    value1 = "value1"
    key2 = "key2"
    value2 = "value2"
    await storage.save(key1, value1)
    await storage.save(key2, value2)

    await storage.clear()

    storage.redis.keys.assert_called_once_with("ultra-cache:*")
    storage.redis.delete.assert_called_once()
    assert await storage.get(key1) is None
    assert await storage.get(key2) is None
