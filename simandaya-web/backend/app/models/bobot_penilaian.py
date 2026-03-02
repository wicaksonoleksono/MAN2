from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer, Enum as SQLAlchemyEnum, UUID as SQLAlchemyUUID,
    ForeignKey, UniqueConstraint, CheckConstraint,
)
from app.config.database import Base
from app.enums import JenisTugas


class BobotPenilaian(Base):
    __tablename__ = "bobot_penilaian"
    __table_args__ = (
        UniqueConstraint(
            "mapel_id", "kelas_id", "semester_id", "jenis",
            name="uq_bobot_context_jenis"
        ),
        CheckConstraint(
            "bobot >= 0 AND bobot <= 100",
            name="ck_bobot_range"
        ),
    )

    bobot_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    mapel_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("mata_pelajaran.mapel_id", ondelete="CASCADE"),
        nullable=False
    )

    kelas_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("kelas.kelas_id", ondelete="CASCADE"),
        nullable=False
    )

    semester_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("semester.semester_id", ondelete="CASCADE"),
        nullable=False
    )

    jenis: Mapped[JenisTugas] = mapped_column(
        SQLAlchemyEnum(JenisTugas, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    bobot: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    mapel: Mapped["MataPelajaran"] = relationship()
    kelas: Mapped["Kelas"] = relationship()
    semester: Mapped["Semester"] = relationship()

    def __repr__(self) -> str:
        return f"BobotPenilaian(jenis={self.jenis}, bobot={self.bobot})"
