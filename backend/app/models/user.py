"""
用户模型 - 账户基础信息
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="微信openid")
    union_id: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="微信unionid")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="1=正常 0=禁用 2=注销")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关联
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, lazy="selectin")
    photos: Mapped[list["Photo"]] = relationship(back_populates="user", lazy="selectin")

    __table_args__ = (
        Index("ix_users_openid", "openid"),
        Index("ix_users_phone", "phone"),
    )


# 避免循环导入，类型引用用字符串
from app.models.profile import Profile  # noqa: E402
from app.models.photo import Photo  # noqa: E402
