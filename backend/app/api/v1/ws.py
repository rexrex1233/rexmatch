"""
WebSocket 实时通信端点 - 消息即时推送
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select, or_

from app.core.database import async_session_factory
from app.core.security import decode_access_token
from app.core.redis import set_user_online
from app.models.match import Match
from app.services import chat_service
from app.services.ws_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/chat")
async def ws_chat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket 聊天端点。
    客户端通过 ?token=xxx 查询参数认证。
    消息格式 (JSON):
      发送: {"type": "message", "match_id": 123, "content": "hello", "msg_type": "text"}
      心跳: {"type": "ping"}
      已读: {"type": "read", "match_id": 123}
    """
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(user_id, websocket)
    await set_user_online(user_id, ttl_seconds=600)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await set_user_online(user_id, ttl_seconds=600)
                await websocket.send_json({"type": "pong"})

            elif msg_type == "message":
                match_id = data.get("match_id")
                content = data.get("content", "").strip()
                m_type = data.get("msg_type", "text")
                reply_to_id = data.get("reply_to_id")
                if not match_id or not content:
                    continue

                async with async_session_factory() as db:
                    try:
                        msg_resp = await chat_service.send_message(
                            db, user_id, match_id, content, m_type, reply_to_id
                        )
                        await db.commit()
                    except ValueError as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e),
                        })
                        continue

                    msg_data = {
                        "type": "new_message",
                        "data": {
                            "id": msg_resp.id,
                            "match_id": msg_resp.match_id,
                            "sender_id": msg_resp.sender_id,
                            "content": msg_resp.content,
                            "msg_type": msg_resp.msg_type,
                            "is_read": msg_resp.is_read,
                            "is_recalled": msg_resp.is_recalled,
                            "reply_to_id": msg_resp.reply_to_id,
                            "reply_to_content": msg_resp.reply_to_content,
                            "reply_to_sender_id": msg_resp.reply_to_sender_id,
                            "created_at": msg_resp.created_at.isoformat(),
                        },
                    }
                    await websocket.send_json(msg_data)

                    partner_id = await _get_partner_id(db, match_id, user_id)
                    if partner_id:
                        await manager.send_to_user(partner_id, msg_data)

            elif msg_type == "read":
                match_id = data.get("match_id")
                if match_id:
                    async with async_session_factory() as db:
                        await chat_service.mark_read(db, user_id, match_id)
                        await db.commit()
                        partner_id = await _get_partner_id(db, match_id, user_id)
                        if partner_id:
                            await manager.send_to_user(partner_id, {
                                "type": "read_ack",
                                "match_id": match_id,
                                "reader_id": user_id,
                            })

            elif msg_type == "typing":
                match_id = data.get("match_id")
                if match_id:
                    async with async_session_factory() as db:
                        partner_id = await _get_partner_id(db, match_id, user_id)
                        if partner_id:
                            await manager.send_to_user(partner_id, {
                                "type": "typing",
                                "match_id": match_id,
                                "user_id": user_id,
                            })

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, websocket)


async def _get_partner_id(db, match_id: int, user_id: int) -> int | None:
    result = await db.execute(
        select(Match).where(
            Match.id == match_id,
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        )
    )
    match = result.scalar_one_or_none()
    if match is None:
        return None
    return match.user2_id if match.user1_id == user_id else match.user1_id
