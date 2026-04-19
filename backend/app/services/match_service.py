"""
匹配服务 - 喜欢/跳过、双向匹配检测、批量解除
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import date, datetime, timezone

from app.models.swipe import Swipe
from app.models.match import Match
from app.models.user import User
from app.models.photo import Photo
from app.models.report import Block
from app.core.config import settings


async def swipe(db: AsyncSession, swiper_id: int, swiped_id: int, is_like: bool) -> dict:
    """
    处理滑动操作：
    1. 记录 swipe
    2. 如果是 like，检查对方是否也 like 了我 -> 若是则创建 match
    返回 {"is_match": bool, "match_id": int | None}
    """
    if swiper_id == swiped_id:
        raise ValueError("不能对自己操作")

    target = await db.execute(select(User).where(User.id == swiped_id))
    if target.scalar_one_or_none() is None:
        raise ValueError("目标用户不存在")

    existing = await db.execute(
        select(Swipe).where(
            Swipe.swiper_id == swiper_id,
            Swipe.swiped_id == swiped_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("已经操作过该用户")

    new_swipe = Swipe(swiper_id=swiper_id, swiped_id=swiped_id, is_like=is_like)
    db.add(new_swipe)
    await db.flush()

    if not is_like:
        return {"is_match": False, "match_id": None}

    reverse = await db.execute(
        select(Swipe).where(
            Swipe.swiper_id == swiped_id,
            Swipe.swiped_id == swiper_id,
            Swipe.is_like == True,
        )
    )

    if reverse.scalar_one_or_none() is None:
        return {"is_match": False, "match_id": None}

    user1_id = min(swiper_id, swiped_id)
    user2_id = max(swiper_id, swiped_id)
    match = Match(user1_id=user1_id, user2_id=user2_id)
    db.add(match)
    await db.flush()

    return {"is_match": True, "match_id": match.id}


async def get_daily_like_count(db: AsyncSession, user_id: int) -> int:
    """获取今日已点赞次数（优先 Redis 缓存，降级到数据库）"""
    from app.core.redis import get_daily_like_count_cached
    cached = await get_daily_like_count_cached(user_id)
    if cached is not None:
        return cached

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count()).select_from(Swipe).where(
            Swipe.swiper_id == user_id,
            Swipe.is_like == True,
            Swipe.created_at >= today_start,
        )
    )
    return result.scalar() or 0


async def get_matches(db: AsyncSession, user_id: int) -> list[dict]:
    """获取用户的所有有效匹配"""
    result = await db.execute(
        select(Match).where(
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        ).order_by(Match.matched_at.desc())
    )
    matches = result.scalars().all()

    match_list = []
    for m in matches:
        partner_id = m.user2_id if m.user1_id == user_id else m.user1_id

        user_result = await db.execute(select(User).where(User.id == partner_id))
        partner = user_result.scalar_one_or_none()

        avatar_result = await db.execute(
            select(Photo).where(Photo.user_id == partner_id, Photo.is_avatar == True)
        )
        avatar = avatar_result.scalar_one_or_none()

        match_list.append({
            "match_id": m.id,
            "user_id": partner_id,
            "nickname": partner.nickname if partner else "未知",
            "avatar_url": avatar.url if avatar else None,
            "matched_at": m.matched_at,
        })

    return match_list


async def get_likes_received(db: AsyncSession, user_id: int) -> list[dict]:
    """获取喜欢了我的用户列表（排除已回滑和已拉黑）"""
    swiped_back_subq = select(Swipe.swiped_id).where(Swipe.swiper_id == user_id)
    blocked_subq = select(Block.blocked_id).where(Block.blocker_id == user_id)
    blocked_by_subq = select(Block.blocker_id).where(Block.blocked_id == user_id)

    result = await db.execute(
        select(Swipe).where(
            Swipe.swiped_id == user_id,
            Swipe.is_like == True,
            Swipe.swiper_id.not_in(swiped_back_subq),
            Swipe.swiper_id.not_in(blocked_subq),
            Swipe.swiper_id.not_in(blocked_by_subq),
        ).order_by(Swipe.created_at.desc())
    )
    swipes = result.scalars().all()

    likes = []
    for s in swipes:
        user_result = await db.execute(select(User).where(User.id == s.swiper_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.nickname:
            continue

        photo_result = await db.execute(
            select(Photo).where(Photo.user_id == s.swiper_id, Photo.is_avatar == True)
        )
        avatar = photo_result.scalar_one_or_none()
        if not avatar:
            photo_result2 = await db.execute(
                select(Photo).where(Photo.user_id == s.swiper_id).order_by(Photo.sort_order).limit(1)
            )
            avatar = photo_result2.scalar_one_or_none()

        from datetime import date as _date
        today = _date.today()
        age = None
        if user.birthday:
            age = today.year - user.birthday.year - (
                (today.month, today.day) < (user.birthday.month, user.birthday.day)
            )

        likes.append({
            "user_id": s.swiper_id,
            "nickname": user.nickname,
            "gender": user.gender,
            "age": age,
            "city": user.city,
            "avatar_url": avatar.url if avatar else None,
            "liked_at": s.created_at,
        })

    return likes


async def unmatch(db: AsyncSession, user_id: int, match_id: int) -> bool:
    """解除匹配"""
    result = await db.execute(
        select(Match).where(
            Match.id == match_id,
            Match.status == 1,
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
        )
    )
    match = result.scalar_one_or_none()
    if match is None:
        return False

    match.status = 0
    await db.flush()
    return True


async def batch_unmatch(db: AsyncSession, user_id: int, match_ids: list[int]) -> int:
    """批量解除匹配，返回成功解除数量"""
    count = 0
    for match_id in match_ids:
        if await unmatch(db, user_id, match_id):
            count += 1
    return count


async def inactive_unmatch_batch(db: AsyncSession, user_id: int, match_ids: list[int]) -> int:
    """
    沉默清理：解除匹配并将双方 Swipe 记录标记为 re_eligible=True，
    使对方可重新出现在推荐池（但排分降低）。
    返回成功处理的数量。
    """
    from sqlalchemy import update as sa_update

    count = 0
    for match_id in match_ids:
        result = await db.execute(
            select(Match).where(
                Match.id == match_id,
                Match.status == 1,
                or_(Match.user1_id == user_id, Match.user2_id == user_id),
            )
        )
        match = result.scalar_one_or_none()
        if match is None:
            continue

        partner_id = match.user2_id if match.user1_id == user_id else match.user1_id

        match.status = 0

        # 双方 Swipe 记录均标记为可再推荐
        await db.execute(
            sa_update(Swipe)
            .where(
                or_(
                    and_(Swipe.swiper_id == user_id, Swipe.swiped_id == partner_id),
                    and_(Swipe.swiper_id == partner_id, Swipe.swiped_id == user_id),
                )
            )
            .values(re_eligible=True)
        )
        await db.flush()
        count += 1

    return count
