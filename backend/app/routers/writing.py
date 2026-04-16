"""
Fluentify — Writing Router
Endpoints: stroke analysis, character library.
RF-24 to RF-27.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.core.security import get_user_id_from_token
from app.services.writing_service import analyze_strokes, get_practice_characters

router = APIRouter(prefix="/api/v1/writing", tags=["Writing"])


async def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    return user_id


class StrokeAnalysisRequest(BaseModel):
    strokes: list[list[dict]]
    target_character: str
    writing_system: str = "kanji"
    cefr_level: str = "A1"


@router.post("/analyze")
async def analyze_writing(
    request: StrokeAnalysisRequest,
    user_id: str = Depends(get_current_user_id),
):
    """RF-24: Analyze handwritten strokes. Target: < 500ms."""
    if not request.strokes:
        raise HTTPException(status_code=400, detail="No se proporcionaron trazos")

    result = await analyze_strokes(
        strokes=request.strokes,
        target_character=request.target_character,
        writing_system=request.writing_system,
        cefr_level=request.cefr_level,
    )
    return result


@router.get("/characters/{writing_system}")
async def get_characters(
    writing_system: str,
    level: str = "beginner",
):
    """RF-25: Get practice characters for a writing system."""
    valid_systems = ["kanji", "cyrillic", "hangul", "arabic"]
    if writing_system not in valid_systems:
        raise HTTPException(status_code=400, detail=f"Sistema inválido. Usa: {', '.join(valid_systems)}")

    characters = get_practice_characters(writing_system, level)
    return {"writing_system": writing_system, "level": level, "characters": characters}
