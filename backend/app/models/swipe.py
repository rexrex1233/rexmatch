"""
滑动记录模型 - 记录用户的喜欢/跳过/超级喜欢操作
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Swipe(Base):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swiper_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="操作者")
    swiped_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="被操作者")
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False, comment="true=喜欢/超级喜欢 false=跳过")
    swipe_type: Mapped[str] = mapped_column(
        String(20), default="like", comment="like=普通喜欢 super_like=超级喜欢 nope=跳过"
    )
    re_eligible: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="沉默清理后标记为可再次推荐"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_swipes_swiper_swiped", "swiper_id", "swiped_id", unique=True),
        Index("ix_swipes_swiped_like", "swiped_id", "is_like"),
    )
