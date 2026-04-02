"""
用户照片模型
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False, comment="图片URL")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序序号")
    is_avatar: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为头像")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="photos")


from app.models.user import User  # noqa: E402
