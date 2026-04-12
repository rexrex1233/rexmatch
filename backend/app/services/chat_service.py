"""
聊天服务 - 消息发送、历史记录、未读计数、撤回、结构化搜索
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, update

from app.models.match import Match
from app.models.message import Message
from app.models.user import User
from app.models.photo import Photo
from app.schemas.chat import MessageResponse, ChatListItem, SearchChatResponse, SearchContactItem, SearchMessageItem

RECALL_WINDOW_SECONDS = 120  # 2分钟内可撤回


async def send_message(
    db: AsyncSession,
    sender_id: int,
    match_id: int,
    content: str,
    msg_type: str = "text",
    reply_to_id: int | None = None,
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

    if reply_to_id:
        reply_result = await db.execute(
            select(Message).where(Message.id == reply_to_id, Message.match_id == match_id)
        )
        reply_msg = reply_result.scalar_one_or_none()
        if reply_msg and not reply_msg.is_recalled:
            message.reply_to_id = reply_to_id
            message.reply_to_content = reply_msg.content[:200]
            message.reply_to_sender_id = reply_msg.sender_id

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

        user_result = await db.execute(select(User).where(User.id == partner_id))
        partner = user_result.scalar_one_or_none()

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
            partner_nickname=partner.nickname if partner else "未知",
            partner_avatar=avatar.url if avatar else None,
            last_message=last_msg.content if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            unread_count=unread_count,
        ))

    chat_list.sort(key=lambda x: x.last_message_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
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


async def recall_message(db: AsyncSession, user_id: int, message_id: int) -> MessageResponse:
    """撤回消息（2分钟内，仅发送者可撤回）"""
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if msg is None:
        raise ValueError("消息不存在")
    if msg.sender_id != user_id:
        raise ValueError("只能撤回自己发送的消息")
    if msg.is_recalled:
        raise ValueError("消息已撤回")

    now = datetime.now(timezone.utc)
    sent_at = msg.created_at
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    if (now - sent_at).total_seconds() > RECALL_WINDOW_SECONDS:
        raise ValueError("超过2分钟，无法撤回")

    msg.is_recalled = True
    msg.recalled_at = now
    await db.flush()
    return MessageResponse.model_validate(msg)


async def search_chats(db: AsyncSession, user_id: int, keyword: str) -> SearchChatResponse:
    """
    按关键词搜索聊天，返回结构化结果：
    - contacts: 昵称命中的联系人
    - messages: 内容命中的具体消息条目
    """
    if not keyword.strip():
        return SearchChatResponse()

    result = await db.execute(
        select(Match).where(
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        )
    )
    matches = result.scalars().all()

    kw = keyword.strip().lower()
    contacts: list[SearchContactItem] = []
    messages: list[SearchMessageItem] = []

    for match in matches:
        partner_id = match.user2_id if match.user1_id == user_id else match.user1_id

        user_result = await db.execute(select(User).where(User.id == partner_id))
        partner = user_result.scalar_one_or_none()
        nickname = partner.nickname if partner else ""

        avatar_result = await db.execute(
            select(Photo).where(Photo.user_id == partner_id, Photo.is_avatar == True)
        )
        avatar = avatar_result.scalar_one_or_none()
        avatar_url = avatar.url if avatar else None

        # 联系人命中
        if nickname and kw in nickname.lower():
            contacts.append(SearchContactItem(
                match_id=match.id,
                partner_id=partner_id,
                partner_nickname=nickname,
                partner_avatar=avatar_url,
            ))

        # 消息内容命中（返回具体命中的消息，每个对话最多5条）
        msg_result = await db.execute(
            select(Message)
            .where(
                Message.match_id == match.id,
                Message.is_recalled == False,
                Message.msg_type == "text",
            )
            .order_by(Message.created_at.desc())
            .limit(200)
        )
        msgs = msg_result.scalars().all()
        hit_count = 0
        for m in msgs:
            if hit_count >= 5:
                break
            if kw in m.content.lower():
                messages.append(SearchMessageItem(
                    match_id=match.id,
                    partner_id=partner_id,
                    partner_nickname=nickname or "未知",
                    partner_avatar=avatar_url,
                    message_id=m.id,
                    message_content=m.content,
                    message_at=m.created_at,
                ))
                hit_count += 1

    return SearchChatResponse(contacts=contacts, messages=messages)


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
