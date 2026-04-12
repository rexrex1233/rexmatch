"""
收藏/稍后再看模型
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="收藏者")
    bookmarked_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="被收藏者")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_bookmarks_user_target", "user_id", "bookmarked_user_id", unique=True),
        Index("ix_bookmarks_user_id", "user_id"),
    )
