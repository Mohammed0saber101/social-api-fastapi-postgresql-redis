from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User


async def create_user(db: AsyncSession, user: User):
  db.add(user)
  await db.commit()
  await db.refresh(user)  # الهدف استرجاع ال id اللي اتولد من db
  return user


async def get_user_by_id(db: AsyncSession, user_id: str):
  result = await db.execute(select(User).where(User.id == user_id))
  return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
  result = await db.execute(select(User).where(User.email == email))
  return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession):
  result = await db.execute(select(User))
  return result.scalars().all()


async def get_all_users_active(db: AsyncSession):
  result = await db.execute(select(User).where(User.is_active == True))
  return result.scalars().all()


async def get_all_users_superuser(db: AsyncSession):
  result = await db.execute(select(User).where(User.is_superuser == True))
  return result.scalars().all()
