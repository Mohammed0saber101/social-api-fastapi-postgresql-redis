from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.db.session import get_db
from app.services.post_service import (
    create_new_post, get_all_posts, get_post, remove_post, update_existing_post, update_existing_post_title)
from typing import List

router = APIRouter()

# هنا بنعمل المسار اللي يتعامل مع العميل


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def add_post(post: PostCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
  return await create_new_post(db, post, current_user.id)


@router.get("/", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 5, db: AsyncSession = Depends(get_db)):
  posts = await get_all_posts(db, skip=skip, limit=limit)
  return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id_endpoint(post_id: str, db: AsyncSession = Depends(get_db)):
  post = await get_post(db, post_id)
  if not post:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
  return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_by_id_endpoint(post_id: str, updated_post: PostUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
  post = await update_existing_post(db, post_id, updated_post, current_user.id)
  if not post:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
  return post


# @router.patch("/{post_id}", response_model=PostResponse)
# async def update_post_title_endpoint(post_id: str, new_title: str, db: AsyncSession = Depends(get_db)):
#   post = await update_existing_post_title(db, post_id, new_title)
#   if not post:
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#   return post


@router.delete("/{post_id}", response_model=PostResponse)
async def delete_post_by_id_endpoint(post_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
  post = await remove_post(db, post_id, current_user.id)
  if not post:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
  return post
