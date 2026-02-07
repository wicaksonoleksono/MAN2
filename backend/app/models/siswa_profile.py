from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Enum as SQLAlchemyEnum,
    UUID as SQLAlchemyUUID, ForeignKey
)
from app.config.database import Base
from app.enums import StatusSiswa, JenisKelamin


class SiswaProfile(Base):
    __tablename__ = "siswa_profiles"

    siswa_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    nis: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    nama_lengkap: Mapped[str] = mapped_column(
        String(225),
        nullable=False
    )

    dob: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    tempat_lahir: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    jenis_kelamin: Mapped[JenisKelamin] = mapped_column(
        SQLAlchemyEnum(JenisKelamin, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    alamat: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    nama_wali: Mapped[str] = mapped_column(
        String(225),
        nullable=False
    )

    nik: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    kelas_jurusan: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    tahun_masuk: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status_siswa: Mapped[StatusSiswa] = mapped_column(
        SQLAlchemyEnum(StatusSiswa, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StatusSiswa.aktif
    )

    kontak: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    kewarganegaraan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Indonesia"
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="siswa_profile")

    def __repr__(self) -> str:
        return f"SiswaProfile(nis={self.nis}, nama={self.nama_lengkap})"
