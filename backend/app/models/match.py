"""
匹配模型 - 双向喜欢后生成匹配记录
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=1, comment="1=有效 0=已解除")
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user1: Mapped["User"] = relationship(foreign_keys=[user1_id], lazy="selectin")
    user2: Mapped["User"] = relationship(foreign_keys=[user2_id], lazy="selectin")
    messages: Mapped[list["Message"]] = relationship(back_populates="match", lazy="select")

    __table_args__ = (
        Index("ix_matches_users", "user1_id", "user2_id", unique=True),
        Index("ix_matches_user1", "user1_id"),
        Index("ix_matches_user2", "user2_id"),
    )


from app.models.user import User  # noqa: E402
from app.models.message import Message  # noqa: E402
