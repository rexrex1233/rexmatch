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
    reply_to_id: Optional[int] = None


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    match_id: int
    sender_id: int
    content: str
    msg_type: str
    is_read: bool
    is_recalled: bool = False
    reply_to_id: Optional[int] = None
    reply_to_content: Optional[str] = None
    reply_to_sender_id: Optional[int] = None
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


# ── 结构化搜索结果 ───────────────────────────────────────────────────────

class SearchContactItem(BaseModel):
    """搜索命中：按联系人昵称匹配"""
    match_id: int
    partner_id: int
    partner_nickname: str
    partner_avatar: Optional[str] = None

class SearchMessageItem(BaseModel):
    """搜索命中：按消息内容匹配"""
    match_id: int
    partner_id: int
    partner_nickname: str
    partner_avatar: Optional[str] = None
    message_id: int
    message_content: str
    message_at: datetime

class SearchChatResponse(BaseModel):
    """结构化搜索结果（联系人 + 聊天记录分组）"""
    contacts: list[SearchContactItem] = []
    messages: list[SearchMessageItem] = []
