from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.absensi import Absensi
from app.models.izin_keluar import IzinKeluar
from app.models.user import User
from app.enums import UserType
from app.dto.absensi.absensi_response import (
    AbsensiResponseDTO,
    IzinKeluarResponseDTO,
)


class AbsensiService:
    """
    Service for attendance and izin keluar records.

    Raises:
        HTTPException: 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate_siswa(self, user_id: UUID) -> User:
        """Validate that the user_id belongs to a siswa."""
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user.user_type != UserType.siswa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a student"
            )
        return user

    # ── Absensi helpers ──────────────────────────────────────────────────────

    def _to_absensi_dto(self, record: Absensi) -> AbsensiResponseDTO:
        return AbsensiResponseDTO(
            absensi_id=record.absensi_id,
            user_id=record.user_id,
            tanggal=record.tanggal,
            time_in=record.time_in,
            time_out=record.time_out,
            status=record.status,
        )

    def _to_izin_dto(self, record: IzinKeluar) -> IzinKeluarResponseDTO:
        return IzinKeluarResponseDTO(
            izin_id=record.izin_id,
            user_id=record.user_id,
            created_at=record.created_at,
            keterangan=record.keterangan,
            waktu_kembali=record.waktu_kembali,
        )

    # ── Absensi CRUD ─────────────────────────────────────────────────────────

    async def list_absensi(self) -> list[AbsensiResponseDTO]:
        """
        List all attendance records.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(Absensi))
        records = result.scalars().all()
        return [self._to_absensi_dto(r) for r in records]

    async def list_absensi_by_student(self, user_id: UUID) -> list[AbsensiResponseDTO]:
        """
        List attendance records for a specific student.

        Raises:
            HTTPException: 404 if user not found
            HTTPException: 400 if user is not a student
        """
        await self._validate_siswa(user_id)
        result = await self.db.execute(
            select(Absensi).where(Absensi.user_id == user_id)
        )
        records = result.scalars().all()
        return [self._to_absensi_dto(r) for r in records]

    async def get_absensi(self, absensi_id: UUID) -> AbsensiResponseDTO:
        """
        Get a single attendance record by ID.

        Raises:
            HTTPException: 404 if record not found
        """
        result = await self.db.execute(
            select(Absensi).where(Absensi.absensi_id == absensi_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        return self._to_absensi_dto(record)

    # ── Izin Keluar CRUD ─────────────────────────────────────────────────────

    async def list_izin_keluar(self) -> list[IzinKeluarResponseDTO]:
        """
        List all izin keluar records.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(IzinKeluar))
        records = result.scalars().all()
        return [self._to_izin_dto(r) for r in records]

    async def list_izin_keluar_by_student(self, user_id: UUID) -> list[IzinKeluarResponseDTO]:
        """
        List izin keluar records for a specific student.

        Raises:
            HTTPException: 404 if user not found
            HTTPException: 400 if user is not a student
        """
        await self._validate_siswa(user_id)
        result = await self.db.execute(
            select(IzinKeluar).where(IzinKeluar.user_id == user_id)
        )
        records = result.scalars().all()
        return [self._to_izin_dto(r) for r in records]

    async def get_izin_keluar(self, izin_id: UUID) -> IzinKeluarResponseDTO:
        """
        Get a single izin keluar record by ID.

        Raises:
            HTTPException: 404 if record not found
        """
        result = await self.db.execute(
            select(IzinKeluar).where(IzinKeluar.izin_id == izin_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Izin keluar record not found"
            )
        return self._to_izin_dto(record)
