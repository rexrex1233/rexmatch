"""
用户资料 API - 个人信息 CRUD、照片管理、兴趣标签
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.user import ProfileUpdate, ProfileResponse, PhotoResponse, InterestResponse, InterestCreate
from app.schemas.preference import PreferenceUpdate, PreferenceResponse
from app.services import user_service
from app.services import preference_service

router = APIRouter(prefix="/users", tags=["用户资料"])


@router.get("/me", response_model=ResponseBase[ProfileResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户资料"""
    profile = await user_service.get_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="资料不存在")
    return ResponseBase(data=profile)


@router.get("/{user_id}", response_model=ResponseBase[ProfileResponse])
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看其他用户的资料"""
    profile = await user_service.get_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseBase(data=profile)


@router.put("/me", response_model=ResponseBase[ProfileResponse])
async def update_my_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户资料"""
    try:
        profile = await user_service.update_profile(db, current_user.id, data)
        return ResponseBase(data=profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/photos", response_model=ResponseBase[PhotoResponse])
async def upload_photo(
    photo_url: str,
    is_avatar: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    添加照片（前端先上传到 COS 获取 URL，再传给此接口）。
    后续可改为直接上传文件到后端再转存 COS。
    """
    photo = await user_service.add_photo(db, current_user.id, photo_url, is_avatar)
    return ResponseBase(data=PhotoResponse.model_validate(photo))


@router.delete("/me/photos/{photo_id}", response_model=ResponseBase)
async def remove_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除照片"""
    success = await user_service.delete_photo(db, current_user.id, photo_id)
    if not success:
        raise HTTPException(status_code=404, detail="照片不存在")
    return ResponseBase(message="删除成功")


@router.get("/me/preferences", response_model=ResponseBase[PreferenceResponse])
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我的择偶偏好"""
    pref = await preference_service.get_preference(db, current_user.id)
    return ResponseBase(data=pref)


@router.put("/me/preferences", response_model=ResponseBase[PreferenceResponse])
async def update_my_preferences(
    data: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新我的择偶偏好"""
    pref = await preference_service.update_preference(db, current_user.id, data)
    return ResponseBase(data=pref)


@router.get("/check-nickname", response_model=ResponseBase[dict])
async def check_nickname(
    nickname: str = Query(..., min_length=2, max_length=12),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """检查昵称是否可用"""
    reserved = {"管理员", "admin", "rex", "rexmatch", "系统", "官方"}
    if nickname.lower() in {r.lower() for r in reserved}:
        return ResponseBase(data={"available": False, "message": "该昵称已被保留"})
    available = await user_service.check_nickname_available(db, nickname, exclude_user_id=current_user.id)
    return ResponseBase(data={
        "available": available,
        "message": "昵称可用，很棒的名字！" if available else "该昵称已被使用"
    })


@router.get("/interests/all", response_model=ResponseBase[list[InterestResponse]])
async def list_interests(db: AsyncSession = Depends(get_db)):
    """获取所有兴趣标签（无需登录）"""
    interests = await user_service.get_all_interests(db)
    return ResponseBase(
        data=[InterestResponse.model_validate(i) for i in interests]
    )


@router.post("/interests/custom", response_model=ResponseBase[InterestResponse])
async def add_custom_interest(
    data: InterestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加自定义兴趣标签"""
    interest = await user_service.create_custom_interest(db, data.name, data.category)
    return ResponseBase(data=InterestResponse.model_validate(interest))
