"""
Fluentify — Conversation Service
Business logic for managing conversation sessions and turns.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.models import (
    Session, ConversationLog, FeedbackEntry,
    UserProfile, ProfessionalContext
)
from app.services.ai_engine import (
    build_system_prompt, generate_ai_response, parse_ai_response
)


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: str,
        session_type: str,
        target_language: str,
        scenario_name: str | None = None,
        professional_ctx: str | None = None,
    ) -> Session:
        """Create a new practice session."""
        session = Session(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            session_type=session_type,
            target_language=target_language,
            scenario_name=scenario_name,
            professional_ctx=professional_ctx,
            is_active=True,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def process_turn(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        mode: str,
        target_language: str,
        scenario_name: str | None = None,
        professional_context: str | None = None,
    ) -> dict:
        """Process a conversation turn: get AI response, parse corrections, save to DB."""
        uid = uuid.UUID(user_id)
        sid = uuid.UUID(session_id)

        # Get user profile for context
        profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == uid)
        )
        profile = profile_result.scalar_one_or_none()

        cefr_level = profile.cefr_level if profile else "A1"
        native_language = profile.native_language if profile else "es"
        pro_context = professional_context or "General"

        # Get scenario details if roleplay
        scenario_description = ""
        ai_role = ""
        if mode == "roleplay" and scenario_name:
            ctx_result = await self.db.execute(
                select(ProfessionalContext).where(ProfessionalContext.slug == pro_context.lower())
            )
            ctx = ctx_result.scalar_one_or_none()
            if ctx and ctx.scenario_templates:
                for tmpl in ctx.scenario_templates:
                    if tmpl.get("name") == scenario_name:
                        scenario_description = tmpl.get("description", "")
                        ai_role = tmpl.get("ai_role", "")
                        break

        # Build system prompt based on mode
        system_prompt = build_system_prompt(
            mode=mode,
            target_language=target_language,
            native_language=native_language,
            cefr_level=cefr_level,
            professional_context=pro_context,
            scenario_name=scenario_name or "",
            scenario_description=scenario_description,
            ai_role=ai_role,
        )

        # Get recent conversation history (last 10 turns)
        history_result = await self.db.execute(
            select(ConversationLog)
            .where(ConversationLog.session_id == sid)
            .order_by(ConversationLog.turn_number.desc())
            .limit(10)
        )
        history = list(reversed(history_result.scalars().all()))

        messages = []
        for log in history:
            messages.append({"role": "user", "content": log.user_message})
            messages.append({"role": "assistant", "content": log.ai_response})
        messages.append({"role": "user", "content": user_message})

        # Generate AI response
        full_response = await generate_ai_response(messages, system_prompt)
        parsed = parse_ai_response(full_response)

        # Calculate turn number
        turn_number = len(history) + 1

        # Save conversation log
        conv_log = ConversationLog(
            id=uuid.uuid4(),
            user_id=uid,
            session_id=sid,
            turn_number=turn_number,
            user_message=user_message,
            ai_response=parsed["response_text"],
            detected_errors=[c for c in parsed["corrections"]],
            confidence_score=1.0 - (len(parsed["corrections"]) * 0.15),
        )
        self.db.add(conv_log)
        await self.db.flush()

        # Save feedback entries
        for correction in parsed["corrections"]:
            entry = FeedbackEntry(
                id=uuid.uuid4(),
                conversation_log_id=conv_log.id,
                feedback_type=correction.get("feedback_type", "grammar"),
                original_text=correction.get("original_text", ""),
                corrected_text=correction.get("corrected_text", ""),
                explanation=correction.get("explanation", ""),
                severity=correction.get("severity", "low"),
            )
            self.db.add(entry)

        # Update session counters
        session_result = await self.db.execute(
            select(Session).where(Session.id == sid)
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.messages_count = turn_number
            session.errors_detected = (session.errors_detected or 0) + len(parsed["corrections"])

        await self.db.flush()

        # Calculate XP for this turn
        base_xp = 10
        error_penalty = len(parsed["corrections"]) * 2
        xp_earned = max(base_xp - error_penalty, 5)

        return {
            "session_id": str(sid),
            "turn_number": turn_number,
            "ai_response": parsed["response_text"],
            "corrections": parsed["corrections"],
            "highlighted_vocabulary": parsed["vocabulary"],
            "suggestion": parsed["suggestion"],
            "xp_earned": xp_earned,
            "confidence_score": conv_log.confidence_score,
        }

    async def end_session(self, session_id: str, user_id: str) -> dict:
        """End a session and calculate final XP."""
        sid = uuid.UUID(session_id)
        uid = uuid.UUID(user_id)

        result = await self.db.execute(
            select(Session).where(Session.id == sid, Session.user_id == uid)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Sesión no encontrada")

        session.is_active = False
        session.ended_at = datetime.now(timezone.utc)

        # Calculate duration
        if session.started_at:
            delta = session.ended_at - session.started_at
            session.duration_seconds = int(delta.total_seconds())

        # Calculate XP based on duration and performance
        duration_bonus = min(session.duration_seconds // 60, 30) * 5  # 5 XP per minute, max 30 min
        base_xp = session.messages_count * 10
        error_penalty = session.errors_detected * 2
        total_xp = max(base_xp + duration_bonus - error_penalty, 10)
        session.xp_earned = total_xp

        await self.db.flush()

        return {
            "session_id": str(sid),
            "xp_earned": total_xp,
            "duration_seconds": session.duration_seconds,
            "messages_count": session.messages_count,
            "errors_detected": session.errors_detected,
        }

    async def get_scenarios(self, context_slug: str) -> list[dict]:
        """Get available scenarios for a professional context."""
        result = await self.db.execute(
            select(ProfessionalContext).where(ProfessionalContext.slug == context_slug)
        )
        ctx = result.scalar_one_or_none()
        if not ctx:
            return []
        return ctx.scenario_templates or []

    async def get_user_sessions(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[Session], int]:
        """Get sessions for a user with pagination."""
        uid = uuid.UUID(user_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(Session).where(Session.user_id == uid)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Session)
            .where(Session.user_id == uid)
            .order_by(Session.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        sessions = result.scalars().all()
        return list(sessions), total
