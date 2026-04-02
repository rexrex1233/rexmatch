"""initial schema - all tables

Revision ID: 001
Revises: None
Create Date: 2026-03-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("openid", sa.String(128), nullable=False, unique=True),
        sa.Column("union_id", sa.String(128), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("status", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_openid", "users", ["openid"])
    op.create_index("ix_users_phone", "users", ["phone"])

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
        sa.Column("is_complete", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_profiles_gender_city", "profiles", ["gender", "city"])

    op.create_table(
        "photos",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("is_avatar", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "interests",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("name", sa.String(30), unique=True, nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
    )

    op.create_table(
        "user_interests",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("interest_id", sa.Integer(), sa.ForeignKey("interests.id"), nullable=False),
    )

    op.create_table(
        "swipes",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("swiper_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("swiped_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_like", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_swipes_swiper_swiped", "swipes", ["swiper_id", "swiped_id"], unique=True)
    op.create_index("ix_swipes_swiped_like", "swipes", ["swiped_id", "is_like"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user1_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("user2_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Integer(), server_default="1"),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_matches_users", "matches", ["user1_id", "user2_id"], unique=True)
    op.create_index("ix_matches_user1", "matches", ["user1_id"])
    op.create_index("ix_matches_user2", "matches", ["user2_id"])

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("msg_type", sa.String(20), server_default="text"),
        sa.Column("is_read", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_messages_match_created", "messages", ["match_id", "created_at"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reported_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("status", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("blocker_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("blocked_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_blocks_pair", "blocks", ["blocker_id", "blocked_id"], unique=True)


def downgrade() -> None:
    op.drop_table("blocks")
    op.drop_table("reports")
    op.drop_table("messages")
    op.drop_table("matches")
    op.drop_table("swipes")
    op.drop_table("user_interests")
    op.drop_table("interests")
    op.drop_table("photos")
    op.drop_table("profiles")
    op.drop_table("users")
