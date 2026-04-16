"""
Fluentify — AI Engine Service
Handles OpenAI integration with dynamic prompts per mode (Libre, Roleplay, Susurro).
Falls back to mock responses when OPENAI_API_KEY is not configured.
"""
import json
from typing import AsyncGenerator, Optional
from app.core.config import settings


# ============================================================
# Prompt Templates per Mode
# ============================================================

SYSTEM_PROMPT_LIBRE = """You are Fluentify, an AI language tutor helping the user practice {target_language}.
The user's native language is {native_language} and their level is {cefr_level}.
Their professional context is: {professional_context}.

Rules:
- Respond ONLY in {target_language}.
- Evaluate the user's grammar, coherence, and tone.
- After your response, provide corrections in this JSON format within a special block:
  [CORRECTIONS]
  {{"corrections": [{{"original_text": "...", "corrected_text": "...", "explanation": "...", "severity": "low|medium|high", "feedback_type": "grammar|vocabulary|pronunciation|style"}}]}}
  [/CORRECTIONS]
- Highlight 1-3 useful vocabulary terms from the professional context:
  [VOCABULARY]
  {{"terms": [{{"term": "...", "translation": "...", "example": "..."}}]}}
  [/VOCABULARY]
- Suggest a continuation question:
  [SUGGESTION]
  {{"text": "..."}}
  [/SUGGESTION]
- Keep conversation natural and encouraging.
- Match your complexity to the user's CEFR level."""

SYSTEM_PROMPT_ROLEPLAY = """You are roleplaying as: {ai_role}
Scenario: {scenario_name} — {scenario_description}
The user is practicing {target_language} (level: {cefr_level}, professional context: {professional_context}).

Rules:
- STAY IN CHARACTER at all times. Only break character with the prefix [Coach:] for pedagogical feedback.
- Respond ONLY in {target_language}.
- Keep responses appropriate for {cefr_level} level.
- Limit corrections to the most impactful ones using [Coach:] prefix.
- After your in-character response, provide corrections block:
  [CORRECTIONS]
  {{"corrections": [{{"original_text": "...", "corrected_text": "...", "explanation": "...", "severity": "low|medium|high", "feedback_type": "grammar|vocabulary|pronunciation|style"}}]}}
  [/CORRECTIONS]
- Highlight professional vocabulary:
  [VOCABULARY]
  {{"terms": [{{"term": "...", "translation": "...", "example": "..."}}]}}
  [/VOCABULARY]"""

SYSTEM_PROMPT_SUSURRO = """You are Fluentify in Whisper Mode — a warm, patient, and encouraging language companion.
The user is practicing {target_language} pronunciation (level: {cefr_level}).
Their native language is {native_language}.

CRITICAL Rules (Psychological Safety — RNF-14):
- Be EXTREMELY warm, empathetic, and encouraging.
- Maximum 2 corrections per turn. Choose only the most important ones.
- NEVER use error sounds, negative scoring, or intimidating language.
- Use phrases like "Great try!", "You're doing well!", "Almost perfect!".
- Focus on positive reinforcement first, then gently suggest improvements.
- Respond in {target_language} with simple, clear sentences.
- After your response, provide max 2 corrections:
  [CORRECTIONS]
  {{"corrections": [{{"original_text": "...", "corrected_text": "...", "explanation": "...", "severity": "low", "feedback_type": "pronunciation"}}]}}
  [/CORRECTIONS]
- NO numeric scores, NO rankings, NO competitive language."""


def build_system_prompt(
    mode: str,
    target_language: str,
    native_language: str = "es",
    cefr_level: str = "A1",
    professional_context: str = "General",
    scenario_name: str = "",
    scenario_description: str = "",
    ai_role: str = "",
) -> str:
    """Build the system prompt based on the conversation mode."""
    if mode == "roleplay":
        return SYSTEM_PROMPT_ROLEPLAY.format(
            target_language=target_language,
            native_language=native_language,
            cefr_level=cefr_level,
            professional_context=professional_context,
            scenario_name=scenario_name,
            scenario_description=scenario_description,
            ai_role=ai_role,
        )
    elif mode == "susurro":
        return SYSTEM_PROMPT_SUSURRO.format(
            target_language=target_language,
            native_language=native_language,
            cefr_level=cefr_level,
        )
    else:  # libre
        return SYSTEM_PROMPT_LIBRE.format(
            target_language=target_language,
            native_language=native_language,
            cefr_level=cefr_level,
            professional_context=professional_context,
        )


