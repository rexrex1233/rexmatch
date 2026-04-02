"""
认证服务 - 微信登录、Token 管理
"""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.profile import Profile


WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def wx_code_to_session(code: str) -> dict:
    """
    调用微信 code2session 接口，获取 openid 和 session_key。
    测试阶段若未配置 APP_ID，返回模拟数据。
    """
    if not settings.WX_APP_ID:
        return {
            "openid": f"test_openid_{code}",
            "session_key": "test_session_key",
        }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            WX_CODE2SESSION_URL,
            params={
                "appid": settings.WX_APP_ID,
                "secret": settings.WX_APP_SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            },
        )
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise ValueError(f"微信登录失败: {data.get('errmsg', '未知错误')}")

    return data


async def login_or_register(db: AsyncSession, code: str) -> tuple[str, bool]:
    """
    微信登录/注册流程：
    1. 通过 code 换取 openid
    2. 查找或创建用户
    3. 签发 JWT token
    返回 (access_token, is_new_user)
    """
    wx_data = await wx_code_to_session(code)
    openid = wx_data["openid"]

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    is_new_user = False

    if user is None:
        is_new_user = True
        user = User(openid=openid)
        db.add(user)
        await db.flush()

        profile = Profile(
            user_id=user.id,
            nickname=f"用户{user.id}",
            gender=0,
        )
        db.add(profile)
        await db.flush()

    access_token = create_access_token(user.id)
    return access_token, is_new_user
