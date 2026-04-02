"""
举报与拉黑 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.report import ReportRequest, BlockRequest
from app.services import report_service

router = APIRouter(prefix="/report", tags=["举报与拉黑"])


@router.post("/submit", response_model=ResponseBase)
async def submit_report(
    req: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交举报"""
    try:
        await report_service.create_report(
            db, current_user.id, req.reported_user_id, req.reason, req.detail
        )
        return ResponseBase(message="举报已提交")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/block", response_model=ResponseBase)
async def block_user(
    req: BlockRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """拉黑用户"""
    try:
        await report_service.block_user(db, current_user.id, req.blocked_user_id)
        return ResponseBase(message="已拉黑")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/block-list", response_model=ResponseBase[list])
async def get_block_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取黑名单列表"""
    blocks = await report_service.get_block_list(db, current_user.id)
    return ResponseBase(data=blocks)


@router.post("/unblock/{user_id}", response_model=ResponseBase)
async def unblock_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消拉黑"""
    success = await report_service.unblock_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="未拉黑该用户")
    return ResponseBase(message="已取消拉黑")
