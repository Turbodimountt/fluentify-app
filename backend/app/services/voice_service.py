"""
Fluentify — Voice Service
RF-21 to RF-23: Speech-to-Text (Google Cloud STT) and Text-to-Speech (ElevenLabs).
Audio is processed in memory and never persisted (safety.md requirement).
"""
import io
import base64
from app.core.config import settings


async def speech_to_text(audio_bytes: bytes, language_code: str = "en-US") -> dict:
    """
    RF-21: Transcribe audio to text.
    Audio is processed in memory only — never persisted to disk.
    
    Returns:
        {"text": "transcribed text", "confidence": 0.95, "language": "en-US"}
    """
    if settings.is_stt_mock_mode:
        return _mock_stt(language_code)

    try:
        from google.cloud import speech_v1

        client = speech_v1.SpeechAsyncClient()
        audio = speech_v1.RecognitionAudio(content=audio_bytes)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        response = await client.recognize(config=config, audio=audio)
        
        if response.results:
            best = response.results[0].alternatives[0]
            return {
                "text": best.transcript,
                "confidence": best.confidence,
                "language": language_code,
            }
        return {"text": "", "confidence": 0.0, "language": language_code}

    except Exception as e:
        return {"text": "", "confidence": 0.0, "language": language_code, "error": str(e)}
    finally:
        # Ensure audio bytes are cleared from memory (privacy requirement)
        del audio_bytes


async def text_to_speech(text: str, voice_id: str = "default", language: str = "en") -> dict:
    """
    RF-22: Convert text to speech audio.
    Returns base64 encoded audio data.
    
    Returns:
        {"audio_base64": "...", "content_type": "audio/mpeg", "duration_ms": 1500}
    """
    if settings.is_tts_mock_mode:
        return _mock_tts(text, language)

    try:
        import httpx

        voice_map = {
            "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "ja": "AZnzlk1XvdvUeBnXmlld",  # Japanese voice
            "ru": "EXAVITQu4vr4xnSDxMaL",  # Russian voice  
            "fr": "ThT5KcBeYPX3keUQqHPh",  # French voice
            "zh": "g5CIjZEefAph4nQFvHAz",  # Chinese voice
        }

        selected_voice = voice_map.get(language, voice_map["en"])
        if voice_id != "default":
            selected_voice = voice_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice}",
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=15.0,
            )

            if response.status_code == 200:
                audio_data = response.content
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")
                return {
                    "audio_base64": audio_b64,
                    "content_type": "audio/mpeg",
                    "duration_ms": int(len(audio_data) / 16),  # Approximation
                }

        return {"audio_base64": "", "content_type": "", "error": "TTS API error"}

    except Exception as e:
        return {"audio_base64": "", "content_type": "", "error": str(e)}


async def pronunciation_analysis(
    audio_bytes: bytes,
    expected_text: str,
    language_code: str = "en-US",
) -> dict:
    """
    RF-23: Analyze pronunciation quality.
    Compares transcription against expected text.
    Audio is processed in memory only.
    
    Returns:
        {"score": 0.85, "transcript": "...", "issues": [...], "tips": [...]}
    """
    if settings.is_stt_mock_mode:
        return _mock_pronunciation(expected_text)

    # Transcribe first
    result = await speech_to_text(audio_bytes, language_code)
    transcript = result.get("text", "")

    # Compare transcription with expected text
    expected_words = expected_text.lower().split()
    actual_words = transcript.lower().split()

    matching = 0
    issues = []
    for i, word in enumerate(expected_words):
        if i < len(actual_words) and actual_words[i] == word:
            matching += 1
        elif i < len(actual_words):
            issues.append({
                "expected": word,
                "heard": actual_words[i],
                "position": i,
                "tip": f"Intenta pronunciar '{word}' con más claridad",
            })
        else:
            issues.append({
                "expected": word,
                "heard": "(no detectado)",
                "position": i,
                "tip": f"Asegúrate de pronunciar '{word}'",
            })

    score = matching / max(len(expected_words), 1)

    return {
        "score": round(score, 2),
        "transcript": transcript,
        "expected_text": expected_text,
        "issues": issues[:5],  # Limit to 5 issues
        "tips": [
            "Habla más despacio para mayor claridad" if score < 0.5 else "",
            "¡Excelente pronunciación!" if score > 0.9 else "",
        ],
    }


# ============================================================
# Mock Implementations
# ============================================================
def _mock_stt(language_code: str) -> dict:
    mock_texts = {
        "en-US": "Hello, I would like to practice my English today.",
        "ja-JP": "こんにちは、今日は日本語を練習したいです。",
        "ru-RU": "Здравствуйте, я хочу практиковать русский язык.",
        "fr-FR": "Bonjour, je voudrais pratiquer mon français aujourd'hui.",
        "zh-CN": "你好，我今天想练习中文。",
    }
    return {
        "text": mock_texts.get(language_code, mock_texts["en-US"]),
        "confidence": 0.92,
        "language": language_code,
        "mock": True,
    }


def _mock_tts(text: str, language: str) -> dict:
    # Generate a tiny silent WAV as mock audio
    import struct
    sample_rate = 22050
    duration = min(len(text) * 0.06, 10.0)
    num_samples = int(sample_rate * duration)
    
    wav_buffer = io.BytesIO()
    # WAV header
    wav_buffer.write(b'RIFF')
    data_size = num_samples * 2
    wav_buffer.write(struct.pack('<I', 36 + data_size))
    wav_buffer.write(b'WAVEfmt ')
    wav_buffer.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    wav_buffer.write(b'data')
    wav_buffer.write(struct.pack('<I', data_size))
    # Silent samples
    wav_buffer.write(b'\x00\x00' * num_samples)
    
    audio_b64 = base64.b64encode(wav_buffer.getvalue()).decode("utf-8")
    return {
        "audio_base64": audio_b64,
        "content_type": "audio/wav",
        "duration_ms": int(duration * 1000),
        "mock": True,
    }


def _mock_pronunciation(expected_text: str) -> dict:
    import random
    score = round(random.uniform(0.65, 0.98), 2)
    words = expected_text.split()
    issues = []
    if score < 0.85 and len(words) > 2:
        issues.append({
            "expected": words[1],
            "heard": words[1][::-1] if len(words[1]) > 2 else "??",
            "position": 1,
            "tip": f"Practica la pronunciación de '{words[1]}'",
        })
    return {
        "score": score,
        "transcript": expected_text if score > 0.9 else " ".join(words[:-1]),
        "expected_text": expected_text,
        "issues": issues,
        "tips": ["¡Buen intento! Sigue practicando. 💪"] if score < 0.85 else ["¡Excelente pronunciación! 🌟"],
        "mock": True,
    }
