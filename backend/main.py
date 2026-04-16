"""
Fluentify Backend — Main Application Entry Point
FastAPI app with CORS, rate limiting, routers, and WebSocket.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db, engine
from app.middleware.rate_limiter import limiter
from app.routers import auth, users, conversation, progress, voice, writing
from app.websocket.conversation_ws import conversation_websocket


# ============================================================
# Lifespan — Init DB on startup
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup (dev mode)."""
    await init_db()
    # Seed data for SQLite dev mode
    await _seed_dev_data()
    yield


async def _seed_dev_data():
    """Insert seed data if tables are empty (SQLite dev mode)."""
    from app.core.database import AsyncSessionLocal
    from app.models.models import ProfessionalContext, Achievement, NodeCategory
    from sqlalchemy import select, func
    import json

    async with AsyncSessionLocal() as db:
        # Check if contexts already exist
        count = await db.execute(select(func.count()).select_from(ProfessionalContext))
        if (count.scalar() or 0) > 0:
            return  # Already seeded

        # Seed Professional Contexts
        contexts = [
            ProfessionalContext(
                name="General", slug="general",
                vocabulary_tags=["everyday", "travel", "social", "culture"],
                icon_slug="public",
                scenario_templates=[
                    {"name": "Coffee Shop Chat", "description": "You are having a casual conversation at a coffee shop.", "ai_role": "Friendly barista", "difficulty": "A1"},
                    {"name": "Travel Planning", "description": "You are at a travel agency planning your vacation.", "ai_role": "Travel agent", "difficulty": "A2"},
                    {"name": "Job Interview", "description": "You are in a job interview.", "ai_role": "HR interviewer", "difficulty": "B1"},
                    {"name": "Apartment Hunting", "description": "You are meeting a landlord about an apartment.", "ai_role": "Property landlord", "difficulty": "A2"},
                    {"name": "Restaurant Reservation", "description": "You are making a dinner reservation.", "ai_role": "Restaurant host", "difficulty": "A1"},
                ],
            ),
            ProfessionalContext(
                name="Medicina", slug="medicina",
                vocabulary_tags=["anatomy", "diagnosis", "treatment", "patient-care"],
                icon_slug="medical_services",
                scenario_templates=[
                    {"name": "Patient Consultation", "description": "A patient describes symptoms to you.", "ai_role": "Patient with flu-like symptoms", "difficulty": "B1"},
                    {"name": "Emergency Room", "description": "You receive a patient with chest pain.", "ai_role": "Worried patient", "difficulty": "B2"},
                    {"name": "Medical Conference", "description": "You present a case study at a conference.", "ai_role": "Fellow doctor asking questions", "difficulty": "C1"},
                    {"name": "Pharmacy Consultation", "description": "A patient asks about medication interactions.", "ai_role": "Patient with prescriptions", "difficulty": "B1"},
                    {"name": "Telemedicine Call", "description": "You conduct a follow-up video call.", "ai_role": "Post-surgery patient", "difficulty": "B1"},
                ],
            ),
            ProfessionalContext(
                name="Ingeniería", slug="ingenieria",
                vocabulary_tags=["software", "systems", "architecture", "agile"],
                icon_slug="engineering",
                scenario_templates=[
                    {"name": "Sprint Planning", "description": "You lead a sprint planning meeting.", "ai_role": "Senior developer", "difficulty": "B1"},
                    {"name": "Code Review", "description": "You review code with a colleague.", "ai_role": "Junior developer", "difficulty": "B2"},
                    {"name": "Client Demo", "description": "You present a new feature to a client.", "ai_role": "Client executive", "difficulty": "B2"},
                    {"name": "Tech Interview", "description": "You conduct a technical interview.", "ai_role": "Candidate", "difficulty": "C1"},
                    {"name": "Bug Report", "description": "You explain a production bug to your manager.", "ai_role": "Engineering manager", "difficulty": "B1"},
                ],
            ),
            ProfessionalContext(
                name="Finanzas", slug="finanzas",
                vocabulary_tags=["investment", "banking", "accounting", "markets"],
                icon_slug="account_balance",
                scenario_templates=[
                    {"name": "Investment Pitch", "description": "You pitch an investment opportunity.", "ai_role": "Wealthy potential client", "difficulty": "B2"},
                    {"name": "Budget Review", "description": "You present the quarterly budget.", "ai_role": "Board member", "difficulty": "C1"},
                    {"name": "Loan Consultation", "description": "A client discusses mortgage options.", "ai_role": "First-time homebuyer", "difficulty": "B1"},
                    {"name": "Market Analysis", "description": "You present market trends.", "ai_role": "Trader", "difficulty": "B2"},
                    {"name": "Tax Advisory", "description": "A business owner needs tax planning help.", "ai_role": "Entrepreneur", "difficulty": "B1"},
                ],
            ),
            ProfessionalContext(
                name="Videojuegos", slug="videojuegos",
                vocabulary_tags=["game-design", "development", "esports", "streaming"],
                icon_slug="sports_esports",
                scenario_templates=[
                    {"name": "Game Design Review", "description": "You present your game design document.", "ai_role": "Creative director", "difficulty": "B1"},
                    {"name": "Esports Commentary", "description": "You commentate a live esports match.", "ai_role": "Co-caster", "difficulty": "B2"},
                    {"name": "Community Management", "description": "You handle community feedback.", "ai_role": "Passionate community member", "difficulty": "B1"},
                    {"name": "Publisher Meeting", "description": "You pitch your indie game.", "ai_role": "Publisher evaluating funding", "difficulty": "B2"},
                    {"name": "QA Bug Triage", "description": "You discuss bugs found during testing.", "ai_role": "QA tester", "difficulty": "B1"},
                ],
            ),
            ProfessionalContext(
                name="Turismo", slug="turismo",
                vocabulary_tags=["hospitality", "travel", "tourism", "service"],
                icon_slug="flight_takeoff",
                scenario_templates=[
                    {"name": "Hotel Check-in", "description": "A guest needs help checking in.", "ai_role": "International tourist", "difficulty": "A2"},
                    {"name": "City Tour Guide", "description": "You give a walking tour.", "ai_role": "Curious tourist", "difficulty": "B1"},
                    {"name": "Travel Emergency", "description": "A tourist lost their passport.", "ai_role": "Distressed tourist", "difficulty": "B1"},
                    {"name": "Restaurant Service", "description": "You are a waiter at an international restaurant.", "ai_role": "Diner", "difficulty": "A2"},
                    {"name": "Tour Package Sales", "description": "You sell vacation packages.", "ai_role": "Couple looking for a getaway", "difficulty": "B1"},
                ],
            ),
        ]
        for ctx in contexts:
            db.add(ctx)

        # Seed Node Categories
        categories = [
            NodeCategory(name="Gramática Básica", skill_area="grammar", color_hex="#6C5CE7"),
            NodeCategory(name="Gramática Intermedia", skill_area="grammar", color_hex="#A29BFE"),
            NodeCategory(name="Vocabulario General", skill_area="vocabulary", color_hex="#00CEC9"),
            NodeCategory(name="Vocabulario Profesional", skill_area="vocabulary", color_hex="#55EFC4"),
            NodeCategory(name="Fonética", skill_area="phonetics", color_hex="#FD79A8"),
            NodeCategory(name="Escritura Kanji", skill_area="writing", color_hex="#FDCB6E"),
            NodeCategory(name="Escritura Cirílica", skill_area="writing", color_hex="#E17055"),
            NodeCategory(name="Cultura", skill_area="culture", color_hex="#74B9FF"),
        ]
        for cat in categories:
            db.add(cat)

        # Seed Achievements
        achievements = [
            Achievement(slug="first_session", name="Primera Sesión", description="Completa tu primera sesión de práctica", xp_reward=50, condition={"type": "session_count", "value": 1}, icon_slug="star"),
            Achievement(slug="five_sessions", name="Practicante", description="Completa 5 sesiones de práctica", xp_reward=100, condition={"type": "session_count", "value": 5}, icon_slug="local_fire_department"),
            Achievement(slug="twenty_sessions", name="Dedicado", description="Completa 20 sesiones de práctica", xp_reward=250, condition={"type": "session_count", "value": 20}, icon_slug="military_tech"),
            Achievement(slug="streak_3", name="En Racha", description="Mantén una racha de 3 días consecutivos", xp_reward=75, condition={"type": "streak", "value": 3}, icon_slug="whatshot"),
            Achievement(slug="streak_7", name="Semana Perfecta", description="Mantén una racha de 7 días consecutivos", xp_reward=200, condition={"type": "streak", "value": 7}, icon_slug="local_fire_department"),
            Achievement(slug="streak_30", name="Mes Imparable", description="Mantén una racha de 30 días consecutivos", xp_reward=1000, condition={"type": "streak", "value": 30}, icon_slug="emoji_events"),
            Achievement(slug="xp_500", name="Aventurero", description="Acumula 500 XP en total", xp_reward=50, condition={"type": "total_xp", "value": 500}, icon_slug="workspace_premium"),
            Achievement(slug="xp_5000", name="Artesano del Idioma", description="Acumula 5,000 XP en total", xp_reward=200, condition={"type": "total_xp", "value": 5000}, icon_slug="workspace_premium"),
            Achievement(slug="first_roleplay", name="Actor Novato", description="Completa tu primera sesión de Roleplay", xp_reward=75, condition={"type": "roleplay_count", "value": 1}, icon_slug="theater_comedy"),
            Achievement(slug="first_whisper", name="Susurro Inicial", description="Completa tu primera sesión en Modo Susurro", xp_reward=75, condition={"type": "whisper_count", "value": 1}, icon_slug="mic"),
            Achievement(slug="nodes_10", name="Explorador del Conocimiento", description="Domina 10 nodos de conocimiento", xp_reward=150, condition={"type": "mastered_nodes", "value": 10}, icon_slug="auto_awesome"),
            Achievement(slug="nodes_50", name="Constelación Brillante", description="Domina 50 nodos de conocimiento", xp_reward=500, condition={"type": "mastered_nodes", "value": 50}, icon_slug="stars"),
        ]
        for ach in achievements:
            db.add(ach)

        await db.commit()


# ============================================================
# App Initialization
# ============================================================
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Fluentify — AI-Powered Language Learning Platform API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ============================================================
# Middleware
# ============================================================

# Rate Limiting (RNF-09)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Routers
# ============================================================
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversation.router)
app.include_router(progress.router)
app.include_router(voice.router)
app.include_router(writing.router)

# ============================================================
# WebSocket
# ============================================================
app.websocket("/ws/conversation")(conversation_websocket)

# ============================================================
# Health Check
# ============================================================
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "ai_mode": "live" if not settings.is_ai_mock_mode else "mock",
        "stt_mode": "live" if not settings.is_stt_mock_mode else "mock",
        "tts_mode": "live" if not settings.is_tts_mock_mode else "mock",
    }


@app.get("/")
async def root():
    return {
        "message": f"¡Bienvenido a {settings.app_name}! 🌍",
        "docs": "/docs" if settings.debug else "Disabled in production",
        "version": settings.app_version,
    }
