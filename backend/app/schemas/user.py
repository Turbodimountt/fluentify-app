"""
Fluentify — Pydantic v2 Schemas for User Profile
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: str = ""
    email: str = ""
    target_language: str
    native_language: str
    cefr_level: str
    professional_context_id: Optional[str] = None
    professional_context_name: Optional[str] = None
    total_xp: int
    current_streak: int
    max_streak: int
    last_session_at: Optional[datetime] = None
    correction_level: str
    whisper_mode_default: bool
    interface_language: str
    user_level: str
    onboarding_completed: bool = False

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    target_language: Optional[str] = None
    native_language: Optional[str] = None
    cefr_level: Optional[str] = Field(None, pattern=r"^(A1|A2|B1|B2|C1|C2)$")
    professional_context_id: Optional[str] = None
    correction_level: Optional[str] = Field(None, pattern=r"^(low|medium|high)$")
    whisper_mode_default: Optional[bool] = None
    interface_language: Optional[str] = Field(None, pattern=r"^(es|en)$")


class ProfessionalContextResponse(BaseModel):
    id: str
    name: str
    slug: str
    vocabulary_tags: list[str]
    scenario_templates: list[dict]
    icon_slug: Optional[str] = None

    model_config = {"from_attributes": True}


class OnboardingRequest(BaseModel):
    target_language: str = Field(..., description="Target language to learn")
    cefr_level: str = Field(..., pattern=r"^(A1|A2|B1|B2|C1|C2)$")
    professional_context_id: str
    display_name: Optional[str] = None
