from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Numeric, String, UUID as SQLAlchemyUUID,
    ForeignKey, UniqueConstraint,
)
from app.config.database import Base


class Nilai(Base):
    __tablename__ = "nilai"
    __table_args__ = (
        UniqueConstraint("tugas_id", "user_id", name="uq_nilai_tugas_user"),
    )

    nilai_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    tugas_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("tugas.tugas_id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    nilai: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    catatan: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    # Relationships
    tugas: Mapped["Tugas"] = relationship()
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"Nilai(tugas_id={self.tugas_id}, user_id={self.user_id}, nilai={self.nilai})"
