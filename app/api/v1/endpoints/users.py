from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.user_service import register_new_user,  get_exist_user_by_id

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserRegister, db: AsyncSession = Depends(get_db)):
  try:
    return await register_new_user(db, user)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/me',  response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
  return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
  user = await get_exist_user_by_id(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user
