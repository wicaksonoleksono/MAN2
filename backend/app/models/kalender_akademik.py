from uuid import UUID, uuid4
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Date, Enum as SQLAlchemyEnum,
    UUID as SQLAlchemyUUID, ForeignKey
)
from app.config.database import Base
from app.enums import JenisKalender


class KalenderAkademik(Base):
    __tablename__ = "kalender_akademik"

    kalender_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    tahun_ajaran_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("tahun_ajaran.tahun_ajaran_id", ondelete="CASCADE"),
        nullable=False
    )
    tanggal: Mapped[date] = mapped_column(Date, nullable=False)
    jenis: Mapped[JenisKalender] = mapped_column(
        SQLAlchemyEnum(JenisKalender, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    keterangan: Mapped[str] = mapped_column(String(255), nullable=False)

    tahun_ajaran: Mapped["TahunAjaran"] = relationship()

    def __repr__(self) -> str:
        return f"KalenderAkademik(tanggal={self.tanggal}, jenis={self.jenis})"
