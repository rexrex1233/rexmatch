"""
统一导出所有 ORM 模型，确保 Alembic 能自动发现
"""
from app.models.user import User
from app.models.photo import Photo
from app.models.interest import Interest, UserInterest
from app.models.swipe import Swipe
from app.models.match import Match
from app.models.message import Message
from app.models.report import Report, Block
from app.models.preference import UserPreference
from app.models.bookmark import Bookmark

__all__ = [
    "User",
    "Photo",
    "Interest",
    "UserInterest",
    "Swipe",
    "Match",
    "Message",
    "Report",
    "Block",
    "UserPreference",
    "Bookmark",
]
