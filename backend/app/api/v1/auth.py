"""
认证 API - 微信登录
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import WxLoginRequest, TokenResponse
from app.schemas.common import ResponseBase
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/wx-login", response_model=ResponseBase[TokenResponse])
async def wx_login(req: WxLoginRequest, db: AsyncSession = Depends(get_db)):
    """微信小程序登录"""
    try:
        access_token, is_new_user = await auth_service.login_or_register(db, req.code)
        return ResponseBase(
            data=TokenResponse(
                access_token=access_token,
                is_new_user=is_new_user,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
