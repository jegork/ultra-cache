from ultra_cache.main import get_storage, init_cache
from ultra_cache.storage.inmemory import InMemoryStorage
import pytest


def test_init_cache():
    with pytest.raises(ValueError):
        get_storage()

    created_storage = InMemoryStorage()
    init_cache(created_storage)
    s2 = get_storage()

    assert created_storage == s2
