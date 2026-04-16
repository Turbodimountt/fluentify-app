"""Quick script to check DB tables and create them + seed if needed."""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.models import (
    User, UserProfile, ProfessionalContext, Session, ConversationLog,
    FeedbackEntry, NodeCategory, KnowledgeNode, Achievement, UserAchievement
)


async def check_and_create():
    # 1. Check existing tables
    async with AsyncSessionLocal() as db:
        if "sqlite" in str(engine.url):
            r = await db.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ))
        else:
            r = await db.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
            ))
        tables = [row[0] for row in r.fetchall()]
        print(f"[INFO] Existing tables ({len(tables)}): {tables}")

    # 2. Create missing tables
    needs_tables = not set(["users", "user_profiles", "sessions", "achievements"]).issubset(set(tables))
    if needs_tables:
        print("[INFO] Creating missing tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[OK] Tables created!")

        # Re-check
        async with AsyncSessionLocal() as db:
            if "sqlite" in str(engine.url):
                r = await db.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ))
            else:
                r = await db.execute(text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
                ))
            tables = [row[0] for row in r.fetchall()]
            print(f"[INFO] Tables after creation ({len(tables)}): {tables}")
    else:
        print("[OK] All core tables already exist")

    # 3. Check seed data
    async with AsyncSessionLocal() as db:
        from sqlalchemy import func, select
        ctx_count = await db.execute(select(func.count()).select_from(ProfessionalContext))
        ach_count = await db.execute(select(func.count()).select_from(Achievement))
        cat_count = await db.execute(select(func.count()).select_from(NodeCategory))
        user_count = await db.execute(select(func.count()).select_from(User))

        ctx_n = ctx_count.scalar() or 0
        ach_n = ach_count.scalar() or 0
        cat_n = cat_count.scalar() or 0
        usr_n = user_count.scalar() or 0

        print(f"[DATA] Professional Contexts: {ctx_n}")
        print(f"[DATA] Achievements: {ach_n}")
        print(f"[DATA] Node Categories: {cat_n}")
        print(f"[DATA] Users: {usr_n}")

        if ctx_n == 0:
            print("[INFO] Seeding professional contexts...")
            await _seed_contexts(db)
        if ach_n == 0:
            print("[INFO] Seeding achievements...")
            await _seed_achievements(db)
        if cat_n == 0:
            print("[INFO] Seeding node categories...")
            await _seed_categories(db)
        if usr_n == 0:
            print("[INFO] Seeding test user...")
            await _seed_test_user(db)


async def _seed_test_user(db):
    from app.core.security import hash_password
    user = User(
        email="test@fluentify.com",
        hashed_password=hash_password("password123"),
        display_name="Usuario de Prueba",
        is_active=True
    )
    db.add(user)
    await db.flush()
    profile = UserProfile(user_id=user.id, native_language="es", target_language="en", cefr_level="A1")
    db.add(profile)
    await db.commit()
    print("[OK] Test user created (test@fluentify.com / password123)")


