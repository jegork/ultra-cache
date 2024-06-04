from ultra_cache.storage.inmemory import InMemoryStorage
import pytest
from datetime import UTC, datetime, timedelta
from freezegun import freeze_time


@pytest.fixture
def storage():
    return InMemoryStorage()


@pytest.mark.anyio
async def test_save_and_get(storage: InMemoryStorage):
    key = "key"
    value = "value"
    await storage.save(key, value)

    assert await storage.get(key) == value


@pytest.mark.anyio
async def test_save_and_get_with_ttl(storage: InMemoryStorage):
    key = "key"
    value = "value"
    await storage.save(key, value, ttl=60)

    assert await storage.get(key) == value


@pytest.mark.anyio
async def test_save_and_get_with_ttl_expired(storage: InMemoryStorage):
    key = "key"
    value = "value"
    save_time = datetime.now(UTC)
    await storage.save(key, value, ttl=60)

    with freeze_time(save_time + timedelta(seconds=100)):
        assert await storage.get(key) is None
