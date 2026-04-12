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
    is_recalled: Mapped[bool] = mapped_column(default=False, comment="是否已撤回")
    recalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="撤回时间")
    is_deleted_for_sender: Mapped[bool] = mapped_column(default=False, comment="发送者已删除")
    is_deleted_for_receiver: Mapped[bool] = mapped_column(default=False, comment="接收者已删除")
    reply_to_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="引用消息ID")
    reply_to_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="引用消息内容快照")
    reply_to_sender_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="引用消息发送者ID")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    match: Mapped["Match"] = relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_match_created", "match_id", "created_at"),
    )


from app.models.match import Match  # noqa: E402
