"""
认证相关 schemas
"""
from pydantic import BaseModel


class WxLoginRequest(BaseModel):
    """微信小程序登录请求"""
    code: str


class TokenResponse(BaseModel):
    """登录成功返回的 token"""
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class PhoneBindRequest(BaseModel):
    """绑定手机号（微信获取手机号）"""
    encrypted_data: str
    iv: str
