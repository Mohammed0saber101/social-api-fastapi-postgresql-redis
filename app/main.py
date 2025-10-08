from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from contextlib import asynccontextmanager

from app.core.cache.posts_cache import create_consumer_group, stream_consumer
from app.core.redis_client import flush_redis_db, ping_redis_connection, close_redis_connection
from app.api.v1.router import api_router
from app.middleware.rate_limit_middleware import rate_limit_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
  # Startup code
  await ping_redis_connection()
  print("Redis connected ✅")

  await create_consumer_group()
  consumer_task = asyncio.create_task(stream_consumer())

  yield

  # Shutdown code
  if consumer_task:
    consumer_task.cancel()
    try:
      await consumer_task
    except asyncio.CancelledError:
      print("Stream consumer task cancelled ❌")

  await flush_redis_db()
  print("Redis cache flushed 🧹")
  await close_redis_connection()
  print("Redis disconnected ❌")


origins = ['http://localhost:5173']


def create_app() -> FastAPI:
  app = FastAPI(title="Social API", version="1.0", lifespan=lifespan)
  app.add_middleware(CORSMiddleware,
                     allow_origins=origins,
                     allow_credentials=True,
                     allow_methods=["*"],
                     allow_headers=["*"],)
  app.middleware("http")(rate_limit_middleware)
  app.include_router(api_router, prefix="/api/v1")
  return app


app = create_app()


@app.get("/")
async def healthchecker():
  return {"status": "OK", "message": "Welcome to Social API. Can use our API now"}


# uvicorn --reload app.main:app
# sudo service redis-server start


if __name__ == "__main__":
  uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
