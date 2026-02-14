from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import bearer_scheme
from app.services.auth_service import AuthService
from app.dto.auth.auth_request import LoginRequestDTO
from app.dto.auth.auth_response import (
    UserResponseDTO,
    TokenResponseDTO,
    MessageResponseDTO
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponseDTO,
    summary="User Login",
    description="Login with username and password to get JWT access token"
)
async def login(
    request: LoginRequestDTO,
    db: AsyncSession = Depends(get_db)
) -> TokenResponseDTO:
    """
    Login with username and password

    - **username**: Your username
    - **password**: Your password

    Returns JWT access token and user information on success.
    """
    service = AuthService(db)
    return await service.login(request)


@router.get(
    "/verify",
    response_model=UserResponseDTO,
    summary="Verify Token",
    description="Verify JWT token and get user information"
)
async def verify(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponseDTO:
    service = AuthService(db)
    return await service.verify_token(credentials.credentials)


@router.post(
    "/logout",
    response_model=MessageResponseDTO,
    summary="User Logout",
    description="Logout user (invalidate token on client side)"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> MessageResponseDTO:
    service = AuthService(db)
    return await service.logout(credentials.credentials)
