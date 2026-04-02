"""
偏好服务 - 管理用户择偶偏好，计算契合度
"""
import json
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.preference import UserPreference
from app.models.profile import Profile
from app.models.interest import UserInterest
from app.schemas.preference import PreferenceUpdate, PreferenceResponse, CompatibilityInfo


async def get_preference(db: AsyncSession, user_id: int) -> Optional[PreferenceResponse]:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        return PreferenceResponse()

    tags = []
    if pref.personality_tags:
        try:
            tags = json.loads(pref.personality_tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    return PreferenceResponse(
        preferred_gender=pref.preferred_gender,
        min_age=pref.min_age,
        max_age=pref.max_age,
        preferred_city=pref.preferred_city,
        preferred_education=pref.preferred_education,
        personality_tags=tags,
    )


async def update_preference(db: AsyncSession, user_id: int, data: PreferenceUpdate) -> PreferenceResponse:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()

    tags_json = json.dumps(data.personality_tags or [], ensure_ascii=False) if data.personality_tags is not None else None

    if pref is None:
        pref = UserPreference(user_id=user_id)
        db.add(pref)

    if data.preferred_gender is not None:
        pref.preferred_gender = data.preferred_gender
    if data.min_age is not None:
        pref.min_age = data.min_age
    if data.max_age is not None:
        pref.max_age = data.max_age
    if data.preferred_city is not None:
        pref.preferred_city = data.preferred_city
    if data.preferred_education is not None:
        pref.preferred_education = data.preferred_education
    if tags_json is not None:
        pref.personality_tags = tags_json

    await db.flush()
    await db.refresh(pref)

    parsed_tags = []
    if pref.personality_tags:
        try:
            parsed_tags = json.loads(pref.personality_tags)
        except (json.JSONDecodeError, TypeError):
            pass

    return PreferenceResponse(
        preferred_gender=pref.preferred_gender,
        min_age=pref.min_age,
        max_age=pref.max_age,
        preferred_city=pref.preferred_city,
        preferred_education=pref.preferred_education,
        personality_tags=parsed_tags,
    )


async def calculate_compatibility(
    db: AsyncSession,
    viewer_id: int,
    target_profile: Profile,
    target_age: Optional[int],
    target_interest_names: list[str],
) -> CompatibilityInfo:
    """计算 viewer 对 target 的契合度"""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == viewer_id)
    )
    pref = result.scalar_one_or_none()

    if pref is None:
        return CompatibilityInfo(score=len(target_interest_names), shared_interests=target_interest_names[:3])

    matched = []

    if pref.preferred_gender and target_profile.gender == pref.preferred_gender:
        gender_label = "男生" if target_profile.gender == 1 else "女生"
        matched.append(f"性别: {gender_label}")

    if target_age and pref.min_age and pref.max_age:
        if pref.min_age <= target_age <= pref.max_age:
            matched.append(f"年龄: {target_age}岁")

    if pref.preferred_city and target_profile.city:
        if pref.preferred_city == target_profile.city:
            matched.append(f"城市: {target_profile.city}")

    if pref.preferred_education and target_profile.education:
        if pref.preferred_education == target_profile.education:
            matched.append(f"学历: {target_profile.education}")

    viewer_interests_result = await db.execute(
        select(UserInterest).where(
            UserInterest.profile_id == (
                await db.execute(select(Profile.id).where(Profile.user_id == viewer_id))
            ).scalar()
        )
    )
    viewer_uis = viewer_interests_result.scalars().all()
    viewer_interest_names = set()
    for ui in viewer_uis:
        await db.refresh(ui, ["interest"])
        if ui.interest:
            viewer_interest_names.add(ui.interest.name)

    shared = list(viewer_interest_names & set(target_interest_names))

    pref_tags = []
    if pref.personality_tags:
        try:
            pref_tags = json.loads(pref.personality_tags)
        except (json.JSONDecodeError, TypeError):
            pass

    for tag in pref_tags:
        if tag in target_interest_names:
            matched.append(tag)

    total_score = len(matched) + len(shared)

    return CompatibilityInfo(
        score=total_score,
        matched_preferences=matched,
        shared_interests=shared[:5],
    )
