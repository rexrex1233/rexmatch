"""
发现页/推荐相关 schemas
"""
from typing import Optional
from pydantic import BaseModel, Field


class DiscoverFilter(BaseModel):
    """发现页筛选条件"""
    gender: Optional[int] = Field(None, ge=1, le=2, description="1=男 2=女")
    min_age: Optional[int] = Field(None, ge=18, le=80)
    max_age: Optional[int] = Field(None, ge=18, le=80)
    city: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
