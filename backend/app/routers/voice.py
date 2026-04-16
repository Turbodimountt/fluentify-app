"""
Fluentify — Voice Router
Endpoints: speech-to-text, text-to-speech, pronunciation analysis.
RF-21 to RF-23.
"""
import base64
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.services.voice_service import speech_to_text, text_to_speech, pronunciation_analysis

router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])


async def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization.split(" ")[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    return user_id


class TTSRequest(BaseModel):
    text: str
    voice_id: str = "default"
    language: str = "en"


class PronunciationRequest(BaseModel):
    audio_base64: str
    expected_text: str
    language_code: str = "en-US"


@router.post("/stt")
async def handle_stt(
    audio: UploadFile = File(...),
    language_code: str = Form("en-US"),
    user_id: str = Depends(get_current_user_id),
):
    """RF-21: Speech-to-Text. Audio is processed in memory only."""
    audio_bytes = await audio.read()
    if len(audio_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Audio demasiado grande (max 10MB)")

    result = await speech_to_text(audio_bytes, language_code)
    # audio_bytes cleared inside voice_service
    return result


@router.post("/tts")
async def handle_tts(
    request: TTSRequest,
    user_id: str = Depends(get_current_user_id),
):
    """RF-22: Text-to-Speech."""
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="Texto demasiado largo (max 5000 caracteres)")

    result = await text_to_speech(request.text, request.voice_id, request.language)
    return result


@router.post("/pronunciation")
async def handle_pronunciation(
    request: PronunciationRequest,
    user_id: str = Depends(get_current_user_id),
):
    """RF-23: Pronunciation analysis."""
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Audio base64 inválido")

    result = await pronunciation_analysis(audio_bytes, request.expected_text, request.language_code)
    return result
