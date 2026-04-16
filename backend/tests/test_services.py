"""
Fluentify — Backend Unit Tests
Target: ≥ 70% coverage per testing.md rules.
"""
import pytest
import uuid
from unittest.mock import patch
from datetime import datetime, timedelta


# ============================================================
# Auth Service Tests
# ============================================================
class TestAuthService:
    """Tests for user registration, login, and token management."""

    def test_password_hashing(self):
        from app.core.security import hash_password, verify_password
        pwd = "TestPassword123!"
        hashed = hash_password(pwd)
        assert hashed != pwd
        assert verify_password(pwd, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_jwt_token_creation(self):
        from app.core.security import create_access_token, get_user_id_from_token
        user_id = str(uuid.uuid4())
        token = create_access_token({"sub": user_id})
        assert token is not None
        assert isinstance(token, str)
        extracted = get_user_id_from_token(token)
        assert extracted == user_id

    def test_jwt_token_expired(self):
        from app.core.security import get_user_id_from_token
        from jose import jwt
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now() - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")
        result = get_user_id_from_token(expired_token)
        assert result is None

    def test_jwt_token_invalid(self):
        from app.core.security import get_user_id_from_token
        result = get_user_id_from_token("not.a.valid.jwt")
        assert result is None


# ============================================================
# AI Engine Tests
# ============================================================
class TestAIEngine:
    """Tests for prompt construction and response parsing."""

    def test_build_system_prompt_libre(self):
        from app.services.ai_engine import build_system_prompt
        prompt = build_system_prompt(
            mode="libre",
            target_language="en",
            native_language="es",
            cefr_level="B1",
        )
        assert "B1" in prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_build_system_prompt_roleplay(self):
        from app.services.ai_engine import build_system_prompt
        prompt = build_system_prompt(
            mode="roleplay",
            target_language="en",
            native_language="es",
            cefr_level="B2",
            professional_context="medicine",
            scenario_name="Doctor Appointment",
            scenario_description="Patient visits doctor",
            ai_role="Doctor",
        )
        assert "[Coach:" in prompt or "coach" in prompt.lower() or "Coach" in prompt

    def test_build_system_prompt_susurro(self):
        from app.services.ai_engine import build_system_prompt
        prompt = build_system_prompt(
            mode="susurro",
            target_language="ja",
            native_language="es",
            cefr_level="A1",
        )
        assert "2" in prompt or "dos" in prompt.lower() or "máximo" in prompt.lower()

    def test_parse_ai_response_with_corrections(self):
        from app.services.ai_engine import parse_ai_response
        raw = """That's a great attempt! Let me help you.

[CORRECTIONS]
- "I go yesterday" → "I went yesterday" | Usa pasado simple para acciones completadas
[/CORRECTIONS]

[VOCABULARY]
- went: ir (pasado) | "I went to the store" 
[/VOCABULARY]

[SUGGESTION]
Can you tell me about your weekend?
[/SUGGESTION]"""
        
        result = parse_ai_response(raw)
        assert "response_text" in result
        assert "corrections" in result
        assert "vocabulary" in result
        assert "suggestion" in result

    def test_parse_ai_response_empty(self):
        from app.services.ai_engine import parse_ai_response
        result = parse_ai_response("Hello! How are you?")
        assert result["response_text"] == "Hello! How are you?"
        assert result["corrections"] == []
        assert result["vocabulary"] == []
        # suggestion may be None or ""
        assert result["suggestion"] is None or result["suggestion"] == ""


# ============================================================
# Gamification Service Tests
# ============================================================
class TestGamification:
    """Tests for SM-2 algorithm, XP, streak, and level calculations."""

    def test_sm2_algorithm_perfect(self):
        from app.services.gamification_service import sm2_algorithm
        # SM-2 returns tuple: (new_reps, new_ef, new_interval)
        new_reps, new_ef, new_interval = sm2_algorithm(
            quality=5,
            repetitions=1,
            easiness_factor=2.5,
            interval_days=1,
        )
        assert new_interval > 1  # interval should increase
        assert new_ef >= 2.5     # ease should not decrease for quality=5
        assert new_reps == 2     # repetitions should increment

    def test_sm2_algorithm_fail(self):
        from app.services.gamification_service import sm2_algorithm
        new_reps, new_ef, new_interval = sm2_algorithm(
            quality=1,
            repetitions=5,
            easiness_factor=2.5,
            interval_days=30,
        )
        assert new_reps == 0      # reset repetitions
        assert new_interval == 1  # reset interval

    def test_sm2_minimum_ease_factor(self):
        from app.services.gamification_service import sm2_algorithm
        _, new_ef, _ = sm2_algorithm(
            quality=0,
            repetitions=0,
            easiness_factor=1.3,
            interval_days=1,
        )
        assert new_ef >= 1.3  # ease factor minimum is 1.3

    def test_calculate_level(self):
        from app.services.gamification_service import calculate_level
        assert calculate_level(0) == "Explorador"
        assert calculate_level(499) == "Explorador"
        assert calculate_level(500) == "Aventurero"
        assert calculate_level(5000) == "Artesano"
        assert calculate_level(25000) == "Sabio"
        assert calculate_level(50000) == "Maestro"

    def test_level_thresholds_ordered(self):
        from app.services.gamification_service import LEVEL_THRESHOLDS
        values = list(LEVEL_THRESHOLDS.values())
        assert values == sorted(values), "Level thresholds should be in ascending order"


# ============================================================
# Writing Service Tests
# ============================================================
class TestWritingService:
    """Tests for stroke analysis and character library."""

    def test_get_practice_characters_kanji(self):
        from app.services.writing_service import get_practice_characters
        chars = get_practice_characters("kanji", "beginner")
        assert len(chars) > 0
        assert all("char" in c for c in chars)
        assert all("meaning" in c for c in chars)
        assert all("strokes" in c for c in chars)

    def test_get_practice_characters_cyrillic(self):
        from app.services.writing_service import get_practice_characters
        chars = get_practice_characters("cyrillic", "beginner")
        assert len(chars) > 0

    def test_get_practice_characters_unknown(self):
        from app.services.writing_service import get_practice_characters
        chars = get_practice_characters("unknown_system")
        assert chars == []

    @pytest.mark.asyncio
    async def test_analyze_strokes_basic(self):
        from app.services.writing_service import analyze_strokes
        strokes = [
            [{"x": 10, "y": 50, "t": 0}, {"x": 200, "y": 50, "t": 100}]
        ]
        result = await analyze_strokes(strokes, "一", "kanji")
        assert "accuracy_score" in result
        assert "feedback" in result
        assert result["target_character"] == "一"
        assert result["processing_ms"] < 500  # Performance requirement

    @pytest.mark.asyncio
    async def test_analyze_strokes_empty(self):
        from app.services.writing_service import analyze_strokes
        result = await analyze_strokes([], "一", "kanji")
        assert result["stroke_count_actual"] == 0

    @pytest.mark.asyncio
    async def test_analyze_strokes_correct_count(self):
        from app.services.writing_service import analyze_strokes
        # 一 has 1 stroke
        strokes = [[{"x": 10, "y": 50}, {"x": 200, "y": 50}]]
        result = await analyze_strokes(strokes, "一", "kanji")
        assert result["stroke_count_expected"] == 1
        assert result["stroke_count_actual"] == 1


# ============================================================
# Voice Service Tests
# ============================================================
class TestVoiceService:
    """Tests for mock mode voice features."""

    @pytest.mark.asyncio
    async def test_mock_stt(self):
        from app.services.voice_service import speech_to_text
        with patch("app.services.voice_service.settings") as mock_settings:
            mock_settings.is_stt_mock_mode = True
            result = await speech_to_text(b"fake_audio", "en-US")
            assert "text" in result
            assert result["confidence"] > 0
            assert result.get("mock") is True

    @pytest.mark.asyncio
    async def test_mock_tts(self):
        from app.services.voice_service import text_to_speech
        with patch("app.services.voice_service.settings") as mock_settings:
            mock_settings.is_tts_mock_mode = True
            result = await text_to_speech("Hello world", "default", "en")
            assert "audio_base64" in result
            assert result["content_type"] == "audio/wav"
            assert result.get("mock") is True

    @pytest.mark.asyncio
    async def test_mock_pronunciation(self):
        from app.services.voice_service import pronunciation_analysis
        with patch("app.services.voice_service.settings") as mock_settings:
            mock_settings.is_stt_mock_mode = True
            result = await pronunciation_analysis(b"fake_audio", "Hello world", "en-US")
            assert "score" in result
            assert 0 <= result["score"] <= 1
            assert "issues" in result
            assert result.get("mock") is True

    @pytest.mark.asyncio
    async def test_mock_tts_duration(self):
        from app.services.voice_service import text_to_speech
        with patch("app.services.voice_service.settings") as mock_settings:
            mock_settings.is_tts_mock_mode = True
            result = await text_to_speech("Short", "default", "en")
            result2 = await text_to_speech("This is a much longer sentence for testing TTS", "default", "en")
            assert result2["duration_ms"] > result["duration_ms"]


# ============================================================
# Config Tests
# ============================================================
class TestConfig:
    """Tests for configuration and settings."""

    def test_settings_defaults(self):
        from app.core.config import Settings
        s = Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            jwt_secret_key="test-secret",
        )
        assert s.app_name == "Fluentify"
        assert s.debug is True

    def test_mock_mode_detection(self):
        from app.core.config import Settings
        # Empty key = mock mode
        s = Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            jwt_secret_key="test-secret",
            openai_api_key="",
        )
        assert s.is_ai_mock_mode is True

        # No key = mock mode
        s2 = Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            jwt_secret_key="test-secret",
        )
        assert s2.is_ai_mock_mode is True

        # Real key = live mode
        s3 = Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            jwt_secret_key="test-secret",
            openai_api_key="sk-real-key-12345",
        )
        assert s3.is_ai_mock_mode is False

    def test_cors_origins(self):
        from app.core.config import Settings
        s = Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            jwt_secret_key="test-secret",
        )
        assert isinstance(s.cors_origins, list)
        assert len(s.cors_origins) > 0
