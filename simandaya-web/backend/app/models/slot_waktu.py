from uuid import UUID, uuid4
from datetime import time
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Time, UUID as SQLAlchemyUUID
from app.config.database import Base


class SlotWaktu(Base):
    __tablename__ = "slot_waktu"

    slot_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    nama: Mapped[str] = mapped_column(String(50), nullable=False)
    jam_mulai: Mapped[time] = mapped_column(Time, nullable=False)
    jam_selesai: Mapped[time] = mapped_column(Time, nullable=False)
    urutan: Mapped[int] = mapped_column(Integer, nullable=False)
    is_piket: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"SlotWaktu(nama={self.nama}, {self.jam_mulai}-{self.jam_selesai})"
