"""
Fluentify — SQLAlchemy Models
All database models matching the Supabase schema.
Compatible with both PostgreSQL and SQLite (dev mode).
"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, Text, DateTime,
    ForeignKey, UniqueConstraint, TypeDecorator
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import CHAR, TypeDecorator as TD
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


# ============================================================
# Portable UUID type — works on both PostgreSQL and SQLite
# ============================================================
class PortableUUID(TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL UUID or CHAR(36)."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))


# ============================================================
# Portable JSON type — works on both PostgreSQL and SQLite
# ============================================================
class PortableJSON(TypeDecorator):
    """Platform-independent JSON type. Uses JSONB on PG, TEXT on SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value) if not isinstance(value, str) else value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(Text)


# ============================================================
# Portable ARRAY type — stores as JSON in SQLite
# ============================================================
class PortableArray(TypeDecorator):
    """Platform-independent ARRAY type. Uses TEXT[] on PG, JSON text on SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if dialect.name == "postgresql":
            return value  # PostgreSQL handles arrays natively
        if value is not None:
            return json.dumps(value)
        return "[]"

    def process_result_value(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        if value is not None and isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return []
        return value or []

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import ARRAY
            return dialect.type_descriptor(ARRAY(Text))
        return dialect.type_descriptor(Text)


class User(Base):
    __tablename__ = "users"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    target_language = Column(String, default="en", nullable=False)
    native_language = Column(String, default="es", nullable=False)
    cefr_level = Column(String, default="A1", nullable=False)
    professional_context_id = Column(PortableUUID(), ForeignKey("professional_contexts.id", ondelete="SET NULL"))
    total_xp = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_session_at = Column(DateTime(timezone=True))
    correction_level = Column(String, default="medium", nullable=False)
    whisper_mode_default = Column(Boolean, default=False, nullable=False)
    interface_language = Column(String, default="es", nullable=False)
    user_level = Column(String, default="Explorador", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
    professional_context = relationship("ProfessionalContext")


class ProfessionalContext(Base):
    __tablename__ = "professional_contexts"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    vocabulary_tags = Column(PortableArray(), default=[])
    scenario_templates = Column(PortableJSON(), default=[])
    icon_slug = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String, nullable=False)
    professional_ctx = Column(String)
    target_language = Column(String, nullable=False)
    scenario_name = Column(String)
    duration_seconds = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    errors_detected = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    ended_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversation_logs = relationship("ConversationLog", back_populates="session", cascade="all, delete-orphan")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(PortableUUID(), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    detected_errors = Column(PortableJSON(), default=[])
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="conversation_logs")
    feedback_entries = relationship("FeedbackEntry", back_populates="conversation_log", cascade="all, delete-orphan")


class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    conversation_log_id = Column(PortableUUID(), ForeignKey("conversation_logs.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String, default="grammar", nullable=False)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    was_helpful = Column(Boolean)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    conversation_log = relationship("ConversationLog", back_populates="feedback_entries")


class NodeCategory(Base):
    __tablename__ = "node_categories"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    parent_id = Column(PortableUUID(), ForeignKey("node_categories.id", ondelete="SET NULL"))
    skill_area = Column(String, nullable=False)
    color_hex = Column(String, default="#4F46E5", nullable=False)


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(PortableUUID(), ForeignKey("node_categories.id", ondelete="SET NULL"))
    node_key = Column(String, nullable=False)
    display_label = Column(String, nullable=False)
    mastery_score = Column(Float, default=0.0, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    easiness_factor = Column(Float, default=2.5, nullable=False)
    interval_days = Column(Integer, default=1, nullable=False)
    next_review_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="knowledge_nodes")
    category = relationship("NodeCategory")

    __table_args__ = (UniqueConstraint("user_id", "node_key"),)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    xp_reward = Column(Integer, default=0, nullable=False)
    condition = Column(PortableJSON(), default={}, nullable=False)
    icon_slug = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id = Column(PortableUUID(), ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True)
    earned_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    achievement = relationship("Achievement")
