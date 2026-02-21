from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.absensi import Absensi
from app.models.izin_keluar import IzinKeluar
from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.kelas import Kelas
from app.models.siswa_kelas import SiswaKelas
from app.models.guru_mapel import GuruMapel
from app.enums import UserType
from app.dto.absensi.absensi_response import (
    AbsensiResponseDTO,
    IzinKeluarResponseDTO,
)
from app.dto.absensi.public_response import (
    PublicAbsensiDTO,
    PublicIzinKeluarDTO,
)
from app.dto.absensi.bulk_absensi_dto import (
    BulkAbsensiCreateDTO,
    BulkAbsensiResponseDTO,
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
            marked_by=record.marked_by,
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

    # ── Public (no auth) ────────────────────────────────────────────────────────

    def _to_public_absensi_dto(self, record: Absensi) -> PublicAbsensiDTO:
        profile = record.user.siswa_profile if record.user else None
        return PublicAbsensiDTO(
            absensi_id=record.absensi_id,
            nama_siswa=profile.nama_lengkap if profile else "Unknown",
            kelas=profile.kelas_jurusan if profile else None,
            tanggal=record.tanggal,
            time_in=record.time_in,
            time_out=record.time_out,
            status=record.status,
        )

    def _to_public_izin_dto(self, record: IzinKeluar) -> PublicIzinKeluarDTO:
        profile = record.user.siswa_profile if record.user else None
        return PublicIzinKeluarDTO(
            izin_id=record.izin_id,
            nama_siswa=profile.nama_lengkap if profile else "Unknown",
            kelas=profile.kelas_jurusan if profile else None,
            created_at=record.created_at,
            keterangan=record.keterangan,
            waktu_kembali=record.waktu_kembali,
        )

    async def list_absensi_public(
        self,
        tanggal: date,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PublicAbsensiDTO]:
        """
        Public list of attendance records filtered by date, with student names.

        Raises:
            HTTPException: 500 if database error
        """
        stmt = (
            select(Absensi)
            .join(User, Absensi.user_id == User.user_id)
            .outerjoin(SiswaProfile, User.user_id == SiswaProfile.user_id)
            .options(
                selectinload(Absensi.user).selectinload(User.siswa_profile)
            )
            .where(Absensi.tanggal == tanggal)
        )
        if search:
            stmt = stmt.where(SiswaProfile.nama_lengkap.ilike(f"%{search}%"))
        stmt = stmt.order_by(SiswaProfile.nama_lengkap).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [self._to_public_absensi_dto(r) for r in records]

    async def list_izin_keluar_public(
        self,
        tanggal: date,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PublicIzinKeluarDTO]:
        """
        Public list of izin keluar records filtered by date, with student names.

        Raises:
            HTTPException: 500 if database error
        """
        stmt = (
            select(IzinKeluar)
            .join(User, IzinKeluar.user_id == User.user_id)
            .outerjoin(SiswaProfile, User.user_id == SiswaProfile.user_id)
            .options(
                selectinload(IzinKeluar.user).selectinload(User.siswa_profile)
            )
            .where(func.date(IzinKeluar.created_at) == tanggal)
        )
        if search:
            stmt = stmt.where(SiswaProfile.nama_lengkap.ilike(f"%{search}%"))
        stmt = stmt.order_by(IzinKeluar.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [self._to_public_izin_dto(r) for r in records]

    # ── Bulk Attendance ─────────────────────────────────────────────────────────

    async def bulk_create_absensi(
        self, request: BulkAbsensiCreateDTO, current_user: User
    ) -> BulkAbsensiResponseDTO:
        """
        Bulk create/update attendance for a class.

        Permission: admin, wali kelas of the class, or any guru who teaches the class.

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 403 if no permission
            HTTPException: 400 if student not in class
            HTTPException: 500 on database error
        """
        try:
            # Validate kelas exists
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == request.kelas_id)
            )
            kelas = result.scalar_one_or_none()
            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {request.kelas_id} not found"
                )

            # Permission check
            if current_user.user_type != UserType.admin:
                is_wali = kelas.wali_kelas_id == current_user.user_id

                teaches_result = await self.db.execute(
                    select(GuruMapel).where(
                        and_(
                            GuruMapel.user_id == current_user.user_id,
                            GuruMapel.kelas_id == request.kelas_id,
                        )
                    )
                )
                is_teacher = teaches_result.first() is not None

                if not is_wali and not is_teacher:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to mark attendance for this class"
                    )

            # Get students in this kelas for validation
            result = await self.db.execute(
                select(SiswaKelas.user_id).where(
                    SiswaKelas.kelas_id == request.kelas_id
                )
            )
            valid_student_ids = {row[0] for row in result.all()}

            created = 0
            updated = 0

            for entry in request.entries:
                if entry.user_id not in valid_student_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Student {entry.user_id} is not in this class"
                    )

                # Check existing record (upsert)
                result = await self.db.execute(
                    select(Absensi).where(
                        and_(
                            Absensi.user_id == entry.user_id,
                            Absensi.tanggal == request.tanggal,
                        )
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.status = entry.status
                    existing.marked_by = current_user.user_id
                    updated += 1
                else:
                    record = Absensi(
                        user_id=entry.user_id,
                        tanggal=request.tanggal,
                        status=entry.status,
                        marked_by=current_user.user_id,
                    )
                    self.db.add(record)
                    created += 1

            await self.db.commit()

            return BulkAbsensiResponseDTO(
                created_count=created,
                updated_count=updated,
                message=f"Bulk attendance: {created} created, {updated} updated"
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create bulk attendance: {str(e)}"
            )
