"""
偏好设置相关 schemas
"""
from typing import Optional
from pydantic import BaseModel, Field


class PreferenceUpdate(BaseModel):
    preferred_gender: Optional[int] = Field(None, ge=1, le=2)
    min_age: Optional[int] = Field(None, ge=18, le=60)
    max_age: Optional[int] = Field(None, ge=18, le=60)
    preferred_city: Optional[str] = Field(None, max_length=50)
    preferred_education: Optional[str] = Field(None, max_length=20)
    personality_tags: Optional[list[str]] = Field(None, max_length=10)


class PreferenceResponse(BaseModel):
    preferred_gender: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    preferred_city: Optional[str] = None
    preferred_education: Optional[str] = None
    personality_tags: list[str] = []

    model_config = {"from_attributes": True}


class CompatibilityInfo(BaseModel):
    score: int = 0
    matched_preferences: list[str] = []
    shared_interests: list[str] = []
