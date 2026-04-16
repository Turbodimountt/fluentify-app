"""Create schema using individual transactions."""
import asyncio
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

import os
from dotenv import load_dotenv

load_dotenv()

# Get DB URL from env or fallback
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    PASSWORD = quote_plus("vYZZJufsCRFi6s8T")
    PROJECT = "ogdemdghhuntuuxvopdd"
    DB_URL = f"postgresql+asyncpg://postgres.{PROJECT}:{PASSWORD}@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

if "asyncpg" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://")

STATEMENTS = [
    # Extension
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
    
    # Users
    """CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR UNIQUE NOT NULL,
        hashed_password VARCHAR NOT NULL,
        display_name VARCHAR NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    
    # Professional Contexts
    """CREATE TABLE IF NOT EXISTS professional_contexts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR UNIQUE NOT NULL,
        slug VARCHAR UNIQUE NOT NULL,
        vocabulary_tags TEXT[] DEFAULT '{}',
        scenario_templates JSONB DEFAULT '[]',
        icon_slug VARCHAR,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    
    # User Profiles
    """CREATE TABLE IF NOT EXISTS user_profiles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        target_language VARCHAR NOT NULL DEFAULT 'en',
        native_language VARCHAR NOT NULL DEFAULT 'es',
        cefr_level VARCHAR NOT NULL DEFAULT 'A1',
        professional_context_id UUID REFERENCES professional_contexts(id) ON DELETE SET NULL,
        total_xp INTEGER NOT NULL DEFAULT 0,
        current_streak INTEGER NOT NULL DEFAULT 0,
        max_streak INTEGER NOT NULL DEFAULT 0,
        last_session_at TIMESTAMPTZ,
        correction_level VARCHAR NOT NULL DEFAULT 'medium',
        whisper_mode_default BOOLEAN NOT NULL DEFAULT false,
        interface_language VARCHAR NOT NULL DEFAULT 'es',
        user_level VARCHAR NOT NULL DEFAULT 'Explorador',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    
    # Sessions
    """CREATE TABLE IF NOT EXISTS sessions (
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
        started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        ended_at TIMESTAMPTZ,
        is_active BOOLEAN NOT NULL DEFAULT true
    )""",
    "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)",
    
    # Conversation Logs
    """CREATE TABLE IF NOT EXISTS conversation_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
        turn_number INTEGER NOT NULL,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        detected_errors JSONB DEFAULT '[]',
        confidence_score FLOAT DEFAULT 0.0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS idx_convlogs_session ON conversation_logs(session_id)",
    
    # Feedback Entries
    """CREATE TABLE IF NOT EXISTS feedback_entries (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        conversation_log_id UUID NOT NULL REFERENCES conversation_logs(id) ON DELETE CASCADE,
        feedback_type VARCHAR NOT NULL DEFAULT 'grammar',
        original_text TEXT NOT NULL,
        corrected_text TEXT NOT NULL,
        explanation TEXT NOT NULL,
        severity VARCHAR NOT NULL,
        was_helpful BOOLEAN,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    
    # Node Categories
    """CREATE TABLE IF NOT EXISTS node_categories (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR NOT NULL,
        parent_id UUID REFERENCES node_categories(id) ON DELETE SET NULL,
        skill_area VARCHAR NOT NULL,
        color_hex VARCHAR NOT NULL DEFAULT '#4F46E5'
    )""",
    
    # Knowledge Nodes
    """CREATE TABLE IF NOT EXISTS knowledge_nodes (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        category_id UUID REFERENCES node_categories(id) ON DELETE SET NULL,
        node_key VARCHAR NOT NULL,
        display_label VARCHAR NOT NULL,
        mastery_score FLOAT NOT NULL DEFAULT 0.0,
        repetitions INTEGER NOT NULL DEFAULT 0,
        easiness_factor FLOAT NOT NULL DEFAULT 2.5,
        interval_days INTEGER NOT NULL DEFAULT 1,
        next_review_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE(user_id, node_key)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_knodes_user ON knowledge_nodes(user_id)",
    
    # Achievements
    """CREATE TABLE IF NOT EXISTS achievements (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        slug VARCHAR UNIQUE NOT NULL,
        name VARCHAR NOT NULL,
        description TEXT NOT NULL,
        xp_reward INTEGER NOT NULL DEFAULT 0,
        condition JSONB NOT NULL DEFAULT '{}',
        icon_slug VARCHAR,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""",
    
    # User Achievements
    """CREATE TABLE IF NOT EXISTS user_achievements (
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
        earned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        PRIMARY KEY (user_id, achievement_id)
    )""",
]

SEED_STATEMENTS = [
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('General', 'general', ARRAY['everyday','travel','social','culture'], 
     '[{"name":"Coffee Shop Chat","description":"Casual conversation at a coffee shop.","ai_role":"Friendly barista","difficulty":"A1"},{"name":"Travel Planning","description":"Planning your vacation.","ai_role":"Travel agent","difficulty":"A2"},{"name":"Job Interview","description":"A standard job interview.","ai_role":"HR interviewer","difficulty":"B1"},{"name":"Apartment Hunting","description":"Meeting a landlord.","ai_role":"Property landlord","difficulty":"A2"},{"name":"Restaurant Reservation","description":"Making a dinner reservation.","ai_role":"Restaurant host","difficulty":"A1"}]',
     'public')
    ON CONFLICT (slug) DO NOTHING""",
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('Medicina', 'medicina', ARRAY['anatomy','diagnosis','treatment','patient-care'],
     '[{"name":"Patient Consultation","description":"A patient describes symptoms.","ai_role":"Patient with flu-like symptoms","difficulty":"B1"},{"name":"Emergency Room","description":"A patient with chest pain.","ai_role":"Worried patient","difficulty":"B2"},{"name":"Medical Conference","description":"Presenting a case study.","ai_role":"Fellow doctor","difficulty":"C1"},{"name":"Pharmacy Consultation","description":"Medication interactions.","ai_role":"Patient with prescriptions","difficulty":"B1"},{"name":"Telemedicine Call","description":"Follow-up video call.","ai_role":"Post-surgery patient","difficulty":"B1"}]',
     'medical_services')
    ON CONFLICT (slug) DO NOTHING""",
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('Ingenieria', 'ingenieria', ARRAY['software','systems','architecture','agile'],
     '[{"name":"Sprint Planning","description":"Leading a sprint planning meeting.","ai_role":"Senior developer","difficulty":"B1"},{"name":"Code Review","description":"Reviewing code.","ai_role":"Junior developer","difficulty":"B2"},{"name":"Client Demo","description":"Presenting a feature.","ai_role":"Client executive","difficulty":"B2"},{"name":"Tech Interview","description":"Conducting a technical interview.","ai_role":"Candidate","difficulty":"C1"},{"name":"Bug Report","description":"Explaining a production bug.","ai_role":"Engineering manager","difficulty":"B1"}]',
     'engineering')
    ON CONFLICT (slug) DO NOTHING""",
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('Finanzas', 'finanzas', ARRAY['investment','banking','accounting','markets'],
     '[{"name":"Investment Pitch","description":"Pitching an investment.","ai_role":"Wealthy client","difficulty":"B2"},{"name":"Budget Review","description":"Presenting budget.","ai_role":"Board member","difficulty":"C1"},{"name":"Loan Consultation","description":"Mortgage options.","ai_role":"First-time homebuyer","difficulty":"B1"},{"name":"Market Analysis","description":"Market trends.","ai_role":"Trader","difficulty":"B2"},{"name":"Tax Advisory","description":"Tax planning.","ai_role":"Entrepreneur","difficulty":"B1"}]',
     'account_balance')
    ON CONFLICT (slug) DO NOTHING""",
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('Videojuegos', 'videojuegos', ARRAY['game-design','development','esports','streaming'],
     '[{"name":"Game Design Review","description":"Presenting game design.","ai_role":"Creative director","difficulty":"B1"},{"name":"Esports Commentary","description":"Commentating a match.","ai_role":"Co-caster","difficulty":"B2"},{"name":"Community Management","description":"Handling feedback.","ai_role":"Community member","difficulty":"B1"},{"name":"Publisher Meeting","description":"Pitching indie game.","ai_role":"Publisher","difficulty":"B2"},{"name":"QA Bug Triage","description":"Discussing bugs.","ai_role":"QA tester","difficulty":"B1"}]',
     'sports_esports')
    ON CONFLICT (slug) DO NOTHING""",
    """INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
    ('Turismo', 'turismo', ARRAY['hospitality','travel','tourism','service'],
     '[{"name":"Hotel Check-in","description":"Helping a guest.","ai_role":"International tourist","difficulty":"A2"},{"name":"City Tour Guide","description":"Giving a walking tour.","ai_role":"Curious tourist","difficulty":"B1"},{"name":"Travel Emergency","description":"Tourist lost passport.","ai_role":"Distressed tourist","difficulty":"B1"},{"name":"Restaurant Service","description":"Serving at restaurant.","ai_role":"Diner","difficulty":"A2"},{"name":"Tour Package Sales","description":"Selling vacation packages.","ai_role":"Couple","difficulty":"B1"}]',
     'flight_takeoff')
    ON CONFLICT (slug) DO NOTHING""",
    
    # Node Categories
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Gramatica Basica', 'grammar', '#6C5CE7' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Gramatica Basica')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Gramatica Intermedia', 'grammar', '#A29BFE' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Gramatica Intermedia')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Vocabulario General', 'vocabulary', '#00CEC9' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Vocabulario General')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Vocabulario Profesional', 'vocabulary', '#55EFC4' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Vocabulario Profesional')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Fonetica', 'phonetics', '#FD79A8' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Fonetica')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Escritura Kanji', 'writing', '#FDCB6E' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Escritura Kanji')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Escritura Cirilica', 'writing', '#E17055' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Escritura Cirilica')",
    "INSERT INTO node_categories (name, skill_area, color_hex) SELECT 'Cultura', 'culture', '#74B9FF' WHERE NOT EXISTS (SELECT 1 FROM node_categories WHERE name='Cultura')",
    
    # Achievements
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('first_session', 'Primera Sesion', 'Completa tu primera sesion', 50, '{\"type\":\"session_count\",\"value\":1}', 'star') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('five_sessions', 'Practicante', 'Completa 5 sesiones', 100, '{\"type\":\"session_count\",\"value\":5}', 'local_fire_department') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('twenty_sessions', 'Dedicado', 'Completa 20 sesiones', 250, '{\"type\":\"session_count\",\"value\":20}', 'military_tech') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('streak_3', 'En Racha', '3 dias consecutivos', 75, '{\"type\":\"streak\",\"value\":3}', 'whatshot') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('streak_7', 'Semana Perfecta', '7 dias consecutivos', 200, '{\"type\":\"streak\",\"value\":7}', 'local_fire_department') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('streak_30', 'Mes Imparable', '30 dias consecutivos', 1000, '{\"type\":\"streak\",\"value\":30}', 'emoji_events') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('xp_500', 'Aventurero', 'Acumula 500 XP', 50, '{\"type\":\"total_xp\",\"value\":500}', 'workspace_premium') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('xp_5000', 'Artesano del Idioma', 'Acumula 5000 XP', 200, '{\"type\":\"total_xp\",\"value\":5000}', 'workspace_premium') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('first_roleplay', 'Actor Novato', 'Primera sesion Roleplay', 75, '{\"type\":\"roleplay_count\",\"value\":1}', 'theater_comedy') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('first_whisper', 'Susurro Inicial', 'Primera sesion Susurro', 75, '{\"type\":\"whisper_count\",\"value\":1}', 'mic') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('nodes_10', 'Explorador del Conocimiento', 'Domina 10 nodos', 150, '{\"type\":\"mastered_nodes\",\"value\":10}', 'auto_awesome') ON CONFLICT (slug) DO NOTHING",
    "INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES ('nodes_50', 'Constelacion Brillante', 'Domina 50 nodos', 500, '{\"type\":\"mastered_nodes\",\"value\":50}', 'stars') ON CONFLICT (slug) DO NOTHING",
]

async def main():
    engine = create_async_engine(
        DB_URL, echo=False,
        connect_args={"prepared_statement_cache_size": 0}
    )
    
    print("1/3 Creating tables...")
    for i, stmt in enumerate(STATEMENTS):
        async with engine.begin() as conn:
            try:
                await conn.execute(text(stmt))
                print(f"  [{i+1}/{len(STATEMENTS)}] OK")
            except Exception as e:
                err = str(e).split('\n')[0][:120]
                print(f"  [{i+1}/{len(STATEMENTS)}] WARN: {err}")
    
    print("\n2/3 Seeding data...")
    for i, stmt in enumerate(SEED_STATEMENTS):
        async with engine.begin() as conn:
            try:
                await conn.execute(text(stmt))
                print(f"  [{i+1}/{len(SEED_STATEMENTS)}] OK")
            except Exception as e:
                err = str(e).split('\n')[0][:120]
                print(f"  [{i+1}/{len(SEED_STATEMENTS)}] WARN: {err}")
    
    print("\n3/3 Verifying...")
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        ))
        tables = [r[0] for r in result.fetchall()]
        print(f"  Tables ({len(tables)}):")
        for t in tables:
            try:
                cnt = await conn.execute(text(f'SELECT count(*) FROM "{t}"'))
                count = cnt.scalar()
                print(f"    {t}: {count} rows")
            except:
                print(f"    {t}")
    
    await engine.dispose()
    print("\nDone!")

asyncio.run(main())
