"""
兴趣标签模型 - 预定义标签 + 用户-标签关联
"""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Interest(Base):
    """预定义的兴趣标签"""
    __tablename__ = "interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, comment="标签名")
    category: Mapped[str] = mapped_column(String(30), nullable=False, comment="分类：运动/音乐/美食/旅行等")
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="图标标识")


class UserInterest(Base):
    """用户选择的兴趣标签（多对多关联表）"""
    __tablename__ = "user_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    interest_id: Mapped[int] = mapped_column(Integer, ForeignKey("interests.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="interests")
    interest: Mapped["Interest"] = relationship(lazy="selectin")


from app.models.user import User  # noqa: E402
