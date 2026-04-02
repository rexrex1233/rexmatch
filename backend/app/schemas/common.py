"""
公共响应模型
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PageInfo(BaseModel):
    """分页信息"""
    page: int
    page_size: int
    total: int


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    code: int = 0
    message: str = "success"
    data: Optional[list[T]] = None
    page_info: Optional[PageInfo] = None
