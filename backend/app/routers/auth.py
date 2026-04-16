"""
Fluentify — Auth Router
Endpoints: register, login, refresh, logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """RF-01: Register a new user."""
    service = AuthService(db)
    try:
        user = await service.register(request.email, request.password, request.display_name)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """RF-02: Authenticate user and return JWT tokens."""
    service = AuthService(db)
    try:
        result = await service.login(request.email, request.password)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """RF-05: Refresh access token."""
    service = AuthService(db)
    try:
        result = await service.refresh_token(request.refresh_token)
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """RF-03: Logout (client-side token removal)."""
    return None
