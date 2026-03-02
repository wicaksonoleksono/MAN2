from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
    UUID as SQLAlchemyUUID, ForeignKey, UniqueConstraint
)
from app.config.database import Base
from app.enums import HariSekolah


class Jadwal(Base):
    __tablename__ = "jadwal"
    __table_args__ = (
        UniqueConstraint(
            "semester_id", "hari", "slot_waktu_id", "kelas_id",
            name="uq_jadwal_kelas_slot"
        ),
        UniqueConstraint(
            "semester_id", "hari", "slot_waktu_id", "guru_user_id",
            name="uq_jadwal_guru_slot"
        ),
    )

    jadwal_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    semester_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("semester.semester_id", ondelete="CASCADE"),
        nullable=False
    )
    kelas_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("kelas.kelas_id", ondelete="CASCADE"),
        nullable=False
    )
    mapel_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("mata_pelajaran.mapel_id", ondelete="CASCADE"),
        nullable=False
    )
    guru_user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    hari: Mapped[HariSekolah] = mapped_column(
        SQLAlchemyEnum(HariSekolah, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    slot_waktu_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("slot_waktu.slot_id", ondelete="CASCADE"),
        nullable=False
    )

    semester: Mapped["Semester"] = relationship()
    kelas: Mapped["Kelas"] = relationship()
    mapel: Mapped["MataPelajaran"] = relationship()
    guru: Mapped["User"] = relationship()
    slot_waktu: Mapped["SlotWaktu"] = relationship()

    def __repr__(self) -> str:
        return f"Jadwal(hari={self.hari}, kelas_id={self.kelas_id})"
