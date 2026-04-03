"""
用户资料服务 - 资料 CRUD、照片管理、兴趣标签
"""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo
from app.models.interest import Interest, UserInterest
from app.schemas.user import ProfileUpdate, ProfileResponse, PhotoResponse, InterestResponse


def _calc_age(birthday: Optional[date]) -> Optional[int]:
    if birthday is None:
        return None
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


async def get_profile(db: AsyncSession, user_id: int) -> Optional[ProfileResponse]:
    """获取用户完整资料"""
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.interests).selectinload(UserInterest.interest))
        .where(Profile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return None

    photo_result = await db.execute(
        select(Photo).where(Photo.user_id == user_id).order_by(Photo.sort_order)
    )
    photos = photo_result.scalars().all()

    return ProfileResponse(
        user_id=user_id,
        nickname=profile.nickname,
        gender=profile.gender,
        birthday=profile.birthday,
        age=_calc_age(profile.birthday),
        city=profile.city,
        province=profile.province,
        bio=profile.bio,
        height=profile.height,
        weight=profile.weight,
        education=profile.education,
        occupation=profile.occupation,
        income=profile.income,
        is_complete=profile.is_complete,
        photos=[PhotoResponse.model_validate(p) for p in photos],
        interests=[
            InterestResponse(
                id=ui.interest.id,
                name=ui.interest.name,
                category=ui.interest.category,
                icon=ui.interest.icon,
            )
            for ui in profile.interests
        ],
    )


async def update_profile(db: AsyncSession, user_id: int, data: ProfileUpdate) -> ProfileResponse:
    """更新用户资料"""
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise ValueError("用户资料不存在")

    update_data = data.model_dump(exclude_unset=True, exclude={"interest_ids"})
    for field, value in update_data.items():
        setattr(profile, field, value)

    if data.interest_ids is not None:
        await db.execute(
            delete(UserInterest).where(UserInterest.profile_id == profile.id)
        )
        for interest_id in data.interest_ids:
            db.add(UserInterest(profile_id=profile.id, interest_id=interest_id))

    profile.is_complete = _check_profile_complete(profile)
    await db.flush()

    return await get_profile(db, user_id)


def _check_profile_complete(profile: Profile) -> bool:
    """检查资料是否填写完整（至少填写了核心字段）"""
    required = [profile.nickname, profile.gender, profile.birthday, profile.city]
    return all(f is not None and f != 0 for f in required)


async def add_photo(db: AsyncSession, user_id: int, url: str, is_avatar: bool = False) -> Photo:
    """添加用户照片"""
    if is_avatar:
        existing = await db.execute(
            select(Photo).where(Photo.user_id == user_id, Photo.is_avatar == True)
        )
        for p in existing.scalars():
            p.is_avatar = False

    count_result = await db.execute(
        select(Photo).where(Photo.user_id == user_id)
    )
    count = len(count_result.scalars().all())

    photo = Photo(user_id=user_id, url=url, sort_order=count, is_avatar=is_avatar)
    db.add(photo)
    await db.flush()
    return photo


async def delete_photo(db: AsyncSession, user_id: int, photo_id: int) -> bool:
    """删除用户照片"""
    result = await db.execute(
        select(Photo).where(Photo.id == photo_id, Photo.user_id == user_id)
    )
    photo = result.scalar_one_or_none()
    if photo is None:
        return False
    await db.delete(photo)
    await db.flush()
    return True


async def get_all_interests(db: AsyncSession) -> list[Interest]:
    """获取所有预定义兴趣标签"""
    result = await db.execute(select(Interest).order_by(Interest.category, Interest.id))
    return list(result.scalars().all())


async def create_custom_interest(db: AsyncSession, name: str, category: str = "自定义") -> Interest:
    """创建自定义兴趣标签，如果已存在同名则直接返回"""
    result = await db.execute(select(Interest).where(Interest.name == name))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    interest = Interest(name=name, category=category, icon="✨")
    db.add(interest)
    await db.flush()
    return interest
