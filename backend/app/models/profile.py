"""
用户资料模型 - 详细个人信息
"""
from datetime import datetime, date, timezone
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, comment="昵称")
    gender: Mapped[int] = mapped_column(Integer, nullable=False, comment="1=男 2=女")
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True, comment="生日")
    city: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="所在城市")
    province: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="所在省份")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, comment="个人简介")
    height: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="身高(cm)")
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="体重(kg)")
    education: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="学历")
    occupation: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="职业")
    income: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="收入范围")
    is_complete: Mapped[bool] = mapped_column(default=False, comment="资料是否填写完整")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关联
    user: Mapped["User"] = relationship(back_populates="profile")
    interests: Mapped[list["UserInterest"]] = relationship(back_populates="profile", lazy="selectin")

    __table_args__ = (
        Index("ix_profiles_gender_city", "gender", "city"),
    )


from app.models.user import User  # noqa: E402
from app.models.interest import UserInterest  # noqa: E402
