from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.core.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt


def verify_access_token(token: str):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("user_id")
    if user_id is None:
      return None
    return user_id
  except JWTError:
    return None
