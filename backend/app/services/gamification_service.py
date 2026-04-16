"""
Fluentify — Gamification Service
XP calculation, SM-2 algorithm for spaced repetition, streak management, achievements.
"""
import uuid
import math
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.models import (
    UserProfile, KnowledgeNode, Achievement,
    UserAchievement, Session, NodeCategory
)


# Level thresholds
LEVEL_THRESHOLDS = {
    "Explorador": 0,
    "Aventurero": 500,
    "Navegante": 2000,
    "Artesano": 5000,
    "Erudito": 12000,
    "Sabio": 25000,
    "Maestro": 50000,
}


def calculate_level(total_xp: int) -> str:
    """Determine user level based on total XP."""
    level = "Explorador"
    for name, threshold in LEVEL_THRESHOLDS.items():
        if total_xp >= threshold:
            level = name
    return level


def sm2_algorithm(
    quality: int,  # 0-5 rating of recall quality
    repetitions: int,
    easiness_factor: float,
    interval_days: int,
) -> tuple[int, float, int]:
    """
    SuperMemo 2 Algorithm for spaced repetition.
    Returns: (new_repetitions, new_easiness_factor, new_interval_days)
    """
    if quality >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * easiness_factor)
        new_repetitions = repetitions + 1
    else:
        new_repetitions = 0
        new_interval = 1

    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    return new_repetitions, new_ef, new_interval


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def award_xp(self, user_id: str, xp_amount: int) -> dict:
        """Award XP to a user and update their level."""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == uid)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("Perfil no encontrado")

        profile.total_xp += xp_amount
        new_level = calculate_level(profile.total_xp)
        level_changed = new_level != profile.user_level
        profile.user_level = new_level

        await self.db.flush()

        return {
            "total_xp": profile.total_xp,
            "xp_awarded": xp_amount,
            "user_level": new_level,
            "level_changed": level_changed,
        }

    async def update_streak(self, user_id: str) -> dict:
        """Update user's streak. Should be called when a session is completed."""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == uid)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError("Perfil no encontrado")

        now = datetime.now(timezone.utc)

        if profile.last_session_at:
            hours_since = (now - profile.last_session_at).total_seconds() / 3600
            if hours_since > 48:
                # Streak broken (more than 48h)
                profile.current_streak = 1
            elif hours_since > 20:
                # New day, increment streak
                profile.current_streak += 1
            # else: same day, no change
        else:
            profile.current_streak = 1

        if profile.current_streak > profile.max_streak:
            profile.max_streak = profile.current_streak

        profile.last_session_at = now
        await self.db.flush()

        return {
            "current_streak": profile.current_streak,
            "max_streak": profile.max_streak,
            "streak_broken": profile.current_streak == 1 and (profile.last_session_at is not None),
        }

    async def update_knowledge_node(
        self, user_id: str, node_key: str, display_label: str,
        quality: int, category_id: str | None = None
    ) -> KnowledgeNode:
        """Update a knowledge node using SM-2 algorithm."""
        uid = uuid.UUID(user_id)

        result = await self.db.execute(
            select(KnowledgeNode).where(
                and_(KnowledgeNode.user_id == uid, KnowledgeNode.node_key == node_key)
            )
        )
        node = result.scalar_one_or_none()

        if not node:
            node = KnowledgeNode(
                id=uuid.uuid4(),
                user_id=uid,
                node_key=node_key,
                display_label=display_label,
                category_id=uuid.UUID(category_id) if category_id else None,
            )
            self.db.add(node)
            await self.db.flush()

        new_reps, new_ef, new_interval = sm2_algorithm(
            quality, node.repetitions, node.easiness_factor, node.interval_days
        )

        node.repetitions = new_reps
        node.easiness_factor = new_ef
        node.interval_days = new_interval
        node.mastery_score = min(1.0, quality / 5.0)
        node.next_review_at = datetime.now(timezone.utc) + timedelta(days=new_interval)
        node.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        return node

    async def get_stats(self, user_id: str) -> dict:
        """Get comprehensive stats for a user."""
        uid = uuid.UUID(user_id)

        # Profile
        profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == uid)
        )
        profile = profile_result.scalar_one_or_none()
        if not profile:
            raise ValueError("Perfil no encontrado")

        # Session count
        session_count = await self.db.execute(
            select(func.count()).select_from(Session).where(Session.user_id == uid)
        )
        total_sessions = session_count.scalar() or 0

        # Practice time
        time_result = await self.db.execute(
            select(func.sum(Session.duration_seconds)).where(Session.user_id == uid)
        )
        total_seconds = time_result.scalar() or 0

        # Knowledge nodes stats
        mastered = await self.db.execute(
            select(func.count()).select_from(KnowledgeNode).where(
                and_(KnowledgeNode.user_id == uid, KnowledgeNode.mastery_score >= 0.8)
            )
        )
        nodes_mastered = mastered.scalar() or 0

        pending = await self.db.execute(
            select(func.count()).select_from(KnowledgeNode).where(
                and_(
                    KnowledgeNode.user_id == uid,
                    KnowledgeNode.next_review_at <= datetime.now(timezone.utc)
                )
            )
        )
        nodes_pending = pending.scalar() or 0

        # Error rate
        total_errors = await self.db.execute(
            select(func.sum(Session.errors_detected)).where(Session.user_id == uid)
        )
        total_msgs = await self.db.execute(
            select(func.sum(Session.messages_count)).where(Session.user_id == uid)
        )
        errors = total_errors.scalar() or 0
        msgs = total_msgs.scalar() or 1
        error_rate = round(errors / msgs, 2) if msgs > 0 else 0.0

        return {
            "total_xp": profile.total_xp,
            "current_streak": profile.current_streak,
            "max_streak": profile.max_streak,
            "user_level": profile.user_level,
            "sessions_count": total_sessions,
            "nodes_mastered": nodes_mastered,
            "nodes_pending_review": nodes_pending,
            "total_practice_minutes": total_seconds // 60,
            "error_rate": error_rate,
        }

    async def get_knowledge_nodes(self, user_id: str) -> list[dict]:
        """Get all knowledge nodes for a user with category info."""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(KnowledgeNode, NodeCategory)
            .outerjoin(NodeCategory, KnowledgeNode.category_id == NodeCategory.id)
            .where(KnowledgeNode.user_id == uid)
            .order_by(KnowledgeNode.next_review_at)
        )
        rows = result.all()

        nodes = []
        for node, category in rows:
            nodes.append({
                "id": str(node.id),
                "node_key": node.node_key,
                "display_label": node.display_label,
                "mastery_score": node.mastery_score,
                "repetitions": node.repetitions,
                "interval_days": node.interval_days,
                "next_review_at": node.next_review_at.isoformat(),
                "category_name": category.name if category else None,
                "skill_area": category.skill_area if category else None,
                "color_hex": category.color_hex if category else "#4F46E5",
            })
        return nodes

    async def check_achievements(self, user_id: str) -> list[dict]:
        """Check and award any newly unlocked achievements."""
        uid = uuid.UUID(user_id)

        # Get already earned achievements
        earned_result = await self.db.execute(
            select(UserAchievement.achievement_id).where(UserAchievement.user_id == uid)
        )
        earned_ids = {row for row in earned_result.scalars().all()}

        # Get all achievements
        all_result = await self.db.execute(select(Achievement))
        all_achievements = all_result.scalars().all()

        # Get user stats for checking conditions
        stats = await self.get_stats(user_id)

        # Get session type counts
        session_counts = {}
        for stype in ["libre", "roleplay", "susurro", "writing"]:
            count_result = await self.db.execute(
                select(func.count()).select_from(Session).where(
                    and_(Session.user_id == uid, Session.session_type == stype)
                )
            )
            session_counts[stype] = count_result.scalar() or 0

        newly_earned = []
        for achievement in all_achievements:
            if achievement.id in earned_ids:
                continue

            condition = achievement.condition
            cond_type = condition.get("type", "")
            cond_value = condition.get("value", 0)
            unlocked = False

            if cond_type == "session_count" and stats["sessions_count"] >= cond_value:
                unlocked = True
            elif cond_type == "streak" and stats["current_streak"] >= cond_value:
                unlocked = True
            elif cond_type == "total_xp" and stats["total_xp"] >= cond_value:
                unlocked = True
            elif cond_type == "roleplay_count" and session_counts.get("roleplay", 0) >= cond_value:
                unlocked = True
            elif cond_type == "whisper_count" and session_counts.get("susurro", 0) >= cond_value:
                unlocked = True
            elif cond_type == "mastered_nodes" and stats["nodes_mastered"] >= cond_value:
                unlocked = True

            if unlocked:
                ua = UserAchievement(
                    user_id=uid,
                    achievement_id=achievement.id,
                )
                self.db.add(ua)
                newly_earned.append({
                    "slug": achievement.slug,
                    "name": achievement.name,
                    "description": achievement.description,
                    "xp_reward": achievement.xp_reward,
                    "icon_slug": achievement.icon_slug,
                })

        if newly_earned:
            await self.db.flush()

        return newly_earned

    async def get_achievements(self, user_id: str) -> dict:
        """Get all achievements with unlock status for a user."""
        uid = uuid.UUID(user_id)

        # All achievements
        all_result = await self.db.execute(
            select(Achievement).order_by(Achievement.slug)
        )
        all_achievements = all_result.scalars().all()

        # Earned
        earned_result = await self.db.execute(
            select(UserAchievement).where(UserAchievement.user_id == uid)
        )
        earned = {ua.achievement_id: ua.earned_at for ua in earned_result.scalars().all()}

        unlocked = []
        available = []
        for ach in all_achievements:
            item = {
                "id": str(ach.id),
                "slug": ach.slug,
                "name": ach.name,
                "description": ach.description,
                "xp_reward": ach.xp_reward,
                "icon_slug": ach.icon_slug,
                "earned_at": earned[ach.id].isoformat() if ach.id in earned else None,
                "is_unlocked": ach.id in earned,
            }
            if ach.id in earned:
                unlocked.append(item)
            else:
                available.append(item)

        return {
            "unlocked": unlocked,
            "available": available,
            "total_unlocked": len(unlocked),
            "total_available": len(available),
        }
