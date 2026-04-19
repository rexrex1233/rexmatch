"""
用户模型 - 账户信息 + 个人资料（已合并原 profiles 表）
"""
from datetime import datetime, date, timezone
from sqlalchemy import String, Integer, Date, DateTime, Text, Float, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # ── 账户字段 ────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="微信openid")
    union_id: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="微信unionid")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="1=正常 0=禁用 2=注销")

    # ── 资料字段（原 profiles 表） ──────────────────────────────────────
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="昵称")
    gender: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="1=男 2=女")
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True, comment="生日")
    city: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="所在城市")
    province: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="所在省份")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, comment="个人简介")
    height: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="身高(cm)")
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="体重(kg)")
    education: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="学历")
    occupation: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="职业")
    income: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="收入范围")
    
    # ── 扩展资料字段 ───────────────────────────────────────────
    mbti: Mapped[str | None] = mapped_column(String(4), nullable=True, comment="MBTI性格")
    hometown: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="家乡")
    school: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="学校")
    study_status: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="在读情况")
    industry: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="行业")
    marital_status: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="婚姻情况")
    dating_purpose: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="交友目的")
    dating_rhythm: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="恋爱节奏倾向")
    meeting_scenarios: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="喜欢的见面方式场景")

    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, comment="资料是否填写完整")

    # ── 未来扩展字段 ────────────────────────────────────────────────────
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否通过照片/实名认证")
    vip_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="VIP到期时间（null=非VIP）"
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="最后活跃时间（用于推荐权重）"
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True, comment="纬度（附近匹配）")
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True, comment="经度（附近匹配）")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── 关联 ────────────────────────────────────────────────────────────
    photos: Mapped[list["Photo"]] = relationship(back_populates="user", lazy="selectin")
    interests: Mapped[list["UserInterest"]] = relationship(back_populates="user", lazy="selectin")

    @property
    def zodiac(self) -> str | None:
        if not self.birthday:
            return None
        m = self.birthday.month
        d = self.birthday.day
        if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "白羊座"
        if (m == 4 and d >= 20) or (m == 5 and d <= 20): return "金牛座"
        if (m == 5 and d >= 21) or (m == 6 and d <= 21): return "双子座"
        if (m == 6 and d >= 22) or (m == 7 and d <= 22): return "巨蟹座"
        if (m == 7 and d >= 23) or (m == 8 and d <= 22): return "狮子座"
        if (m == 8 and d >= 23) or (m == 9 and d <= 22): return "处女座"
        if (m == 9 and d >= 23) or (m == 10 and d <= 23): return "天秤座"
        if (m == 10 and d >= 24) or (m == 11 and d <= 22): return "天蝎座"
        if (m == 11 and d >= 23) or (m == 12 and d <= 21): return "射手座"
        if (m == 12 and d >= 22) or (m == 1 and d <= 19): return "摩羯座"
        if (m == 1 and d >= 20) or (m == 2 and d <= 18): return "水瓶座"
        if (m == 2 and d >= 19) or (m == 3 and d <= 20): return "双鱼座"
        return None

    __table_args__ = (
        Index("ix_users_openid", "openid"),
        Index("ix_users_phone", "phone"),
        Index("ix_users_gender_city", "gender", "city"),
    )


from app.models.photo import Photo  # noqa: E402
from app.models.interest import UserInterest  # noqa: E402
