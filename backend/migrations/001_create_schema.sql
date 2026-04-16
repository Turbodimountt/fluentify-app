-- ============================================================
-- Fluentify — Full Database Schema Migration
-- Run this against your Supabase PostgreSQL database
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. Professional Contexts (must be first - referenced by user_profiles)
-- ============================================================
CREATE TABLE IF NOT EXISTS professional_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL UNIQUE,
    slug VARCHAR NOT NULL UNIQUE,
    vocabulary_tags TEXT[] DEFAULT '{}',
    scenario_templates JSONB DEFAULT '[]',
    icon_slug VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. Users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================
-- 3. User Profiles
-- ============================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    target_language VARCHAR NOT NULL DEFAULT 'en',
    native_language VARCHAR NOT NULL DEFAULT 'es',
    cefr_level VARCHAR NOT NULL DEFAULT 'A1',
    professional_context_id UUID REFERENCES professional_contexts(id) ON DELETE SET NULL,
    total_xp INTEGER NOT NULL DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,
    max_streak INTEGER NOT NULL DEFAULT 0,
    last_session_at TIMESTAMPTZ,
    correction_level VARCHAR NOT NULL DEFAULT 'medium',
    whisper_mode_default BOOLEAN NOT NULL DEFAULT FALSE,
    interface_language VARCHAR NOT NULL DEFAULT 'es',
    user_level VARCHAR NOT NULL DEFAULT 'Explorador',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 4. Sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR NOT NULL,
    professional_ctx VARCHAR,
    target_language VARCHAR NOT NULL,
    scenario_name VARCHAR,
    duration_seconds INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    messages_count INTEGER DEFAULT 0,
    errors_detected INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- ============================================================
-- 5. Conversation Logs
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    detected_errors JSONB DEFAULT '[]',
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_logs_session ON conversation_logs(session_id);

-- ============================================================
-- 6. Feedback Entries
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_log_id UUID NOT NULL REFERENCES conversation_logs(id) ON DELETE CASCADE,
    feedback_type VARCHAR NOT NULL DEFAULT 'grammar',
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    explanation TEXT NOT NULL,
    severity VARCHAR NOT NULL,
    was_helpful BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. Node Categories
-- ============================================================
CREATE TABLE IF NOT EXISTS node_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    parent_id UUID REFERENCES node_categories(id) ON DELETE SET NULL,
    skill_area VARCHAR NOT NULL,
    color_hex VARCHAR NOT NULL DEFAULT '#4F46E5'
);

-- ============================================================
-- 8. Knowledge Nodes
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES node_categories(id) ON DELETE SET NULL,
    node_key VARCHAR NOT NULL,
    display_label VARCHAR NOT NULL,
    mastery_score FLOAT NOT NULL DEFAULT 0.0,
    repetitions INTEGER NOT NULL DEFAULT 0,
    easiness_factor FLOAT NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 1,
    next_review_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, node_key)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_user ON knowledge_nodes(user_id);

-- ============================================================
-- 9. Achievements
-- ============================================================
CREATE TABLE IF NOT EXISTS achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    description TEXT NOT NULL,
    xp_reward INTEGER NOT NULL DEFAULT 0,
    condition JSONB NOT NULL DEFAULT '{}',
    icon_slug VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 10. User Achievements
-- ============================================================
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, achievement_id)
);

-- ============================================================
-- Enable Row Level Security (RLS)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
