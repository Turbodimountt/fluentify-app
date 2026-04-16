"""
Fluentify Backend — Application Configuration
Uses Pydantic v2 BaseSettings for environment variable management.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "Fluentify"
    app_version: str = "1.0.0"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # Database
    database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # Google Gemini
    google_api_key: Optional[str] = None

    # Google Cloud STT
    google_cloud_project_id: Optional[str] = None
    google_application_credentials: Optional[str] = None

    # ElevenLabs TTS
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None

    # Redis
    redis_url: Optional[str] = None

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # Emergency / Dev Mode
    force_mock_mode: bool = False

    @property
    def is_ai_mock_mode(self) -> bool:
        return self.force_mock_mode or (not self.openai_api_key and not self.google_api_key)

    @property
    def is_stt_mock_mode(self) -> bool:
        return self.force_mock_mode or not self.google_cloud_project_id

    @property
    def is_tts_mock_mode(self) -> bool:
        return self.force_mock_mode or not self.elevenlabs_api_key

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
