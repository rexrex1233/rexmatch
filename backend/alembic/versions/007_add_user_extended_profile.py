"""add extended profile fields to users

Revision ID: 007
Revises: 006
Create Date: 2026-04-19

说明：
- users 表新增 9 个扩展资料字段，对应 onboarding 新增步骤收集的信息
- mbti / hometown / school / study_status / industry / marital_status
  / dating_purpose / dating_rhythm / meeting_scenarios
- 全部可为空，不影响现有用户
"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("mbti", sa.String(4), nullable=True, comment="MBTI性格"))
    op.add_column("users", sa.Column("hometown", sa.String(50), nullable=True, comment="家乡"))
    op.add_column("users", sa.Column("school", sa.String(50), nullable=True, comment="学校"))
    op.add_column("users", sa.Column("study_status", sa.String(20), nullable=True, comment="在读情况"))
    op.add_column("users", sa.Column("industry", sa.String(50), nullable=True, comment="行业"))
    op.add_column("users", sa.Column("marital_status", sa.String(20), nullable=True, comment="婚姻情况"))
    op.add_column("users", sa.Column("dating_purpose", sa.String(50), nullable=True, comment="交友目的"))
    op.add_column("users", sa.Column("dating_rhythm", sa.String(50), nullable=True, comment="恋爱节奏倾向"))
    op.add_column("users", sa.Column("meeting_scenarios", sa.String(255), nullable=True, comment="喜欢的见面方式场景"))


def downgrade() -> None:
    op.drop_column("users", "meeting_scenarios")
    op.drop_column("users", "dating_rhythm")
    op.drop_column("users", "dating_purpose")
    op.drop_column("users", "marital_status")
    op.drop_column("users", "industry")
    op.drop_column("users", "study_status")
    op.drop_column("users", "school")
    op.drop_column("users", "hometown")
    op.drop_column("users", "mbti")
