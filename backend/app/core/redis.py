"""
Redis 连接管理 - 可选依赖，未配置时优雅降级
用途：用户在线状态、每日点赞计数缓存、推荐队列缓存
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None
_redis_available = False


async def get_redis():
    """获取 Redis 客户端，不可用时返回 None"""
    global _redis_client, _redis_available

    if _redis_client is not None:
        return _redis_client if _redis_available else None

    if not settings.REDIS_URL:
        _redis_available = False
        return None

    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis 连接成功")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis 不可用，降级到数据库查询: {e}")
        _redis_available = False
        return None


async def close_redis():
    global _redis_client, _redis_available
    if _redis_client and _redis_available:
        await _redis_client.close()
    _redis_client = None
    _redis_available = False


# ---- 在线状态 ----

async def set_user_online(user_id: int, ttl_seconds: int = 300):
    """标记用户在线，默认 5 分钟过期"""
    r = await get_redis()
    if r:
        await r.setex(f"online:{user_id}", ttl_seconds, "1")


async def is_user_online(user_id: int) -> bool:
    r = await get_redis()
    if r:
        return await r.exists(f"online:{user_id}") > 0
    return False


async def get_online_users(user_ids: list[int]) -> set[int]:
    """批量查询哪些用户在线"""
    r = await get_redis()
    if not r or not user_ids:
        return set()
    pipe = r.pipeline()
    for uid in user_ids:
        pipe.exists(f"online:{uid}")
    results = await pipe.execute()
    return {uid for uid, exists in zip(user_ids, results) if exists}


# ---- 每日点赞计数 ----

async def incr_daily_like(user_id: int) -> Optional[int]:
    """增加今日点赞计数，返回当前值；Redis 不可用时返回 None（由调用方降级到数据库）"""
    r = await get_redis()
    if not r:
        return None
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    key = f"likes:{user_id}:{today}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 86400)
    return count


async def get_daily_like_count_cached(user_id: int) -> Optional[int]:
    """获取今日点赞计数缓存；Redis 不可用时返回 None"""
    r = await get_redis()
    if not r:
        return None
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    key = f"likes:{user_id}:{today}"
    val = await r.get(key)
    return int(val) if val else 0
