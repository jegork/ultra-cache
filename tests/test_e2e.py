from fastapi.testclient import TestClient
from .utils import app

client = TestClient(app)


def test_cache_decorator():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "MISS"

    # Test cache hit
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
    assert response.headers.get("X-Cache") == "HIT"

    # Test cache miss
    response = client.get("/items/2")
    assert response.status_code == 200
    assert response.json() == {"item_id": 2}
    assert response.headers.get("X-Cache") == "MISS"
