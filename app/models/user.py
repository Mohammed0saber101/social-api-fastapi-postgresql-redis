from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base
from app.models.mixin import IDMixin, TimestampMixin
from app.models.post import Post


class UserStatusMixin:
  is_active: Mapped[bool] = mapped_column(
      Boolean, default=True, nullable=False)
  is_superuser: Mapped[bool] = mapped_column(
      Boolean, default=False, nullable=False)


class User(Base, IDMixin, TimestampMixin, UserStatusMixin):
  __tablename__ = "users"

  name: Mapped[str] = mapped_column(String(255), nullable=False)
  email: Mapped[str] = mapped_column(
      String(255), unique=True, index=True, nullable=False)
  hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

  posts: Mapped[list["Post"]] = relationship("Post", back_populates="owner",
                                             cascade="all, delete-orphan", lazy="noload")

  def __repr__(self):
    return f"<User id={self.id} name={self.name} email={self.email}>"
