"""
举报与拉黑相关 schemas
"""
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """举报请求"""
    reported_user_id: int
    reason: str = Field(..., max_length=50)
    detail: str | None = Field(None, max_length=500)


class BlockRequest(BaseModel):
    """拉黑请求"""
    blocked_user_id: int
