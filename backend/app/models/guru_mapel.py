from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID as SQLAlchemyUUID, ForeignKey, UniqueConstraint
from app.config.database import Base


class GuruMapel(Base):
    __tablename__ = "guru_mapel"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "mapel_id", "kelas_id", "tahun_ajaran_id",
            name="uq_guru_mapel_assignment"
        ),
    )

    guru_mapel_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
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
    tahun_ajaran_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("tahun_ajaran.tahun_ajaran_id", ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped["User"] = relationship()
    mapel: Mapped["MataPelajaran"] = relationship()
    kelas: Mapped["Kelas"] = relationship()
    tahun_ajaran: Mapped["TahunAjaran"] = relationship()

    def __repr__(self) -> str:
        return f"GuruMapel(user_id={self.user_id}, mapel_id={self.mapel_id})"
