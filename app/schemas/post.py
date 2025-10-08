from pydantic import BaseModel, field_validator
from datetime import datetime

from app.schemas.user import OwnerBase

# هنا بنعرف شكل البيانات اللي داخلة والخارجة من الـAPI


class PostCreate(BaseModel):
  title: str
  content: str
  published: bool = True

  @field_validator('title')
  def title_must_not_be_empty(cls, v):
    if not v or not v.strip():
      raise ValueError('Title must not be empty')
    return v.strip()


class PostUpdate(BaseModel):
  title: str | None = None
  content: str | None = None
  published: bool | None = None


class PostResponse(BaseModel):
  id: str
  title: str
  content: str
  published: bool
  created_at: datetime
  owner: OwnerBase

  # Pydantic 2.0
  model_config = {
      "from_attributes": True
  }


class PostsResponseRedis(PostResponse):
  created_at: str  # Redis cache عشان نقدر نخزنها في

  @classmethod
  def from_post_response(cls, post: PostResponse):
    data = post.model_dump()
    data['created_at'] = data['created_at'].isoformat()
    return cls.model_validate(data)

  # Pydantic 1.0
  # class Config:
  #   orm_mode = True  # SQLAlchemy object لـ  Pydantic model عشان نقدر نحول من
