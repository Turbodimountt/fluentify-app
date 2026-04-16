"""
Fluentify — Conversation Router
Endpoints: conversation turns, sessions, scenarios.
"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.schemas.conversation import (
    ConversationTurnRequest, ConversationTurnResponse,
    SessionResponse, SessionListResponse, ScenarioResponse
)
from app.services.conversation_service import ConversationService
from app.services.gamification_service import GamificationService

router = APIRouter(prefix="/api/v1", tags=["Conversation"])


async def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    return user_id


@router.post("/conversation", response_model=ConversationTurnResponse)
async def conversation_turn(
    request: ConversationTurnRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-10, RF-11, RF-12: Process a conversation turn via HTTP (fallback)."""
    service = ConversationService(db)
    gamification = GamificationService(db)

    try:
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session = await service.create_session(
                user_id=user_id,
                session_type=request.mode,
                target_language=request.target_language,
                scenario_name=request.scenario_name,
                professional_ctx=request.professional_context,
            )
            session_id = str(session.id)

        result = await service.process_turn(
            user_id=user_id,
            session_id=session_id,
            user_message=request.message,
            mode=request.mode,
            target_language=request.target_language,
            scenario_name=request.scenario_name,
            professional_context=request.professional_context,
        )

        # Award XP
        await gamification.award_xp(user_id, result["xp_earned"])

        return ConversationTurnResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """End a practice session and finalize XP."""
    conv_service = ConversationService(db)
    gam_service = GamificationService(db)

    try:
        result = await conv_service.end_session(session_id, user_id)
        # Award final XP and update streak
        await gam_service.award_xp(user_id, result["xp_earned"])
        await gam_service.update_streak(user_id)
        # Check for new achievements
        new_achievements = await gam_service.check_achievements(user_id)
        result["new_achievements"] = new_achievements
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scenarios/{context_slug}", response_model=list[ScenarioResponse])
async def get_scenarios(
    context_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """RF-15: Get available scenarios for a context."""
    service = ConversationService(db)
    scenarios = await service.get_scenarios(context_slug)
    return [ScenarioResponse(**s) for s in scenarios]


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-35: Get session history for user."""
    service = ConversationService(db)
    sessions, total = await service.get_user_sessions(user_id, limit, offset)
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total,
    )
