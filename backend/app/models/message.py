"""
聊天消息模型
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    msg_type: Mapped[str] = mapped_column(
        String(20), default="text", comment="text/image/system"
    )
    is_read: Mapped[bool] = mapped_column(default=False, comment="是否已读")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    match: Mapped["Match"] = relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_match_created", "match_id", "created_at"),
    )


from app.models.match import Match  # noqa: E402
