"""
用户偏好模型 - 存储择偶偏好，用于契合度计算
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_gender: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="期望性别 1=男 2=女")
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最小年龄")
    max_age: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大年龄")
    preferred_city: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="期望城市")
    preferred_education: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="期望学历")
    personality_tags: Mapped[str | None] = mapped_column(Text, nullable=True, comment="偏好性格标签 JSON数组")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id], lazy="selectin")

    __table_args__ = (
        Index("ix_user_preferences_user_id", "user_id", unique=True),
    )


from app.models.user import User  # noqa: E402
