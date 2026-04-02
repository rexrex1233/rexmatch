"""
滑动记录模型 - 记录用户的喜欢/跳过操作
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Swipe(Base):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swiper_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="操作者")
    swiped_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="被操作者")
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False, comment="true=喜欢 false=跳过")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_swipes_swiper_swiped", "swiper_id", "swiped_id", unique=True),
        Index("ix_swipes_swiped_like", "swiped_id", "is_like"),
    )
