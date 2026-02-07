from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Enum as SQLAlchemyEnum,
    UUID as SQLAlchemyUUID, ForeignKey
)
from app.config.database import Base
from app.enums import StatusGuru, JenisKelamin, StructuralRole, BidangWakasek


class GuruProfile(Base):
    __tablename__ = "guru_profiles"

    guru_id: Mapped[UUID] = mapped_column(
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

    nip: Mapped[str] = mapped_column(
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

    nik: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    tahun_masuk: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status_guru: Mapped[StatusGuru] = mapped_column(
        SQLAlchemyEnum(StatusGuru, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StatusGuru.aktif
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

    structural_role: Mapped[StructuralRole] = mapped_column(
        SQLAlchemyEnum(StructuralRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StructuralRole.guru
    )

    # Only set when structural_role = Wakasek
    bidang_wakasek: Mapped[Optional[BidangWakasek]] = mapped_column(
        SQLAlchemyEnum(BidangWakasek, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        default=None
    )

    # Technical role / subject taught (e.g. "Matematika", "Fisika", "Agama")
    mata_pelajaran: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    pendidikan_terakhir: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="guru_profile")

    def __repr__(self) -> str:
        return f"GuruProfile(nip={self.nip}, nama={self.nama_lengkap})"
