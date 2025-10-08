from datetime import datetime
from sqlalchemy import TIMESTAMP, String, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.utils import generate_ulid


class IDMixin:
  id: Mapped[str] = mapped_column(
      String(26), primary_key=True, index=True, default=lambda: generate_ulid())


class TimestampMixin:
  created_at: Mapped[datetime] = mapped_column(
      TIMESTAMP(timezone=True),
      nullable=False,
      server_default=text("CURRENT_TIMESTAMP")
  )
  updated_at: Mapped[datetime] = mapped_column(
      TIMESTAMP(timezone=True),
      nullable=False,
      server_default=text("CURRENT_TIMESTAMP"),
      server_onupdate=text("CURRENT_TIMESTAMP")
  )
