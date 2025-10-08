from fastapi import HTTPException
from app.core.redis_client import get_redis_key, set_redis_key, redis_client


async def rate_limiter(key: str, limit: int, period: int) -> bool:
  """
  Rate limiter using Redis.

  Args:
      key (str): The key to identify the user or action.
      limit (int): The maximum number of allowed actions within the period.
      period (int): The time period in seconds.

  Returns:
      bool: True if the action is allowed, False if rate limit is exceeded.
  """
  current = await get_redis_key(key)
  if current is None:
    await set_redis_key(key, 1, period)
    return {'limit': limit, 'remaining': limit - 1, 'reset': period}

  ttl = await redis_client.ttl(key)

  if int(current) >= limit:
    raise HTTPException(status_code=429, detail={
                        "error": "Rate limit exceeded", "limit": limit, "remaining": 0, "reset": ttl if ttl > 0 else period})

  await redis_client.incr(key)

  return {'limit': limit, 'remaining': limit - int(current) - 1, 'reset': ttl}