def parse_ai_response(full_response: str) -> dict:
    """Parse the AI response to extract corrections, vocabulary, and suggestion."""
    result = {
        "response_text": full_response,
        "corrections": [],
        "vocabulary": [],
        "suggestion": None,
    }

    # Extract corrections
    if "[CORRECTIONS]" in full_response and "[/CORRECTIONS]" in full_response:
        start = full_response.index("[CORRECTIONS]") + len("[CORRECTIONS]")
        end = full_response.index("[/CORRECTIONS]")
        try:
            data = json.loads(full_response[start:end].strip())
            result["corrections"] = data.get("corrections", [])
        except json.JSONDecodeError:
            pass
        result["response_text"] = full_response[:full_response.index("[CORRECTIONS]")].strip()

    # Extract vocabulary
    if "[VOCABULARY]" in full_response and "[/VOCABULARY]" in full_response:
        start = full_response.index("[VOCABULARY]") + len("[VOCABULARY]")
        end = full_response.index("[/VOCABULARY]")
        try:
            data = json.loads(full_response[start:end].strip())
            result["vocabulary"] = data.get("terms", [])
        except json.JSONDecodeError:
            pass
        if "[VOCABULARY]" in result["response_text"]:
            result["response_text"] = result["response_text"][:result["response_text"].index("[VOCABULARY]")].strip()

    # Extract suggestion
    if "[SUGGESTION]" in full_response and "[/SUGGESTION]" in full_response:
        start = full_response.index("[SUGGESTION]") + len("[SUGGESTION]")
        end = full_response.index("[/SUGGESTION]")
        try:
            data = json.loads(full_response[start:end].strip())
            result["suggestion"] = data.get("text")
        except json.JSONDecodeError:
            pass
        if "[SUGGESTION]" in result["response_text"]:
            result["response_text"] = result["response_text"][:result["response_text"].index("[SUGGESTION]")].strip()

    return result


async def generate_ai_response(
    messages: list[dict],
    system_prompt: str,
) -> str:
    """Generate a complete AI response (non-streaming)."""
    if settings.is_ai_mock_mode:
        return _mock_response(messages[-1]["content"] if messages else "")

    # Priority 1: Google Gemini
    if settings.google_api_key:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Convert message history for Gemini (system prompt goes to the first turn or instruction)
        # For simplicity with current structure, we prepend system prompt to the user message or use it in the model init
        # But let's use the standard conversation structure
        chat = model.start_chat(history=[])
        
        # Gemini behaves better with system instruction in constructor, but let's stick to simple prompt injection for now
        # to match the current OpenAI-centric 'system_prompt' + 'messages' structure.
        combined_prompt = f"{system_prompt}\n\nUser context/history follows:\n"
        for msg in messages[:-1]:
            combined_prompt += f"{msg['role']}: {msg['content']}\n"
        
        last_user_msg = messages[-1]["content"] if messages else ""
        
        response = await model.generate_content_async(
            f"{combined_prompt}\nUser: {last_user_msg}",
            generation_config={"temperature": 0.7, "max_output_tokens": 1000}
        )
        return response.text

    # Priority 2: OpenAI
    if settings.openai_api_key:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content or ""
    
    return _mock_response(messages[-1]["content"] if messages else "")


async def stream_ai_response(
    messages: list[dict],
    system_prompt: str,
) -> AsyncGenerator[str, None]:
    """Stream AI response token by token via WebSocket."""
    if settings.is_ai_mock_mode:
        mock = _mock_response(messages[-1]["content"] if messages else "")
        for word in mock.split(" "):
            yield word + " "
        return

    # Priority 1: Google Gemini
    if settings.google_api_key:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        combined_prompt = f"{system_prompt}\n\nUser context/history follows:\n"
        for msg in messages[:-1]:
            combined_prompt += f"{msg['role']}: {msg['content']}\n"
        
        last_user_msg = messages[-1]["content"] if messages else ""
        
        response = await model.generate_content_async(
            f"{combined_prompt}\nUser: {last_user_msg}",
            generation_config={"temperature": 0.7, "max_output_tokens": 1000},
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
        return

    # Priority 2: OpenAI
    if settings.openai_api_key:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        stream = await client.chat.completions.create(
            model=settings.openai_model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        return


def _mock_response(user_message: str) -> str:
    """Generate a mock response for development without API key."""
    return f"""That's a great message! Let me help you practice.

I understood your message: "{user_message[:50]}..."

Here's my response to continue our conversation. Keep practicing, you're doing great!

What would you like to talk about next?

[CORRECTIONS]
{{"corrections": [{{"original_text": "example error", "corrected_text": "example correction", "explanation": "This is a mock correction for development purposes.", "severity": "low", "feedback_type": "grammar"}}]}}
[/CORRECTIONS]

[VOCABULARY]
{{"terms": [{{"term": "practice", "translation": "práctica", "example": "Practice makes perfect."}}]}}
[/VOCABULARY]

[SUGGESTION]
{{"text": "Can you tell me about your favorite hobby?"}}
[/SUGGESTION]"""
