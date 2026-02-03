from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.services.auth_service import AuthService
from app.dto.auth.auth_request import SignupRequestDTO, LoginRequestDTO
from app.dto.auth.auth_response import (
    UserResponseDTO,
    TokenResponseDTO,
    SignupResponseDTO,
    MessageResponseDTO
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=SignupResponseDTO,
    status_code=201,
    summary="User Signup",
    description="Create a new user account with username and password"
)
async def signup(
    request: SignupRequestDTO,
    db: AsyncSession = Depends(get_db)
) -> SignupResponseDTO:
    """
    Create a new user account

    - **username**: 3-100 chars, alphanumeric and underscore only (lowercase)
    - **password**: Min 8 chars, must contain uppercase, lowercase, and digit

    Returns user information on success.
    """
    service = AuthService(db)
    return await service.signup(request)


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
    authorization: str = Header(..., description="Bearer token"),
    db: AsyncSession = Depends(get_db)
) -> UserResponseDTO:
    """
    Verify JWT token and get user information

    - **Authorization header**: "Bearer {your_jwt_token}"

    Returns user information if token is valid.
    """
    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "").strip()
    service = AuthService(db)
    return await service.verify_token(token)


@router.post(
    "/logout",
    response_model=MessageResponseDTO,
    summary="User Logout",
    description="Logout user (invalidate token on client side)"
)
async def logout(
    authorization: str = Header(..., description="Bearer token"),
    db: AsyncSession = Depends(get_db)
) -> MessageResponseDTO:
    """
    Logout user

    - **Authorization header**: "Bearer {your_jwt_token}"

    Note: This is a basic implementation. Client should delete the token.
    For production, consider implementing Redis-based token blacklist.
    """
    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "").strip()
    service = AuthService(db)
    return await service.logout(token)
