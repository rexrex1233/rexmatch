"""
聊天 API - 消息收发、聊天列表
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.chat import SendMessageRequest, MessageResponse, ChatListItem
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.get("/list", response_model=ResponseBase[list[ChatListItem]])
async def get_chat_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取聊天列表"""
    chats = await chat_service.get_chat_list(db, current_user.id)
    return ResponseBase(data=chats)


@router.get("/{match_id}/messages", response_model=ResponseBase[list[MessageResponse]])
async def get_messages(
    match_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取聊天历史消息"""
    try:
        messages = await chat_service.get_messages(
            db, current_user.id, match_id, page, page_size
        )
        return ResponseBase(data=messages)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/send", response_model=ResponseBase[MessageResponse])
async def send_message(
    req: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息"""
    try:
        message = await chat_service.send_message(
            db, current_user.id, req.match_id, req.content, req.msg_type
        )
        return ResponseBase(data=message)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
