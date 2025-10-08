from sqlalchemy.ext.asyncio import AsyncSession
from app.core.cache.posts_cache import publish_post_event
from app.core.redis_client import delete_redis_key, get_redis_key, set_redis_key_object
from app.schemas.post import PostCreate, PostResponse, PostsResponseRedis
from app.repositories.post_repository import (
    create_post,
    get_posts,
    get_post_by_id,
    delete_post,
    update_post,
    update_post_title
)


# هنا بنضيف الـBusiness Logic قبل ما نعمل الـInsert
async def create_new_post(db: AsyncSession, post_data: PostCreate, user_id: str):

  post = await create_post(db, post_data, user_id)
  if not post:
    return None

  new_post_data = PostsResponseRedis.from_post_response(
      PostResponse.model_validate(post)).model_dump()
  await publish_post_event("create", new_post_data)

  return post


async def get_all_posts(db: AsyncSession, skip: int, limit: int):
  cache_key = f'posts:skip:{skip}:limit:{limit}'
  cached_posts = await get_redis_key(cache_key)
  if cached_posts:
    print(f'Cached hit - from redis - posts:{cache_key} ✅')
    return cached_posts

  print(f'Cache miss - from db - posts:{cache_key} ❌')
  posts = await get_posts(db, skip, limit)

  posts_data = [PostsResponseRedis.from_post_response(
      PostResponse.model_validate(post)).model_dump() for post in posts]
  await set_redis_key_object(cache_key, posts_data)

  return posts


async def get_post(db: AsyncSession, post_id: str):
  cached_post = await get_redis_key(f'post:{post_id}')
  if cached_post:
    print(f'Cached hit - from redis - post:{post_id} ✅')
    return cached_post

  post = await get_post_by_id(db, post_id)
  if not post:
    return None

  print(f'Cache miss - from db - post:{post_id} ❌')
  post_data = PostsResponseRedis.from_post_response(
      PostResponse.model_validate(post)).model_dump()
  await set_redis_key_object(f'post:{post_id}', post_data)

  return post


async def update_existing_post(db: AsyncSession, post_id: str, updated_data: PostCreate, user_id: str):
  post = await get_post_by_id(db, post_id)
  if not post or post.owner_id != user_id:
    return None

  updated_post = await update_post(db, post, updated_data)
  if not updated_post:
    return None

  post_data = PostsResponseRedis.from_post_response(
      PostResponse.model_validate(post)).model_dump()
  await publish_post_event("update", post_data)
  await set_redis_key_object(f'post:{post_id}', post_data)

  return updated_post


async def remove_post(db: AsyncSession, post_id: str, user_id: str):
  post = await get_post_by_id(db, post_id)
  if not post or post.owner_id != user_id:
    return None

  deleted_post = await delete_post(db, post)
  if not deleted_post:
    return None

  post_data = PostsResponseRedis.from_post_response(
      PostResponse.model_validate(post)).model_dump()
  await publish_post_event("delete", post_data)
  await delete_redis_key(f'post:{post_id}')

  return deleted_post


async def update_existing_post_title(db: AsyncSession, post_id: str, new_title: str):
  post = await get_post_by_id(db, post_id)
  if not post:
    return None
  post.title = new_title
  return await update_post_title(db, post)
