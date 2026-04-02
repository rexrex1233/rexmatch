"""
匹配相关 schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SwipeRequest(BaseModel):
    """滑动操作请求"""
    target_user_id: int
    is_like: bool


class SwipeResponse(BaseModel):
    """滑动操作结果"""
    is_match: bool = False
    match_id: Optional[int] = None


class MatchResponse(BaseModel):
    """匹配信息"""
    match_id: int
    user_id: int
    nickname: str
    avatar_url: Optional[str] = None
    matched_at: datetime
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}
