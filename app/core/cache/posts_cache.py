import asyncio
import json
import redis.asyncio as redis

from app.core.redis_client import get_redis_key, redis_client, set_redis_key_object


STREAM_KEY = "posts:stream"
GROUP_NAME = "posts_group"
CONSUMER_NAME = "posts_consumer_1"
CACHE_KEY_ALL_POSTS = "posts:all"


async def create_consumer_group():
  try:
    await redis_client.xgroup_create(name=STREAM_KEY, groupname=GROUP_NAME, id='0', mkstream=True)
  except redis.ResponseError as e:
    if "BUSYGROUP" in str(e):
      print("Consumer group already exists")
    else:
      raise e


# ---------- Producer: ننشر حدث بعد إنشاء post ----------
async def publish_post_event(event_type: str, payload: dict):
  """
  event_type: str  # "create", "update", "delete"
  payload: dict   # البيانات اللي عايزين نبعتها مع الحدث
  Redis stream في الستريم بضيف حدث جديد باستخدام XADD command
  STREAM_KEY: str  # اسم الستريم
  event_type: str  # نوع الحدث
  """
  # add a new entry to the stream with XADD command
  await redis_client.xadd(STREAM_KEY, {"type": event_type, "data": json.dumps(payload, default=str)})


# ---------- Consumer: يقرأ من Consumer Group ويحدّث الكاش ----------
async def stream_consumer():
  """
  Loop يقرأ رسائل جديدة من الستريم باستخدام xreadgroup وينفّذ عملية المعالجة،
  ثم يعمل ACK (xack) عند النجاح.
  """
  while True:
    try:
      # نقرأ رسائل جديدة (block لمدة 5000 ms لو مفيش)
      entries = await redis_client.xreadgroup(groupname=GROUP_NAME, consumername=CONSUMER_NAME,
                                              streams={STREAM_KEY: '>'}, count=1, block=5000)

      if not entries:
        continue  # مفيش رسائل جديدة، نعيد المحاولة مرة تانية

      for stream_name, messages in entries:
        for message_id, message in messages:
          event_type = message.get("type")
          data = json.loads(message.get("data"))

          cached_posts = await get_redis_key(CACHE_KEY_ALL_POSTS)

          if event_type == "create":
            if cached_posts:
              cached_posts.insert(0, data)  # نضيف البوست الجديد في البداية
              await set_redis_key_object(CACHE_KEY_ALL_POSTS, cached_posts)
            else:
              await set_redis_key_object(CACHE_KEY_ALL_POSTS, [data])

          elif event_type == "update":
            if cached_posts:
              for idx, post in enumerate(cached_posts):
                if post['id'] == data['id']:
                  cached_posts[idx] = data  # نحدّث البوست الموجود
                  await set_redis_key_object(CACHE_KEY_ALL_POSTS, cached_posts)
                  break

          elif event_type == "delete":
            if cached_posts:
              cached_posts = [
                  post for post in cached_posts if post['id'] != data['id']]
              await set_redis_key_object(CACHE_KEY_ALL_POSTS, cached_posts)

          else:
            # Invalidate the cache for all posts
            await redis_client.delete(CACHE_KEY_ALL_POSTS)

          # Acknowledge the message
          await redis_client.xack(STREAM_KEY, GROUP_NAME, message_id)

    except Exception as e:
      print(f"Error in stream consumer: {e}")
      await asyncio.sleep(1)  # wait before retrying in case of error
