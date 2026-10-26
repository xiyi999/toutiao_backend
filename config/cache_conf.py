import json
from typing import Any

import redis.asyncio as redis


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    # Older Redis-compatible servers may not implement HELLO/RESP3 negotiation.
    protocol=2,
)


async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"得到缓存失败 : {e}")
        return None


async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data is not None:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"得到JSON缓存失败 : {e}")
        return None


async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
