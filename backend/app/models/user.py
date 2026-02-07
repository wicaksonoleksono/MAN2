from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum as SQLAlchemyEnum, UUID as SQLAlchemyUUID, func
from passlib.context import CryptContext
from app.config.database import Base
from app.config.settings import settings
from app.enums import UserType


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """
    Auth-only user model. Profile data lives in siswa_profile / guru_profile.
    """

    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    user_type: Mapped[UserType] = mapped_column(
        SQLAlchemyEnum(UserType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

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

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    # Relationships
    siswa_profile: Mapped[Optional["SiswaProfile"]] = relationship(back_populates="user")
    guru_profile: Mapped[Optional["GuruProfile"]] = relationship(back_populates="user")

    def set_password(self, plain_password: str) -> None:
        self.password_hash = pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    def update_last_login(self) -> None:
        self.last_login = utc_now()

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username={self.username})"
