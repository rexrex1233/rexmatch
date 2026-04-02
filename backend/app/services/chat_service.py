"""
聊天服务 - 消息发送、历史记录、未读计数
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, update

from app.models.match import Match
from app.models.message import Message
from app.models.profile import Profile
from app.models.photo import Photo
from app.schemas.chat import MessageResponse, ChatListItem


async def send_message(
    db: AsyncSession,
    sender_id: int,
    match_id: int,
    content: str,
    msg_type: str = "text",
) -> MessageResponse:
    """发送消息（需校验 sender 是 match 的参与者）"""
    match = await _verify_match_participant(db, match_id, sender_id)
    if match is None:
        raise ValueError("无权在此对话中发送消息")

    message = Message(
        match_id=match_id,
        sender_id=sender_id,
        content=content,
        msg_type=msg_type,
    )
    db.add(message)
    await db.flush()

    return MessageResponse.model_validate(message)


async def get_messages(
    db: AsyncSession,
    user_id: int,
    match_id: int,
    page: int = 1,
    page_size: int = 50,
) -> list[MessageResponse]:
    """获取聊天历史（分页，最新的在前）"""
    match = await _verify_match_participant(db, match_id, user_id)
    if match is None:
        raise ValueError("无权查看此对话")

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Message)
        .where(Message.match_id == match_id)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    messages = result.scalars().all()

    await db.execute(
        update(Message)
        .where(
            Message.match_id == match_id,
            Message.sender_id != user_id,
            Message.is_read == False,
        )
        .values(is_read=True)
    )
    await db.flush()

    return [MessageResponse.model_validate(m) for m in reversed(messages)]


async def get_chat_list(db: AsyncSession, user_id: int) -> list[ChatListItem]:
    """获取聊天列表（有匹配关系的对话）"""
    result = await db.execute(
        select(Match).where(
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        ).order_by(Match.matched_at.desc())
    )
    matches = result.scalars().all()

    chat_list = []
    for match in matches:
        partner_id = match.user2_id if match.user1_id == user_id else match.user1_id

        profile_result = await db.execute(
            select(Profile).where(Profile.user_id == partner_id)
        )
        partner_profile = profile_result.scalar_one_or_none()

        avatar_result = await db.execute(
            select(Photo).where(Photo.user_id == partner_id, Photo.is_avatar == True)
        )
        avatar = avatar_result.scalar_one_or_none()

        last_msg_result = await db.execute(
            select(Message)
            .where(Message.match_id == match.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()

        unread_result = await db.execute(
            select(func.count()).select_from(Message).where(
                Message.match_id == match.id,
                Message.sender_id != user_id,
                Message.is_read == False,
            )
        )
        unread_count = unread_result.scalar() or 0

        chat_list.append(ChatListItem(
            match_id=match.id,
            partner_id=partner_id,
            partner_nickname=partner_profile.nickname if partner_profile else "未知",
            partner_avatar=avatar.url if avatar else None,
            last_message=last_msg.content if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            unread_count=unread_count,
        ))

    chat_list.sort(key=lambda x: x.last_message_at or match.matched_at, reverse=True)
    return chat_list


async def mark_read(db: AsyncSession, user_id: int, match_id: int):
    """标记某个对话中对方发送的消息为已读"""
    await db.execute(
        update(Message)
        .where(
            Message.match_id == match_id,
            Message.sender_id != user_id,
            Message.is_read == False,
        )
        .values(is_read=True)
    )
    await db.flush()


async def _verify_match_participant(db: AsyncSession, match_id: int, user_id: int) -> Match | None:
    """验证用户是否为匹配对话的参与者"""
    result = await db.execute(
        select(Match).where(
            Match.id == match_id,
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        )
    )
    return result.scalar_one_or_none()
