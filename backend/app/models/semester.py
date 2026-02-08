from uuid import UUID, uuid4
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Date, Boolean, Enum as SQLAlchemyEnum,
    UUID as SQLAlchemyUUID, ForeignKey, UniqueConstraint
)
from app.config.database import Base
from app.enums import TipeSemester


class Semester(Base):
    __tablename__ = "semester"
    __table_args__ = (
        UniqueConstraint("tahun_ajaran_id", "tipe", name="uq_semester_tahun_tipe"),
    )

    semester_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    tahun_ajaran_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("tahun_ajaran.tahun_ajaran_id", ondelete="CASCADE"),
        nullable=False
    )
    tipe: Mapped[TipeSemester] = mapped_column(
        SQLAlchemyEnum(TipeSemester, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    tanggal_mulai: Mapped[date] = mapped_column(Date, nullable=False)
    tanggal_selesai: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tahun_ajaran: Mapped["TahunAjaran"] = relationship()

    def __repr__(self) -> str:
        return f"Semester(tipe={self.tipe}, active={self.is_active})"
