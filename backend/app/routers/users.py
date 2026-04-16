"""
Fluentify — Users Router
Endpoints: profile read/update, onboarding.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.models.models import User, UserProfile, ProfessionalContext
from app.schemas.user import (
    ProfileResponse, ProfileUpdateRequest,
    ProfessionalContextResponse, OnboardingRequest
)

router = APIRouter(prefix="/users", tags=["Users"])


async def get_current_user_id(authorization: str = Header(...)) -> str:
    """Extract user_id from Bearer token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    return user_id


async def _build_profile_response(profile: UserProfile, db: AsyncSession) -> ProfileResponse:
    """Build a complete ProfileResponse including user and context info."""
    # Get user info
    user_result = await db.execute(select(User).where(User.id == profile.user_id))
    user = user_result.scalar_one_or_none()

    # Get professional context name
    ctx_name = None
    if profile.professional_context_id:
        ctx_result = await db.execute(
            select(ProfessionalContext).where(ProfessionalContext.id == profile.professional_context_id)
        )
        ctx = ctx_result.scalar_one_or_none()
        ctx_name = ctx.name if ctx else None

    return ProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        display_name=user.display_name if user else "",
        email=user.email if user else "",
        target_language=profile.target_language,
        native_language=profile.native_language,
        cefr_level=profile.cefr_level,
        professional_context_id=str(profile.professional_context_id) if profile.professional_context_id else None,
        professional_context_name=ctx_name,
        total_xp=profile.total_xp,
        current_streak=profile.current_streak,
        max_streak=profile.max_streak,
        last_session_at=profile.last_session_at,
        correction_level=profile.correction_level,
        whisper_mode_default=profile.whisper_mode_default,
        interface_language=profile.interface_language,
        user_level=profile.user_level,
        onboarding_completed=profile.professional_context_id is not None,
    )


@router.get("/me/profile", response_model=ProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-09: Get current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == uuid.UUID(user_id))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return await _build_profile_response(profile, db)


@router.put("/me/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-09: Update current user's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == uuid.UUID(user_id))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "professional_context_id" and value:
            setattr(profile, key, uuid.UUID(value))
        else:
            setattr(profile, key, value)

    await db.flush()
    return await _build_profile_response(profile, db)


@router.post("/me/onboarding", response_model=ProfileResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-07, RF-08: Complete onboarding flow."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == uuid.UUID(user_id))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    profile.target_language = request.target_language
    profile.cefr_level = request.cefr_level
    profile.professional_context_id = uuid.UUID(request.professional_context_id)

    if request.display_name:
        user_result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = user_result.scalar_one_or_none()
        if user:
            user.display_name = request.display_name

    await db.flush()
    return await _build_profile_response(profile, db)


@router.get("/professional-contexts", response_model=list[ProfessionalContextResponse])
async def list_contexts(db: AsyncSession = Depends(get_db)):
    """List all available professional contexts."""
    result = await db.execute(select(ProfessionalContext).order_by(ProfessionalContext.name))
    contexts = result.scalars().all()
    return [
        ProfessionalContextResponse(
            id=str(c.id),
            name=c.name,
            slug=c.slug,
            vocabulary_tags=c.vocabulary_tags or [],
            scenario_templates=c.scenario_templates or [],
            icon_slug=c.icon_slug,
        )
        for c in contexts
    ]
