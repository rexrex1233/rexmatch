"""
聊天相关 schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    match_id: int
    content: str = Field(..., min_length=1, max_length=2000)
    msg_type: str = Field(default="text", pattern="^(text|image|system)$")


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    match_id: int
    sender_id: int
    content: str
    msg_type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatListItem(BaseModel):
    """聊天列表项"""
    match_id: int
    partner_id: int
    partner_nickname: str
    partner_avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
