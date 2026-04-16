"""
Fluentify — Authentication Service
Business logic for registration, login, and token management.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User, UserProfile
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str, display_name: str) -> User:
        """Register a new user with email, password and display name."""
        # Check if email already exists
        result = await self.db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("El correo electrónico ya está registrado")

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hash_password(password),
            display_name=display_name,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()

        # Create default profile
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            target_language="en",
            native_language="es",
            cefr_level="A1",
        )
        self.db.add(profile)
        await self.db.flush()

        return user

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user and return tokens."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Credenciales inválidas")

        if not user.is_active:
            raise ValueError("La cuenta está desactivada")

        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": user,
        }

    async def refresh_token(self, refresh_token_str: str) -> dict:
        """Generate new access token from valid refresh token."""
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Token de refresco inválido")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("Usuario no encontrado o inactivo")

        token_data = {"sub": str(user.id), "email": user.email}
        new_access = create_access_token(token_data)

        return {
            "access_token": new_access,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by UUID."""
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        return result.scalar_one_or_none()
