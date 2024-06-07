from fastapi import FastAPI
from ultra_cache.decorator import cache
from ultra_cache.storage.inmemory import InMemoryStorage

app = FastAPI()
storage = InMemoryStorage()


@app.get("/items/{item_id}")
@cache(storage=storage)
async def read_item(item_id: int):
    return {"item_id": item_id}
