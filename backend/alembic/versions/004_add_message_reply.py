"""add message reply columns

Revision ID: 004
Revises: 003
Create Date: 2026-04-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 引用消息功能：reply_to_id（自引用）、快照内容、发送者ID
    op.add_column("messages", sa.Column("reply_to_id", sa.Integer(), nullable=True))
    op.add_column("messages", sa.Column("reply_to_content", sa.Text(), nullable=True))
    op.add_column("messages", sa.Column("reply_to_sender_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "reply_to_sender_id")
    op.drop_column("messages", "reply_to_content")
    op.drop_column("messages", "reply_to_id")
