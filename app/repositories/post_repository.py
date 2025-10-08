from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.models.post import Post
from app.schemas.post import PostCreate


# هنا بنكتب الكود اللي يتعامل مع قاعدة البيانات فقط
async def create_post(db: AsyncSession, post_data: PostCreate, user_id: str):
  new_post = Post(**post_data.model_dump(), owner_id=user_id)
  db.add(new_post)
  await db.commit()
  await db.refresh(new_post)  # الهدف استرجاع ال id اللي اتولد من db
  return new_post

  # result = await db.execute(select(Post).options(selectinload(Post.owner)).order_by(Post.id.desc()))


async def get_posts(db: AsyncSession, skip: int, limit: int):
  result = await db.execute(select(Post).limit(limit).offset(skip).order_by(Post.id.desc()))
  return result.scalars().all()


async def get_post_by_id(db: AsyncSession, post_id: str):
  result = await db.execute(select(Post).where(Post.id == post_id))
  return result.scalar_one_or_none()


async def update_post(db: AsyncSession, post: Post, updated_data: PostCreate):
  for key, value in updated_data.model_dump(exclude_unset=True).items():
    setattr(post, key, value)
  db.add(post)
  await db.commit()
  await db.refresh(post)
  return post


async def update_post_title(db: AsyncSession, post: Post):
  db.add(post)
  await db.commit()
  await db.refresh(post)
  return post


async def delete_post(db: AsyncSession, post: Post):
  await db.delete(post)
  await db.commit()
  return post
