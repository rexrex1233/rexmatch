"""
匹配 API - 喜欢/跳过、匹配列表
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.match import SwipeRequest, SwipeResponse, MatchResponse
from app.services import match_service

router = APIRouter(prefix="/match", tags=["匹配"])


@router.get("/daily-likes", response_model=ResponseBase[dict])
async def get_daily_likes_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取今日点赞额度信息"""
    used = await match_service.get_daily_like_count(db, current_user.id)
    limit = settings.DAILY_LIKE_LIMIT
    return ResponseBase(data={
        "used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
    })


@router.post("/swipe", response_model=ResponseBase[SwipeResponse])
async def swipe_user(
    req: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """喜欢或跳过用户"""
    if req.is_like:
        daily_count = await match_service.get_daily_like_count(db, current_user.id)
        if daily_count >= settings.DAILY_LIKE_LIMIT:
            raise HTTPException(status_code=429, detail="今日点赞次数已达上限")

    try:
        result = await match_service.swipe(
            db, current_user.id, req.target_user_id, req.is_like
        )
        return ResponseBase(
            data=SwipeResponse(is_match=result["is_match"], match_id=result["match_id"])
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=ResponseBase[list[MatchResponse]])
async def get_match_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我的匹配列表"""
    matches = await match_service.get_matches(db, current_user.id)
    return ResponseBase(data=[MatchResponse(**m) for m in matches])


@router.get("/likes-received", response_model=ResponseBase[list])
async def get_likes_received(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取喜欢了我的用户列表"""
    likes = await match_service.get_likes_received(db, current_user.id)
    return ResponseBase(data=likes)


@router.post("/{match_id}/unmatch", response_model=ResponseBase)
async def unmatch(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解除匹配"""
    success = await match_service.unmatch(db, current_user.id, match_id)
    if not success:
        raise HTTPException(status_code=404, detail="匹配不存在")
    return ResponseBase(message="已解除匹配")
