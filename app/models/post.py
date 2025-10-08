from sqlalchemy import Column, ForeignKey,  String, TIMESTAMP, text, Boolean
from sqlalchemy.orm import relationship
from app.core.utils import generate_ulid
from app.db.session import Base


class Post(Base):
  __tablename__ = "posts"

  id = Column(String(26), primary_key=True, default=generate_ulid, index=True)
  title = Column(String, nullable=False)
  content = Column(String, nullable=False)
  published = Column(Boolean, server_default='TRUE', nullable=False)
  created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

  owner_id = Column(String, ForeignKey(
      "users.id", ondelete="CASCADE"), nullable=False)

  owner = relationship("User", back_populates="posts", lazy="joined")
