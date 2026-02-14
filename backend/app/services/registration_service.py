from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.guru_profile import GuruProfile
from app.enums import (
    UserType, RegistrationStatus, StatusSiswa, StatusGuru,
)
from app.dto.registration.registration_dto import (
    PendingStudentDTO, PendingTeacherDTO,
    PendingStudentSearchResponse, PendingTeacherSearchResponse,
    ClaimStudentRequestDTO, ClaimTeacherRequestDTO, ClaimResponseDTO,
    PreRegisterStudentDTO, PreRegisterTeacherDTO, PreRegisterResponseDTO,
)


class RegistrationService:
    """
    Handles pre-registration search and self-signup claim flow.

    Raises:
        HTTPException: 400, 404
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Search ──────────────────────────────────────────────────────────────

    async def search_pending_students(self, name: str) -> PendingStudentSearchResponse:
        """
        Search PENDING students by nama_lengkap (ILIKE, min 2 chars).

        Raises:
            HTTPException: 400 if search term too short
        """
        if len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimal 2 karakter untuk pencarian"
            )

        pattern = f"%{name.strip()}%"
        query = (
            select(SiswaProfile)
            .join(User, SiswaProfile.user_id == User.user_id)
            .where(
                and_(
                    User.registration_status == RegistrationStatus.pending,
                    SiswaProfile.nama_lengkap.ilike(pattern),
                )
            )
        )
        result = await self.db.execute(query)
        profiles = result.scalars().all()

        items = [
            PendingStudentDTO(
                siswa_id=p.siswa_id,
                nama_lengkap=p.nama_lengkap,
                kelas_jurusan=p.kelas_jurusan,
                jenis_kelamin=p.jenis_kelamin,
            )
            for p in profiles
        ]
        return PendingStudentSearchResponse(items=items, total=len(items))

    async def search_pending_teachers(self, name: str) -> PendingTeacherSearchResponse:
        """
        Search PENDING teachers by nama_lengkap (ILIKE, min 2 chars).

        Raises:
            HTTPException: 400 if search term too short
        """
        if len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimal 2 karakter untuk pencarian"
            )

        pattern = f"%{name.strip()}%"
        query = (
            select(GuruProfile)
            .join(User, GuruProfile.user_id == User.user_id)
            .where(
                and_(
                    User.registration_status == RegistrationStatus.pending,
                    GuruProfile.nama_lengkap.ilike(pattern),
                )
            )
        )
        result = await self.db.execute(query)
        profiles = result.scalars().all()

        items = [
            PendingTeacherDTO(
                guru_id=p.guru_id,
                nama_lengkap=p.nama_lengkap,
                jenis_kelamin=p.jenis_kelamin,
            )
            for p in profiles
        ]
        return PendingTeacherSearchResponse(items=items, total=len(items))

    # ── Claim ───────────────────────────────────────────────────────────────

    async def claim_student(self, request: ClaimStudentRequestDTO) -> ClaimResponseDTO:
        """
        Student claims a PENDING entry and completes registration.

        Raises:
            HTTPException: 404 if siswa not found
            HTTPException: 400 if not PENDING, username taken, or NIS taken
        """
        # Load profile + user
        result = await self.db.execute(
            select(SiswaProfile)
            .options(joinedload(SiswaProfile.user))
            .where(SiswaProfile.siswa_id == request.siswa_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data siswa tidak ditemukan"
            )

        user = profile.user
        if user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun ini sudah terdaftar"
            )

        # Check username uniqueness
        username_check = await self.db.execute(
            select(User).where(User.username == request.username)
        )
        if username_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' sudah digunakan"
            )

        # Check NIS uniqueness
        nis_check = await self.db.execute(
            select(SiswaProfile).where(
                and_(
                    SiswaProfile.nis == request.nis,
                    SiswaProfile.siswa_id != request.siswa_id,
                )
            )
        )
        if nis_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"NIS '{request.nis}' sudah digunakan"
            )

        # Update user
        user.username = request.username
        user.set_password(request.password)
        user.registration_status = RegistrationStatus.completed
        user.is_active = True

        # Fill profile
        profile.nis = request.nis
        profile.dob = request.dob
        profile.tempat_lahir = request.tempat_lahir
        profile.alamat = request.alamat
        profile.nama_wali = request.nama_wali
        profile.nik = request.nik
        profile.tahun_masuk = request.tahun_masuk

        await self.db.commit()

        return ClaimResponseDTO(
            message="Registrasi berhasil! Silakan login.",
            username=user.username,
            user_type=user.user_type.value,
        )

    async def claim_teacher(self, request: ClaimTeacherRequestDTO) -> ClaimResponseDTO:
        """
        Teacher claims a PENDING entry and completes registration.

        Raises:
            HTTPException: 404 if guru not found
            HTTPException: 400 if not PENDING, username taken, or NIP taken
        """
        result = await self.db.execute(
            select(GuruProfile)
            .options(joinedload(GuruProfile.user))
            .where(GuruProfile.guru_id == request.guru_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data guru tidak ditemukan"
            )

        user = profile.user
        if user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun ini sudah terdaftar"
            )

        # Check username uniqueness
        username_check = await self.db.execute(
            select(User).where(User.username == request.username)
        )
        if username_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' sudah digunakan"
            )

        # Check NIP uniqueness
        nip_check = await self.db.execute(
            select(GuruProfile).where(
                and_(
                    GuruProfile.nip == request.nip,
                    GuruProfile.guru_id != request.guru_id,
                )
            )
        )
        if nip_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"NIP '{request.nip}' sudah digunakan"
            )

        # Update user
        user.username = request.username
        user.set_password(request.password)
        user.registration_status = RegistrationStatus.completed
        user.is_active = True

        # Fill profile
        profile.nip = request.nip
        profile.dob = request.dob
        profile.tempat_lahir = request.tempat_lahir
        profile.alamat = request.alamat
        profile.nik = request.nik
        profile.tahun_masuk = request.tahun_masuk
        if request.kontak is not None:
            profile.kontak = request.kontak
        if request.mata_pelajaran is not None:
            profile.mata_pelajaran = request.mata_pelajaran
        if request.pendidikan_terakhir is not None:
            profile.pendidikan_terakhir = request.pendidikan_terakhir

        await self.db.commit()

        return ClaimResponseDTO(
            message="Registrasi berhasil! Silakan login.",
            username=user.username,
            user_type=user.user_type.value,
        )

    # ── Admin Pre-Register ──────────────────────────────────────────────────

    async def pre_register_student(self, request: PreRegisterStudentDTO) -> PreRegisterResponseDTO:
        """
        Admin creates a PENDING student entry (name + gender + kelas only).

        Raises:
            HTTPException: 500 if database error
        """
        user = User(
            user_type=UserType.siswa,
            registration_status=RegistrationStatus.pending,
            username=None,
            password_hash=None,
            is_active=False,
        )
        self.db.add(user)
        await self.db.flush()

        profile = SiswaProfile(
            user_id=user.user_id,
            nama_lengkap=request.nama_lengkap,
            jenis_kelamin=request.jenis_kelamin,
            kelas_jurusan=request.kelas_jurusan,
            kontak=request.kontak or "",
            status_siswa=StatusSiswa.aktif,
            kewarganegaraan="Indonesia",
        )
        self.db.add(profile)
        await self.db.commit()

        return PreRegisterResponseDTO(
            message=f"Siswa '{request.nama_lengkap}' berhasil didaftarkan (PENDING)"
        )

    async def pre_register_teacher(self, request: PreRegisterTeacherDTO) -> PreRegisterResponseDTO:
        """
        Admin creates a PENDING teacher entry (name + gender only).

        Raises:
            HTTPException: 500 if database error
        """
        user = User(
            user_type=UserType.guru,
            registration_status=RegistrationStatus.pending,
            username=None,
            password_hash=None,
            is_active=False,
        )
        self.db.add(user)
        await self.db.flush()

        profile = GuruProfile(
            user_id=user.user_id,
            nama_lengkap=request.nama_lengkap,
            jenis_kelamin=request.jenis_kelamin,
            kontak=request.kontak or "",
            status_guru=StatusGuru.aktif,
            kewarganegaraan="Indonesia",
        )
        self.db.add(profile)
        await self.db.commit()

        return PreRegisterResponseDTO(
            message=f"Guru '{request.nama_lengkap}' berhasil didaftarkan (PENDING)"
        )
