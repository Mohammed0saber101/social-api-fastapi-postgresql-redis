from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


# ملف إعداد قاعدة البيانات
engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)
asyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
  async with asyncSessionLocal() as session:
    yield session


# class Base(declarative_base()):
#   pass

Base = declarative_base()
