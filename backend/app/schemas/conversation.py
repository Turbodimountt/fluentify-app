"""
Fluentify — Pydantic v2 Schemas for Conversation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConversationTurnRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=5000)
    mode: str = Field(..., pattern=r"^(libre|roleplay|susurro)$")
    target_language: str = Field(default="en")
    scenario_name: Optional[str] = None
    professional_context: Optional[str] = None


class CorrectionItem(BaseModel):
    original_text: str
    corrected_text: str
    explanation: str
    severity: str = Field(..., pattern=r"^(low|medium|high)$")
    feedback_type: str = "grammar"


class ConversationTurnResponse(BaseModel):
    session_id: str
    turn_number: int
    ai_response: str
    corrections: list[CorrectionItem] = []
    highlighted_vocabulary: list[dict] = []
    suggestion: Optional[str] = None
    xp_earned: int = 0
    confidence_score: float = 0.0


class SessionResponse(BaseModel):
    id: str
    session_type: str
    professional_ctx: Optional[str] = None
    target_language: str
    scenario_name: Optional[str] = None
    duration_seconds: int
    xp_earned: int
    messages_count: int
    errors_detected: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class ScenarioResponse(BaseModel):
    name: str
    description: str
    ai_role: str
    difficulty: str
