"""
举报与拉黑模型
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    """举报记录"""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="举报人")
    reported_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="被举报人")
    reason: Mapped[str] = mapped_column(String(50), nullable=False, comment="举报原因分类")
    detail: Mapped[str | None] = mapped_column(Text, nullable=True, comment="详细描述")
    status: Mapped[int] = mapped_column(Integer, default=0, comment="0=待处理 1=已处理 2=已驳回")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Block(Base):
    """拉黑记录"""
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blocker_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_blocks_pair", "blocker_id", "blocked_id", unique=True),
    )
