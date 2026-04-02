"""
文件上传 API - 自动选择本地存储或 S3 对象存储
"""
import os

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.storage import upload_file
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.user import PhotoResponse
from app.services import user_service

router = APIRouter(prefix="/upload", tags=["文件上传"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/photo", response_model=ResponseBase[PhotoResponse])
async def upload_photo(
    file: UploadFile = File(...),
    is_avatar: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传用户照片（支持 jpg/png/gif/webp，最大 5MB）"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    photo_url = await upload_file(content, current_user.id, ext, is_avatar)

    photo = await user_service.add_photo(db, current_user.id, photo_url, is_avatar)
    return ResponseBase(data=PhotoResponse.model_validate(photo))
