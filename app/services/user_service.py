from sqlalchemy.ext.asyncio import AsyncSession
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import create_user, get_user_by_email, get_user_by_id
from app.schemas.user import UserCreate, UserRegister


# async def register_new_user(db: AsyncSession, user_data: UserRegister):
#   # لازم تتأكد إن الباسورد متشفر قبل ما تبعته
#   hashed_pw = hash_password(user_data.password)
#   del user_data.password  # بنشيل الباسورد العادي من ال data
#   user_in = UserCreate(**user_data.model_dump(), hashed_password=hashed_pw)
#   return await create_user(db, user_in)

async def register_new_user(db: AsyncSession, user_data: UserRegister):
  # check if user exists
  exists = await get_user_by_email(db, user_data.email)
  if exists:
    raise ValueError('Email already registered')

  # create user
  new_user = User(name=user_data.name, email=user_data.email,
                  hashed_password=hash_password(user_data.password))
  return await create_user(db, new_user)


async def get_exist_user_by_id(db: AsyncSession, user_id: str):
  user = await get_user_by_id(db, user_id)
  if not user:
    return None
  return user


async def get_exist_user_by_email(db: AsyncSession, email: str):
  user = await get_user_by_email(db, email)
  if not user:
    return None
  return user


async def authenticate_user(db: AsyncSession, email: str, password: str):
  user = await get_user_by_email(db, email)
  if not user or not verify_password(password, user.hashed_password) or not user.is_active:
    return None
  access_token = create_access_token(data={"user_id": user.id})
  return access_token
