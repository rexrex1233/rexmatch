"""add re_eligible to swipes

Revision ID: 006
Revises: 005
Create Date: 2026-04-19

说明：
- swipes 表新增 re_eligible 布尔列，默认 false
- 当用户通过「沉默清理」解除匹配时，双方 Swipe 记录的 re_eligible 设为 true
- 推荐服务据此允许这些用户重新出现在推荐池，但排分降低
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "swipes",
        sa.Column(
            "re_eligible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="沉默清理后标记为可再次推荐",
        ),
    )


def downgrade() -> None:
    op.drop_column("swipes", "re_eligible")
