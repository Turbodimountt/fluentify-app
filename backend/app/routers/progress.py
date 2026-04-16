"""
Fluentify — Progress & Gamification Router
Endpoints: stats, knowledge nodes, achievements.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.services.gamification_service import GamificationService
from app.schemas.gamification import StatsResponse, AchievementsListResponse

router = APIRouter(tags=["Progress & Gamification"])


async def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    return user_id


@router.get("/progress/stats", response_model=StatsResponse)
async def get_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-34: Get user's progress statistics."""
    service = GamificationService(db)
    try:
        stats = await service.get_stats(user_id)
        return StatsResponse(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/progress/nodes")
async def get_knowledge_nodes(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-29: Get user's knowledge node constellation."""
    service = GamificationService(db)
    nodes = await service.get_knowledge_nodes(user_id)
    return {"nodes": nodes, "total": len(nodes)}


@router.get("/achievements", response_model=AchievementsListResponse)
async def get_achievements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """RF-32: Get user's achievements."""
    service = GamificationService(db)
    result = await service.get_achievements(user_id)
    return AchievementsListResponse(**result)
