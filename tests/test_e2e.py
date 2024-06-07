import asyncio
from fastapi.testclient import TestClient
import pytest

from ultra_cache.decorator import _default_hash_fn
from . import utils


client = TestClient(utils.app)


@pytest.fixture(autouse=True, scope="function")
def reset_cache():
    try:
        loop = asyncio.get_event_loop()
    except:  # noqa: E722
        loop = asyncio.new_event_loop()
    loop.run_until_complete(utils.storage.clear())
    yield
    loop.close()


# TODO: Reset cache between tests
def test_cache_decorator():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("Cache-Control", "") == ""
    etag_1 = response.headers.get("ETag")
    assert etag_1 is not None

    # Test cache hit
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "HIT"
    assert response.headers.get("Cache-Control", "") == ""
    etag_2 = response.headers.get("ETag")
    assert etag_2 is not None
    assert etag_1 == etag_2

    # Test cache miss
    response = client.get("/items/2")
    assert response.status_code == 200
    assert response.json() == {"item_id": 2}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("ETag") != etag_1
    assert response.headers.get("Cache-Control", "") == ""


def test_cache_with_maxage():
    response = client.get("/items/1", headers={"Cache-Control": "max-age=10"})
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("Cache-Control", "") == "max-age=10"


def test_cache_with_if_none_match_hit():
    response = client.get(
        "/items/1",
    )
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("Cache-Control", "") == ""

    etag = response.headers.get("ETag")
    assert etag is not None
    assert etag == _default_hash_fn(response.json())

    # run again with If-None-Match
    response = client.get("/items/1", headers={"If-None-Match": etag})

    assert response.status_code == 304
    assert response.headers.get("X-Cache") == "HIT"
    assert response.headers.get("Cache-Control", "") == ""
    assert response.headers.get("ETag") == etag


def test_cache_with_if_none_match_hit_star():
    response = client.get(
        "/items/1",
    )
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("Cache-Control", "") == ""

    etag = response.headers.get("ETag")
    assert etag is not None
    assert etag == _default_hash_fn(response.json())

    # run again with If-None-Match
    response = client.get("/items/1", headers={"If-None-Match": "*"})

    assert response.status_code == 304
    assert response.headers.get("X-Cache") == "HIT"
    assert response.headers.get("Cache-Control", "") == ""
    assert response.headers.get("ETag") == etag


def test_cache_with_if_none_match_miss():
    response = client.get(
        "/items/1",
    )
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"
    assert response.headers.get("Cache-Control", "") == ""

    etag = response.headers.get("ETag")
    assert etag is not None
    assert etag == _default_hash_fn(response.json())

    # run again with If-None-Match
    response = client.get("/items/1", headers={"If-None-Match": "W/123"})

    assert response.status_code == 200
    assert response.headers.get("X-Cache") == "HIT"
    assert response.headers.get("Cache-Control", "") == ""
    assert response.headers.get("ETag") == etag
