from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, UUID as SQLAlchemyUUID, func
from app.config.database import Base


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)


class User(Base):
    """
    User database model with username/password authentication

    Authentication via username and password (hashed with bcrypt)
    """

    __tablename__ = "users"

    # Primary key
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    # Username - unique, 3-100 chars, alphanumeric + underscore
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # Password hash - bcrypt hashed password (NEVER store plain password)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = utc_now()

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username={self.username})"
