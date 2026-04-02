"""
WebSocket 连接管理器 - 维护在线用户的 WS 连接池
"""
import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """管理所有活跃的 WebSocket 连接，支持单用户多设备"""

    def __init__(self):
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)
        logger.info(f"WS connected: user={user_id}, total_conns={self.total_connections}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self._connections:
            try:
                self._connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info(f"WS disconnected: user={user_id}, total_conns={self.total_connections}")

    async def send_to_user(self, user_id: int, message: dict[str, Any]):
        """向指定用户的所有连接发送消息"""
        conns = self._connections.get(user_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def broadcast(self, message: dict[str, Any], exclude: int | None = None):
        for uid, conns in list(self._connections.items()):
            if uid == exclude:
                continue
            await self.send_to_user(uid, message)

    def is_online(self, user_id: int) -> bool:
        return user_id in self._connections and len(self._connections[user_id]) > 0

    @property
    def total_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())

    @property
    def online_user_count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
