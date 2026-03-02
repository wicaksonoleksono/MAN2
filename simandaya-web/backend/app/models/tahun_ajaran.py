from uuid import UUID, uuid4
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Boolean, UUID as SQLAlchemyUUID
from app.config.database import Base


class TahunAjaran(Base):
    __tablename__ = "tahun_ajaran"

    tahun_ajaran_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    nama: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    tanggal_mulai: Mapped[date] = mapped_column(Date, nullable=False)
    tanggal_selesai: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"TahunAjaran(nama={self.nama}, active={self.is_active})"
