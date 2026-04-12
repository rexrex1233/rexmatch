"""merge users+profiles, add future-proofing columns, add swipe_type

Revision ID: 005
Revises: 004
Create Date: 2026-04-13

说明：
- 将 profiles 表所有字段合并进 users 表（1:1 关系，消除 JOIN）
- user_interests 的 profile_id FK 改为 user_id FK
- 删除 profiles 表
- users 表新增未来扩展字段：is_verified, vip_expires_at, last_active_at, latitude, longitude
- swipes 表新增 swipe_type 列（为超级喜欢功能预留）
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Step 1: 将 profiles 列添加到 users ────────────────────────────
    op.add_column("users", sa.Column("nickname", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("gender", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("birthday", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("city", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("province", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("height", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("weight", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("education", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("occupation", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("income", sa.String(30), nullable=True))
    op.add_column("users", sa.Column("is_complete", sa.Boolean(), nullable=False, server_default="false"))

    # 未来扩展字段
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("vip_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("longitude", sa.Float(), nullable=True))

    # ── Step 2: 数据迁移：profiles → users ─────────────────────────────
    op.execute("""
        UPDATE users
        SET
            nickname    = p.nickname,
            gender      = p.gender,
            birthday    = p.birthday,
            city        = p.city,
            province    = p.province,
            bio         = p.bio,
            height      = p.height,
            weight      = p.weight,
            education   = p.education,
            occupation  = p.occupation,
            income      = p.income,
            is_complete = p.is_complete
        FROM profiles p
        WHERE p.user_id = users.id
    """)

    # ── Step 3: user_interests: 新增 user_id 列并填充 ──────────────────
    op.add_column("user_interests", sa.Column("user_id", sa.Integer(), nullable=True))
    op.execute("""
        UPDATE user_interests
        SET user_id = p.user_id
        FROM profiles p
        WHERE p.id = user_interests.profile_id
    """)

    # Step 4: user_id 设为 NOT NULL 并加 FK
    op.alter_column("user_interests", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_user_interests_user_id",
        "user_interests", "users",
        ["user_id"], ["id"],
    )

    # Step 5: 删除 profile_id 列（CockroachDB 同时自动删除相关 FK 约束）
    op.drop_column("user_interests", "profile_id")

    # ── Step 6: 删除 profiles 表 ────────────────────────────────────────
    op.drop_index("ix_profiles_gender_city", table_name="profiles")
    op.drop_table("profiles")

    # ── Step 7: 新增 swipe_type 列 ──────────────────────────────────────
    op.add_column(
        "swipes",
        sa.Column("swipe_type", sa.String(20), nullable=False, server_default="like"),
    )

    # ── Step 8: 新增 users 索引 ─────────────────────────────────────────
    op.create_index("ix_users_gender_city", "users", ["gender", "city"])


def downgrade() -> None:
    # 此迁移含数据迁移，回滚不恢复数据，仅恢复结构
    op.drop_index("ix_users_gender_city", table_name="users")
    op.drop_column("swipes", "swipe_type")

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("nickname", sa.String(50), nullable=False),
        sa.Column("gender", sa.Integer(), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("city", sa.String(50), nullable=True),
        sa.Column("province", sa.String(50), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("education", sa.String(20), nullable=True),
        sa.Column("occupation", sa.String(50), nullable=True),
        sa.Column("income", sa.String(30), nullable=True),
        sa.Column("is_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_profiles_gender_city", "profiles", ["gender", "city"])

    op.add_column("user_interests", sa.Column("profile_id", sa.Integer(), nullable=True))
    op.drop_constraint("fk_user_interests_user_id", "user_interests", type_="foreignkey")
    op.drop_column("user_interests", "user_id")

    for col in ["longitude", "latitude", "last_active_at", "vip_expires_at", "is_verified",
                "is_complete", "income", "occupation", "education", "weight", "height",
                "bio", "province", "city", "birthday", "gender", "nickname"]:
        op.drop_column("users", col)
