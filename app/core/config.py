from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
  DATABASE_URL_ASYNC: str
  DATABASE_URL_SYNC: str
  REDIS_HOST: str
  REDIS_PORT: int
  REDIS_DB: int
  REDIS_CACHE_EXPIRE_IN_SECONDS: int  # 5 minutes default
  JWT_SECRET_KEY: str

  class Config:
    env_file = ".env"


@lru_cache
def get_settings():
  return Settings()


settings = get_settings()
