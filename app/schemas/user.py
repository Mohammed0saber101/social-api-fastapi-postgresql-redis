from pydantic import BaseModel, EmailStr,  field_validator


class OwnerBase(BaseModel):
  id: str
  name: str

  model_config = {
      "from_attributes": True
  }


class UserCreate(BaseModel):
  name: str
  email: EmailStr
  password: str
  hashed_password: str | None = None
  is_active: bool = True
  is_superuser: bool = False


class UserRegister(BaseModel):
  name: str
  email: EmailStr
  password: str

  @field_validator('password')
  def password_not_empty(cls, v: str):
    if len(v.strip()) < 6:
      raise ValueError(
          "Password must be at least 6 characters")
    return v


class UserResponse(BaseModel):
  id: str
  name: str
  email: EmailStr
  is_active: bool
  is_superuser: bool

  model_config = {
      "from_attributes": True
  }


class TokenResponse(BaseModel):
  access_token: str
  token_type: str
