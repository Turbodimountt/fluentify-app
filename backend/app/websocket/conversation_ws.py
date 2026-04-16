"""
Fluentify — WebSocket Conversation Handler
Real-time streaming of AI responses token-by-token (RF-13).
"""
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_user_id_from_token
from app.core.database import AsyncSessionLocal
from app.services.ai_engine import build_system_prompt, stream_ai_response, parse_ai_response
from app.models.models import ConversationLog, Session, UserProfile, ProfessionalContext
from sqlalchemy import select


async def conversation_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI conversation streaming.
    
    Protocol:
    1. Client sends: {"token": "jwt_token", "session_id": "...", "mode": "libre|roleplay|susurro", ...}
    2. Client sends messages: {"type": "message", "content": "..."}
    3. Server streams: {"type": "token", "content": "word "} per token
    4. Server sends final: {"type": "complete", "corrections": [...], "vocabulary": [...], "suggestion": "..."}
    """
    await websocket.accept()
    
    try:
        # Wait for initial auth message
        init_data = await websocket.receive_json()
        token = init_data.get("token", "")
        user_id = get_user_id_from_token(token)
        
        if not user_id:
            await websocket.send_json({"type": "error", "message": "Token inválido"})
            await websocket.close()
            return

        session_id = init_data.get("session_id")
        mode = init_data.get("mode", "libre")
        target_language = init_data.get("target_language", "en")
        scenario_name = init_data.get("scenario_name")
        professional_context = init_data.get("professional_context", "general")

        await websocket.send_json({"type": "connected", "user_id": user_id})

        # Main message loop
        conversation_history = []
        
        async with AsyncSessionLocal() as db:
            # Get user profile
            profile_result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == uuid.UUID(user_id))
            )
            profile = profile_result.scalar_one_or_none()
            cefr_level = profile.cefr_level if profile else "A1"
            native_language = profile.native_language if profile else "es"

            # Get scenario details
            scenario_description = ""
            ai_role = ""
            if mode == "roleplay" and scenario_name:
                ctx_result = await db.execute(
                    select(ProfessionalContext).where(
                        ProfessionalContext.slug == professional_context.lower()
                    )
                )
                ctx = ctx_result.scalar_one_or_none()
                if ctx and ctx.scenario_templates:
                    for tmpl in ctx.scenario_templates:
                        if tmpl.get("name") == scenario_name:
                            scenario_description = tmpl.get("description", "")
                            ai_role = tmpl.get("ai_role", "")
                            break

            system_prompt = build_system_prompt(
                mode=mode,
                target_language=target_language,
                native_language=native_language,
                cefr_level=cefr_level,
                professional_context=professional_context,
                scenario_name=scenario_name or "",
                scenario_description=scenario_description,
                ai_role=ai_role,
            )

        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                user_message = data.get("content", "")
                conversation_history.append({"role": "user", "content": user_message})

                # Stream AI response
                full_response = ""
                async for token_chunk in stream_ai_response(conversation_history, system_prompt):
                    full_response += token_chunk
                    # Only send visible tokens (not the metadata blocks)
                    if "[CORRECTIONS]" not in full_response:
                        await websocket.send_json({
                            "type": "token",
                            "content": token_chunk,
                        })

                # Parse complete response
                parsed = parse_ai_response(full_response)
                conversation_history.append({"role": "assistant", "content": parsed["response_text"]})

                # Send completion with corrections
                await websocket.send_json({
                    "type": "complete",
                    "ai_response": parsed["response_text"],
                    "corrections": parsed["corrections"],
                    "vocabulary": parsed["vocabulary"],
                    "suggestion": parsed["suggestion"],
                    "turn_number": len(conversation_history) // 2,
                })

                # Save to database
                async with AsyncSessionLocal() as db:
                    if session_id:
                        conv_log = ConversationLog(
                            id=uuid.uuid4(),
                            user_id=uuid.UUID(user_id),
                            session_id=uuid.UUID(session_id),
                            turn_number=len(conversation_history) // 2,
                            user_message=user_message,
                            ai_response=parsed["response_text"],
                            detected_errors=parsed["corrections"],
                            confidence_score=1.0 - (len(parsed["corrections"]) * 0.15),
                        )
                        db.add(conv_log)
                        await db.commit()

            elif data.get("type") == "end":
                await websocket.send_json({"type": "session_ended"})
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
