"""add bookmarks table and message recall/delete fields

Revision ID: 003
Revises: 002
Create Date: 2026-04-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # bookmarks 表
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bookmarked_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_bookmarks_user_target", "bookmarks", ["user_id", "bookmarked_user_id"], unique=True)
    op.create_index("ix_bookmarks_user_id", "bookmarks", ["user_id"])

    # messages 表新增撤回/删除字段
    op.add_column("messages", sa.Column("is_recalled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("messages", sa.Column("recalled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("messages", sa.Column("is_deleted_for_sender", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("messages", sa.Column("is_deleted_for_receiver", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("messages", "is_deleted_for_receiver")
    op.drop_column("messages", "is_deleted_for_sender")
    op.drop_column("messages", "recalled_at")
    op.drop_column("messages", "is_recalled")
    op.drop_index("ix_bookmarks_user_id", table_name="bookmarks")
    op.drop_index("ix_bookmarks_user_target", table_name="bookmarks")
    op.drop_table("bookmarks")
