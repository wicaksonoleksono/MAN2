from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID as SQLAlchemyUUID, ForeignKey, UniqueConstraint
from app.config.database import Base


class SiswaKelas(Base):
    __tablename__ = "siswa_kelas"
    __table_args__ = (
        UniqueConstraint("kelas_id", "user_id", name="uq_siswa_kelas"),
    )

    siswa_kelas_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    kelas_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("kelas.kelas_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    kelas: Mapped["Kelas"] = relationship()
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"SiswaKelas(kelas_id={self.kelas_id}, user_id={self.user_id})"
