from fastapi import FastAPI
from ultra_cache.decorator import UltraCache
from ultra_cache.storage.inmemory import InMemoryStorage

app = FastAPI()
storage = InMemoryStorage()
cache = UltraCache(storage=storage)


@app.get("/items/{item_id}")
@cache()
async def read_item(item_id: int):
    return {"item_id": item_id}
