"""
发现页 API - 推荐用户列表
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.discover import DiscoverFilter
from app.schemas.user import UserCardResponse
from app.services import recommend_service

router = APIRouter(prefix="/discover", tags=["发现"])


@router.get("/recommend", response_model=ResponseBase[list[UserCardResponse]])
async def get_recommendations(
    gender: int | None = Query(None, ge=1, le=2),
    min_age: int | None = Query(None, ge=18, le=80),
    max_age: int | None = Query(None, ge=18, le=80),
    city: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取推荐用户列表"""
    filters = DiscoverFilter(
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        city=city,
        page=page,
        page_size=page_size,
    )
    cards = await recommend_service.get_recommendations(db, current_user.id, filters)
    return ResponseBase(data=cards)
