"""
推荐服务 - 基于条件筛选推荐候选用户，含契合度计算与智能排序
"""
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
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
    # 只排除普通滑动（re_eligible=False），沉默清理后的用户（re_eligible=True）重新进入候选池
    swiped_subq = select(Swipe.swiped_id).where(
        Swipe.swiper_id == user_id,
        Swipe.re_eligible == False,  # noqa: E712
    )
    # 记录哪些候选人是被沉默清理放回的，用于评分惩罚
    re_eligible_subq = select(Swipe.swiped_id).where(
        Swipe.swiper_id == user_id,
        Swipe.re_eligible == True,  # noqa: E712
    )
    blocked_subq = select(Block.blocked_id).where(Block.blocker_id == user_id)
    blocked_by_subq = select(Block.blocker_id).where(Block.blocked_id == user_id)

    re_eligible_result = await db.execute(re_eligible_subq)
    re_eligible_ids: set[int] = {row[0] for row in re_eligible_result.fetchall()}

    query = (
        select(User)
        .where(
            User.id != user_id,
            User.status == 1,
            User.is_complete == True,
            User.id.not_in(swiped_subq),
            User.id.not_in(blocked_subq),
            User.id.not_in(blocked_by_subq),
        )
    )

    if filters.gender is not None:
        query = query.where(User.gender == filters.gender)

    if filters.city is not None:
        query = query.where(User.city == filters.city)

    if filters.min_age is not None or filters.max_age is not None:
        min_birthday, max_birthday = _age_to_birthday_range(filters.min_age, filters.max_age)
        if min_birthday:
            query = query.where(User.birthday >= min_birthday)
        if max_birthday:
            query = query.where(User.birthday <= max_birthday)

    candidate_limit = max(filters.page_size * 3, 60)
    offset = (filters.page - 1) * filters.page_size
    query = query.order_by(User.updated_at.desc()).limit(candidate_limit)

    result = await db.execute(query)
    users = result.scalars().all()

    now_utc = datetime.now(timezone.utc)
    new_user_cutoff = now_utc - timedelta(days=NEW_USER_BOOST_DAYS)

    scored_cards: list[tuple[float, UserCardResponse]] = []

    for user in users:
        photo_result = await db.execute(
            select(Photo)
            .where(Photo.user_id == user.id)
            .order_by(Photo.sort_order)
        )
        photos = photo_result.scalars().all()

        avatar = next((p for p in photos if p.is_avatar), photos[0] if photos else None)

        interest_result = await db.execute(
            select(UserInterest).where(UserInterest.user_id == user.id)
        )
        user_interests = interest_result.scalars().all()
        interest_names = []
        for ui in user_interests:
            await db.refresh(ui, ["interest"])
            if ui.interest:
                interest_names.append(ui.interest.name)

        today = date.today()
        age = None
        if user.birthday:
            age = today.year - user.birthday.year - (
                (today.month, today.day) < (user.birthday.month, user.birthday.day)
            )

        online = await is_user_online(user.id)

        compat = await calculate_compatibility(
            db, user_id, user, age, interest_names
        )

        all_photo_infos = [
            PhotoInfo(url=p.url, is_avatar=p.is_avatar) for p in photos
        ]

        card = UserCardResponse(
            user_id=user.id,
            nickname=user.nickname or "未知",
            gender=user.gender or 0,
            age=age,
            city=user.city,
            bio=user.bio,
            education=user.education,
            occupation=user.occupation,
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
            has_bio=bool(user.bio),
            user_created=user.created_at,
            user_updated=user.updated_at,
            new_user_cutoff=new_user_cutoff,
            previously_matched=user.id in re_eligible_ids,
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
    user_created: datetime,
    user_updated: datetime,
    new_user_cutoff: datetime,
    previously_matched: bool = False,
) -> float:
    score = 0.0
    score += compat_score * 3.0

    # 沉默清理放回的用户排位靠后
    if previously_matched:
        score -= 40

    if has_photos:
        score += 30
        score += min(photo_count - 1, 4) * 5
    else:
        score -= 20

    if is_online:
        score += 25

    if has_bio:
        score += 10

    created_aware = user_created.replace(tzinfo=timezone.utc) if user_created.tzinfo is None else user_created
    if created_aware > new_user_cutoff:
        score += NEW_USER_BOOST_SCORE

    updated_aware = user_updated.replace(tzinfo=timezone.utc) if user_updated.tzinfo is None else user_updated
    now = datetime.now(timezone.utc)
    hours_since_update = (now - updated_aware).total_seconds() / 3600
    if hours_since_update < 1:
        score += 15
    elif hours_since_update < 24:
        score += 10
    elif hours_since_update < 72:
        score += 5

    return score
