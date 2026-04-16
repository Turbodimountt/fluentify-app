"""
Fluentify — Pydantic v2 Schemas for Gamification
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatsResponse(BaseModel):
    total_xp: int
    current_streak: int
    max_streak: int
    user_level: str
    sessions_count: int
    nodes_mastered: int
    nodes_pending_review: int
    total_practice_minutes: int
    error_rate: float


class KnowledgeNodeResponse(BaseModel):
    id: str
    node_key: str
    display_label: str
    mastery_score: float
    repetitions: int
    interval_days: int
    next_review_at: datetime
    category_name: Optional[str] = None
    skill_area: Optional[str] = None
    color_hex: Optional[str] = None

    model_config = {"from_attributes": True}


class AchievementResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    xp_reward: int
    icon_slug: Optional[str] = None
    earned_at: Optional[datetime] = None
    is_unlocked: bool = False

    model_config = {"from_attributes": True}


class AchievementsListResponse(BaseModel):
    unlocked: list[AchievementResponse]
    available: list[AchievementResponse]
    total_unlocked: int
    total_available: int
