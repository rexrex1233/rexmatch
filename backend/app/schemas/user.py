"""
用户资料相关 schemas
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    """更新用户资料请求"""
    nickname: Optional[str] = Field(None, max_length=50)
    gender: Optional[int] = Field(None, ge=1, le=2)
    birthday: Optional[date] = None
    city: Optional[str] = Field(None, max_length=50)
    province: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    height: Optional[int] = Field(None, ge=100, le=250)
    weight: Optional[int] = Field(None, ge=30, le=200)
    education: Optional[str] = Field(None, max_length=20)
    occupation: Optional[str] = Field(None, max_length=50)
    income: Optional[str] = Field(None, max_length=30)
    interest_ids: Optional[list[int]] = Field(None, max_length=10)


class ProfileResponse(BaseModel):
    """用户资料响应"""
    user_id: int
    nickname: str
    gender: int
    birthday: Optional[date] = None
    age: Optional[int] = None
    city: Optional[str] = None
    province: Optional[str] = None
    bio: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[str] = None
    photos: list["PhotoResponse"] = []
    interests: list["InterestResponse"] = []
    is_complete: bool = False

    model_config = {"from_attributes": True}


class PhotoResponse(BaseModel):
    """照片响应"""
    id: int
    url: str
    sort_order: int
    is_avatar: bool

    model_config = {"from_attributes": True}


class InterestCreate(BaseModel):
    """创建自定义兴趣标签"""
    name: str = Field(..., min_length=1, max_length=20)
    category: str = Field("自定义", max_length=20)


class InterestResponse(BaseModel):
    """兴趣标签响应"""
    id: int
    name: str
    category: str
    icon: Optional[str] = None

    model_config = {"from_attributes": True}


class PhotoInfo(BaseModel):
    """照片信息（用于推荐卡片）"""
    url: str
    is_avatar: bool = False


class UserCardResponse(BaseModel):
    """推荐卡片：用于发现页展示的用户信息"""
    user_id: int
    nickname: str
    gender: int
    age: Optional[int] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    avatar_url: Optional[str] = None
    photos: list[str] = []
    all_photos: list[PhotoInfo] = []
    interests: list[str] = []
    is_online: bool = False
    compatibility: Optional["CompatibilityInfo"] = None
    distance: Optional[float] = None

    model_config = {"from_attributes": True}


from app.schemas.preference import CompatibilityInfo  # noqa: E402
