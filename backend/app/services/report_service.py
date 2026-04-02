"""
举报与拉黑服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.report import Report, Block


async def create_report(
    db: AsyncSession,
    reporter_id: int,
    reported_id: int,
    reason: str,
    detail: str | None = None,
) -> Report:
    """创建举报记录"""
    if reporter_id == reported_id:
        raise ValueError("不能举报自己")

    report = Report(
        reporter_id=reporter_id,
        reported_id=reported_id,
        reason=reason,
        detail=detail,
    )
    db.add(report)
    await db.flush()
    return report


async def block_user(db: AsyncSession, blocker_id: int, blocked_id: int) -> Block:
    """拉黑用户"""
    if blocker_id == blocked_id:
        raise ValueError("不能拉黑自己")

    existing = await db.execute(
        select(Block).where(
            Block.blocker_id == blocker_id,
            Block.blocked_id == blocked_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("已经拉黑该用户")

    block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
    db.add(block)
    await db.flush()
    return block


async def get_block_list(db: AsyncSession, user_id: int) -> list[dict]:
    """获取黑名单列表"""
    from app.models.profile import Profile
    from app.models.photo import Photo

    result = await db.execute(
        select(Block).where(Block.blocker_id == user_id).order_by(Block.created_at.desc())
    )
    blocks = result.scalars().all()

    items = []
    for b in blocks:
        profile_r = await db.execute(select(Profile).where(Profile.user_id == b.blocked_id))
        profile = profile_r.scalar_one_or_none()
        avatar_r = await db.execute(
            select(Photo).where(Photo.user_id == b.blocked_id, Photo.is_avatar == True)
        )
        avatar = avatar_r.scalar_one_or_none()
        items.append({
            "user_id": b.blocked_id,
            "nickname": profile.nickname if profile else "未知用户",
            "avatar_url": avatar.url if avatar else None,
            "blocked_at": b.created_at,
        })
    return items


async def unblock_user(db: AsyncSession, blocker_id: int, blocked_id: int) -> bool:
    """取消拉黑"""
    result = await db.execute(
        select(Block).where(
            Block.blocker_id == blocker_id,
            Block.blocked_id == blocked_id,
        )
    )
    block = result.scalar_one_or_none()
    if block is None:
        return False
    await db.delete(block)
    await db.flush()
    return True
