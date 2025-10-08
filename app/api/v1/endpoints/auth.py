from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import TokenResponse
from app.services.user_service import authenticate_user


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(response: Response, db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
  result = await authenticate_user(db, form_data.username, form_data.password)
  if not result:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid credentials")

  access_token = result
  response.set_cookie(
      key="access_token", value=access_token, httponly=True, secure=False, samesite="lax")

  return {"access_token": access_token, "token_type": "bearer"}
