"""
推荐服务 - 基于条件筛选推荐候选用户，含契合度计算与智能排序
"""
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo
from app.models.interest import UserInterest
from app.models.swipe import Swipe
from app.models.report import Block
from app.schemas.discover import DiscoverFilter
from app.schemas.user import UserCardResponse, PhotoInfo
from app.core.redis import is_user_online
from app.services.preference_service import calculate_compatibility

NEW_USER_BOOST_DAYS = 7
NEW_USER_BOOST_SCORE = 20


def _age_to_birthday_range(min_age: Optional[int], max_age: Optional[int]) -> tuple:
    today = date.today()
    min_birthday = None
    max_birthday = None

    if max_age is not None:
        min_birthday = today.replace(year=today.year - max_age - 1)
    if min_age is not None:
        max_birthday = today.replace(year=today.year - min_age)

    return min_birthday, max_birthday


async def get_recommendations(
    db: AsyncSession,
    user_id: int,
    filters: DiscoverFilter,
) -> list[UserCardResponse]:
    swiped_subq = select(Swipe.swiped_id).where(Swipe.swiper_id == user_id)
    blocked_subq = select(Block.blocked_id).where(Block.blocker_id == user_id)
    blocked_by_subq = select(Block.blocker_id).where(Block.blocked_id == user_id)

    query = (
        select(Profile)
        .join(User, User.id == Profile.user_id)
        .where(
            Profile.user_id != user_id,
            User.status == 1,
            Profile.is_complete == True,
            Profile.user_id.not_in(swiped_subq),
            Profile.user_id.not_in(blocked_subq),
            Profile.user_id.not_in(blocked_by_subq),
        )
    )

    if filters.gender is not None:
        query = query.where(Profile.gender == filters.gender)

    if filters.city is not None:
        query = query.where(Profile.city == filters.city)

    if filters.min_age is not None or filters.max_age is not None:
        min_birthday, max_birthday = _age_to_birthday_range(filters.min_age, filters.max_age)
        if min_birthday:
            query = query.where(Profile.birthday >= min_birthday)
        if max_birthday:
            query = query.where(Profile.birthday <= max_birthday)

    # Fetch larger candidate pool for scoring-based reranking
    candidate_limit = max(filters.page_size * 3, 60)
    offset = (filters.page - 1) * filters.page_size
    query = query.order_by(Profile.updated_at.desc()).limit(candidate_limit)

    result = await db.execute(query)
    profiles = result.scalars().all()

    now_utc = datetime.now(timezone.utc)
    new_user_cutoff = now_utc - timedelta(days=NEW_USER_BOOST_DAYS)

    scored_cards: list[tuple[float, UserCardResponse]] = []

    for profile in profiles:
        photo_result = await db.execute(
            select(Photo)
            .where(Photo.user_id == profile.user_id)
            .order_by(Photo.sort_order)
        )
        photos = photo_result.scalars().all()

        avatar = next((p for p in photos if p.is_avatar), photos[0] if photos else None)

        interest_result = await db.execute(
            select(UserInterest)
            .where(UserInterest.profile_id == profile.id)
        )
        user_interests = interest_result.scalars().all()
        interest_names = []
        for ui in user_interests:
            await db.refresh(ui, ["interest"])
            if ui.interest:
                interest_names.append(ui.interest.name)

        today = date.today()
        age = None
        if profile.birthday:
            age = today.year - profile.birthday.year - (
                (today.month, today.day) < (profile.birthday.month, profile.birthday.day)
            )

        online = await is_user_online(profile.user_id)

        compat = await calculate_compatibility(
            db, user_id, profile, age, interest_names
        )

        all_photo_infos = [
            PhotoInfo(url=p.url, is_avatar=p.is_avatar) for p in photos
        ]

        card = UserCardResponse(
            user_id=profile.user_id,
            nickname=profile.nickname,
            gender=profile.gender,
            age=age,
            city=profile.city,
            bio=profile.bio,
            education=profile.education,
            occupation=profile.occupation,
            avatar_url=avatar.url if avatar else None,
            photos=[p.url for p in photos],
            all_photos=all_photo_infos,
            interests=interest_names,
            is_online=online,
            compatibility=compat,
        )

        rank_score = _compute_rank_score(
            compat_score=compat.score if compat else 0,
            has_photos=len(photos) > 0,
            photo_count=len(photos),
            is_online=online,
            has_bio=bool(profile.bio),
            profile_created=profile.created_at,
            profile_updated=profile.updated_at,
            new_user_cutoff=new_user_cutoff,
        )

        scored_cards.append((rank_score, card))

    scored_cards.sort(key=lambda x: x[0], reverse=True)

    start = offset
    end = offset + filters.page_size
    return [card for _, card in scored_cards[start:end]]


def _compute_rank_score(
    *,
    compat_score: int,
    has_photos: bool,
    photo_count: int,
    is_online: bool,
    has_bio: bool,
    profile_created: datetime,
    profile_updated: datetime,
    new_user_cutoff: datetime,
) -> float:
    """
    综合排序分数，权重:
    - 契合度 (0-100): 权重 3.0
    - 有照片: +30, 每多一张 +5 (上限 +50)
    - 在线: +25
    - 有简介: +10
    - 新用户加速 (注册 7 天内): +20
    - 活跃度 (最近更新): +0~15
    """
    score = 0.0

    score += compat_score * 3.0

    if has_photos:
        score += 30
        score += min(photo_count - 1, 4) * 5
    else:
        score -= 20

    if is_online:
        score += 25

    if has_bio:
        score += 10

    created_aware = profile_created.replace(tzinfo=timezone.utc) if profile_created.tzinfo is None else profile_created
    if created_aware > new_user_cutoff:
        score += NEW_USER_BOOST_SCORE

    updated_aware = profile_updated.replace(tzinfo=timezone.utc) if profile_updated.tzinfo is None else profile_updated
    now = datetime.now(timezone.utc)
    hours_since_update = (now - updated_aware).total_seconds() / 3600
    if hours_since_update < 1:
        score += 15
    elif hours_since_update < 24:
        score += 10
    elif hours_since_update < 72:
        score += 5

    return score