async def _seed_contexts(db):
    contexts_data = [
        ("General", "general", ["everyday", "travel", "social"], "public", [
            {"name": "Coffee Shop Chat", "description": "Casual conversation at a coffee shop.", "ai_role": "Friendly barista", "difficulty": "A1"},
            {"name": "Travel Planning", "description": "Planning your next vacation.", "ai_role": "Travel agent", "difficulty": "A2"},
            {"name": "Job Interview", "description": "Job interview practice.", "ai_role": "HR interviewer", "difficulty": "B1"},
            {"name": "Apartment Hunting", "description": "Looking at an apartment.", "ai_role": "Landlord", "difficulty": "A2"},
            {"name": "Restaurant Reservation", "description": "Making a dinner reservation.", "ai_role": "Restaurant host", "difficulty": "A1"},
        ]),
        ("Medicina", "medicina", ["anatomy", "diagnosis", "treatment"], "medical_services", [
            {"name": "Patient Consultation", "description": "A patient describes symptoms.", "ai_role": "Patient with flu symptoms", "difficulty": "B1"},
            {"name": "Emergency Room", "description": "Receiving a patient with chest pain.", "ai_role": "Worried patient", "difficulty": "B2"},
            {"name": "Medical Conference", "description": "Presenting a case study.", "ai_role": "Fellow doctor", "difficulty": "C1"},
            {"name": "Pharmacy Consultation", "description": "Patient asks about medications.", "ai_role": "Patient with prescriptions", "difficulty": "B1"},
            {"name": "Telemedicine Call", "description": "Follow-up video call.", "ai_role": "Post-surgery patient", "difficulty": "B1"},
        ]),
        ("Ingenieria", "ingenieria", ["software", "systems", "agile"], "engineering", [
            {"name": "Sprint Planning", "description": "Leading a sprint planning meeting.", "ai_role": "Senior developer", "difficulty": "B1"},
            {"name": "Code Review", "description": "Reviewing code with a colleague.", "ai_role": "Junior developer", "difficulty": "B2"},
            {"name": "Client Demo", "description": "Presenting a feature to a client.", "ai_role": "Client executive", "difficulty": "B2"},
            {"name": "Tech Interview", "description": "Conducting a technical interview.", "ai_role": "Candidate", "difficulty": "C1"},
            {"name": "Bug Report", "description": "Explaining a production bug.", "ai_role": "Engineering manager", "difficulty": "B1"},
        ]),
        ("Finanzas", "finanzas", ["investment", "banking", "markets"], "account_balance", [
            {"name": "Investment Pitch", "description": "Pitching an investment.", "ai_role": "Wealthy client", "difficulty": "B2"},
            {"name": "Budget Review", "description": "Presenting quarterly budget.", "ai_role": "Board member", "difficulty": "C1"},
            {"name": "Loan Consultation", "description": "Discussing mortgage options.", "ai_role": "Homebuyer", "difficulty": "B1"},
            {"name": "Market Analysis", "description": "Presenting market trends.", "ai_role": "Trader", "difficulty": "B2"},
            {"name": "Tax Advisory", "description": "Tax planning help.", "ai_role": "Entrepreneur", "difficulty": "B1"},
        ]),
        ("Videojuegos", "videojuegos", ["game-design", "esports", "streaming"], "sports_esports", [
            {"name": "Game Design Review", "description": "Presenting your game design.", "ai_role": "Creative director", "difficulty": "B1"},
            {"name": "Esports Commentary", "description": "Commentating a match.", "ai_role": "Co-caster", "difficulty": "B2"},
            {"name": "Community Management", "description": "Handling community feedback.", "ai_role": "Community member", "difficulty": "B1"},
            {"name": "Publisher Meeting", "description": "Pitching your indie game.", "ai_role": "Publisher", "difficulty": "B2"},
            {"name": "QA Bug Triage", "description": "Discussing testing bugs.", "ai_role": "QA tester", "difficulty": "B1"},
        ]),
        ("Turismo", "turismo", ["hospitality", "travel", "service"], "flight_takeoff", [
            {"name": "Hotel Check-in", "description": "Guest checking in.", "ai_role": "Tourist", "difficulty": "A2"},
            {"name": "City Tour Guide", "description": "Giving a walking tour.", "ai_role": "Curious tourist", "difficulty": "B1"},
            {"name": "Travel Emergency", "description": "Tourist lost passport.", "ai_role": "Distressed tourist", "difficulty": "B1"},
            {"name": "Restaurant Service", "description": "Serving at restaurant.", "ai_role": "Diner", "difficulty": "A2"},
            {"name": "Tour Package Sales", "description": "Selling vacation packages.", "ai_role": "Couple", "difficulty": "B1"},
        ]),
    ]
    for name, slug, tags, icon, templates in contexts_data:
        ctx = ProfessionalContext(
            name=name, slug=slug, vocabulary_tags=tags,
            icon_slug=icon, scenario_templates=templates
        )
        db.add(ctx)
    await db.commit()
    print(f"[OK] Seeded {len(contexts_data)} professional contexts")


async def _seed_achievements(db):
    achs = [
        ("first_session", "Primera Sesion", "Completa tu primera sesion", 50, {"type": "session_count", "value": 1}, "star"),
        ("five_sessions", "Practicante", "Completa 5 sesiones", 100, {"type": "session_count", "value": 5}, "local_fire_department"),
        ("twenty_sessions", "Dedicado", "Completa 20 sesiones", 250, {"type": "session_count", "value": 20}, "military_tech"),
        ("streak_3", "En Racha", "Racha de 3 dias", 75, {"type": "streak", "value": 3}, "whatshot"),
        ("streak_7", "Semana Perfecta", "Racha de 7 dias", 200, {"type": "streak", "value": 7}, "local_fire_department"),
        ("streak_30", "Mes Imparable", "Racha de 30 dias", 1000, {"type": "streak", "value": 30}, "emoji_events"),
        ("xp_500", "Aventurero", "Acumula 500 XP", 50, {"type": "total_xp", "value": 500}, "workspace_premium"),
        ("xp_5000", "Artesano del Idioma", "Acumula 5000 XP", 200, {"type": "total_xp", "value": 5000}, "workspace_premium"),
        ("first_roleplay", "Actor Novato", "Primera sesion Roleplay", 75, {"type": "roleplay_count", "value": 1}, "theater_comedy"),
        ("first_whisper", "Susurro Inicial", "Primera sesion Susurro", 75, {"type": "whisper_count", "value": 1}, "mic"),
        ("nodes_10", "Explorador del Conocimiento", "Domina 10 nodos", 150, {"type": "mastered_nodes", "value": 10}, "auto_awesome"),
        ("nodes_50", "Constelacion Brillante", "Domina 50 nodos", 500, {"type": "mastered_nodes", "value": 50}, "stars"),
    ]
    for slug, name, desc, xp, cond, icon in achs:
        db.add(Achievement(slug=slug, name=name, description=desc, xp_reward=xp, condition=cond, icon_slug=icon))
    await db.commit()
    print(f"[OK] Seeded {len(achs)} achievements")


async def _seed_categories(db):
    cats = [
        ("Gramatica Basica", "grammar", "#6C5CE7"),
        ("Gramatica Intermedia", "grammar", "#A29BFE"),
        ("Vocabulario General", "vocabulary", "#00CEC9"),
        ("Vocabulario Profesional", "vocabulary", "#55EFC4"),
        ("Fonetica", "phonetics", "#FD79A8"),
        ("Escritura Kanji", "writing", "#FDCB6E"),
        ("Escritura Cirilica", "writing", "#E17055"),
        ("Cultura", "culture", "#74B9FF"),
    ]
    for name, area, color in cats:
        db.add(NodeCategory(name=name, skill_area=area, color_hex=color))
    await db.commit()
    print(f"[OK] Seeded {len(cats)} node categories")


if __name__ == "__main__":
    asyncio.run(check_and_create())
