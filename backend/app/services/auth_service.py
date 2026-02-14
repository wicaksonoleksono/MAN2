from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.utils.jwt_utils import JWTManager
from app.dto.auth.auth_request import SignupRequestDTO, LoginRequestDTO
from app.dto.auth.auth_response import (
    UserResponseDTO,
    TokenResponseDTO,
    SignupResponseDTO,
    MessageResponseDTO
)
from app.enums import RegistrationStatus


class AuthService:
    """
    Authentication service for username/password auth

    Password hashing/verification is handled by the User model.

    Raises:
        HTTPException: 400, 401, 403, 404, 500
    """

    def __init__(
        self,
        db: AsyncSession,
        jwt_manager: JWTManager | None = None,
    ):
        self.db = db
        self.jwt_manager = jwt_manager or JWTManager()

    async def signup(self, request: SignupRequestDTO) -> SignupResponseDTO:
        """
        User signup - creates new user with username and password

        Args:
            request: Signup request with username and password

        Returns:
            SignupResponseDTO: Created user information

        Raises:
            HTTPException: 400 if username already exists
            HTTPException: 500 if database error occurs
        """
        try:
            # Check if username already exists
            result = await self.db.execute(
                select(User).where(User.username == request.username)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{request.username}' is already taken"
                )

            user = User(
                username=request.username,
                user_type=request.user_type,
            )
            user.set_password(request.password)

            # Save to database
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            # Convert to DTO
            user_dto = UserResponseDTO(
                user_id=user.user_id,
                username=user.username,
                user_type=user.user_type.value,
                registration_status=user.registration_status.value,
                created_at=user.created_at,
                last_login=user.last_login,
                is_active=user.is_active
            )

            return SignupResponseDTO(
                message="User created successfully",
                user=user_dto
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    async def login(self, request: LoginRequestDTO) -> TokenResponseDTO:
        """
        User login with username and password

        Args:
            request: Login request with username and password

        Returns:
            TokenResponseDTO: JWT token and user info

        Raises:
            HTTPException: 401 if credentials are invalid
            HTTPException: 403 if user account is deactivated
        """
        # Find user by username
        result = await self.db.execute(
            select(User).where(User.username == request.username)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if not user.verify_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        if user.registration_status == RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Registrasi belum selesai. Silakan lengkapi pendaftaran."
            )

        # Update last login
        user.update_last_login()
        await self.db.commit()

        # Generate JWT token
        jwt_token = self.jwt_manager.create_access_token(
            user_id=user.user_id,
            username=user.username
        )

        # Create response
        user_dto = UserResponseDTO(
            user_id=user.user_id,
            username=user.username,
            user_type=user.user_type.value,
            registration_status=user.registration_status.value,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active
        )

        return TokenResponseDTO(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=self.jwt_manager.get_token_expiration(),
            user=user_dto
        )

    async def verify_token(self, token: str) -> UserResponseDTO:
        """
        Verify JWT token and return user info

        Args:
            token: JWT access token

        Returns:
            UserResponseDTO: User information

        Raises:
            HTTPException: 401 if token is invalid or expired
            HTTPException: 404 if user not found
            HTTPException: 403 if user account is deactivated
        """
        payload = self.jwt_manager.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        user_id = UUID(payload["sub"])

        # Query user from database
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        return UserResponseDTO(
            user_id=user.user_id,
            username=user.username,
            user_type=user.user_type.value,
            registration_status=user.registration_status.value,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active
        )

    async def logout(self, token: str) -> MessageResponseDTO:
        """
        Logout user (basic implementation)

        Args:
            token: JWT access token

        Returns:
            MessageResponseDTO: Success message

        Raises:
            HTTPException: 401 if token is invalid

        Note:
            This is a basic implementation. For production, consider:
            - Redis-based token blacklist
            - Token versioning in database
        """
        # Verify token is valid
        payload = self.jwt_manager.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # In basic implementation, client is responsible for deleting token
        # Future: Add Redis blacklist here
        return MessageResponseDTO(
            message="Logged out successfully"
        )
