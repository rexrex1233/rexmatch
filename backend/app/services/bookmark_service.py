"""
收藏服务 - 稍后再看
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.bookmark import Bookmark
from app.models.user import User
from app.models.photo import Photo
from app.schemas.user import UserCardResponse, PhotoInfo
from datetime import date


async def add_bookmark(db: AsyncSession, user_id: int, target_user_id: int) -> bool:
    """收藏用户，已存在则忽略"""
    if user_id == target_user_id:
        return False
    existing = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.bookmarked_user_id == target_user_id,
        )
    )
    if existing.scalar_one_or_none():
        return True

    db.add(Bookmark(user_id=user_id, bookmarked_user_id=target_user_id))
    await db.flush()
    return True


async def remove_bookmark(db: AsyncSession, user_id: int, target_user_id: int) -> bool:
    """取消收藏"""
    result = await db.execute(
        delete(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.bookmarked_user_id == target_user_id,
        )
    )
    await db.flush()
    return result.rowcount > 0


async def get_bookmarks(db: AsyncSession, user_id: int) -> list[UserCardResponse]:
    """获取收藏列表（返回用户卡片格式）"""
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
    )
    bookmarks = result.scalars().all()

    cards = []
    today = date.today()
    for bm in bookmarks:
        user_res = await db.execute(select(User).where(User.id == bm.bookmarked_user_id))
        user = user_res.scalar_one_or_none()
        if not user or not user.nickname:
            continue

        photo_res = await db.execute(
            select(Photo)
            .where(Photo.user_id == bm.bookmarked_user_id)
            .order_by(Photo.sort_order)
        )
        photos = photo_res.scalars().all()
        avatar = next((p for p in photos if p.is_avatar), photos[0] if photos else None)

        age = None
        if user.birthday:
            age = today.year - user.birthday.year - (
                (today.month, today.day) < (user.birthday.month, user.birthday.day)
            )

        cards.append(UserCardResponse(
            user_id=user.id,
            nickname=user.nickname,
            gender=user.gender or 0,
            age=age,
            city=user.city,
            bio=user.bio,
            education=user.education,
            occupation=user.occupation,
            avatar_url=avatar.url if avatar else None,
            photos=[p.url for p in photos],
            all_photos=[PhotoInfo(url=p.url, is_avatar=p.is_avatar) for p in photos],
            interests=[],
            is_online=False,
        ))

    return cards


async def is_bookmarked(db: AsyncSession, user_id: int, target_user_id: int) -> bool:
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.bookmarked_user_id == target_user_id,
        )
    )
    return result.scalar_one_or_none() is not None
