import redis.asyncio as redis
import json

from app.core.config import settings


redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                           db=settings.REDIS_DB, decode_responses=True)


async def ping_redis_connection():
  await redis_client.ping()


async def close_redis_connection():
  await redis_client.close()


async def set_redis_key(key: str, value: str, expire: int = settings.REDIS_CACHE_EXPIRE_IN_SECONDS):
  return await redis_client.set(name=key, value=value, ex=expire)


async def set_redis_key_object(key: str, value: object, expire: int = settings.REDIS_CACHE_EXPIRE_IN_SECONDS):
  return await redis_client.set(name=key, value=json.dumps(value), ex=expire)


async def get_redis_key(key: str):
  value = await redis_client.get(name=key)
  if value is not None:
    try:
      return json.loads(value)
    except json.JSONDecodeError:
      return value
  return None


async def update_redis_key(key: str, value: str, expire: int = settings.REDIS_CACHE_EXPIRE_IN_SECONDS):
  return await redis_client.set(name=key, value=value, ex=expire)


async def update_redis_key_object(key: str, value: object, expire: int = settings.REDIS_CACHE_EXPIRE_IN_SECONDS):
  return await redis_client.set(name=key, value=json.dumps(value), ex=expire)


async def set_redis_key_expire(key: str, expire: int):
  return await redis_client.expire(name=key, time=expire)


async def delete_redis_key(key: str):
  return await redis_client.delete(key)


async def flush_redis_db():
  return await redis_client.flushdb()
