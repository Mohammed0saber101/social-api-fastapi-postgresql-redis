from calendar import c
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from httpx import get

from app.core.jwt import verify_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import get_user_by_id


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(request: Request, token: str = Depends(oauth2_schema), db=Depends(get_db)) -> User:

  if not token:
    cookie_token = request.cookies.get("access_token")
    token = cookie_token  # .split(" ")[1]  # Bearer token
  if not token:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"},)

  # هنا بنعمل التحقق من الـToken وبنرجع بيانات المستخدم
  payload = verify_access_token(token)

  if not payload or len(payload) != 26:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"},)

  user = await get_user_by_id(db, payload)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found")
  return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
  if not current_user.is_active:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Inactive user")
  return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)):
  if not current_user.is_superuser:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The user doesn't have enough privileges")
  return current_user
