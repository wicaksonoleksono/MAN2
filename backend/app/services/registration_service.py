from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.guru_profile import GuruProfile
from app.enums import (
    UserType, RegistrationStatus, StatusSiswa, StatusGuru,
)
from app.dto.registration.registration_dto import (
    StudentLookupResponseDTO, TeacherLookupResponseDTO,
    ClaimStudentRequestDTO, ClaimTeacherRequestDTO, ClaimResponseDTO,
    PreRegisterStudentDTO, PreRegisterTeacherDTO, PreRegisterResponseDTO,
)


class RegistrationService:
    """
    Handles pre-registration and NIS/NIP-based claim flow.

    Raises:
        HTTPException: 400, 404
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Lookup (Step 2: verify NIS/NIP) ──────────────────────────────────────

    async def lookup_student_by_nis(self, nis: str) -> StudentLookupResponseDTO:
        """
        Lookup a PENDING student by NIS.

        Raises:
            HTTPException: 404 if NIS not found or not PENDING
        """
        result = await self.db.execute(
            select(SiswaProfile)
            .options(joinedload(SiswaProfile.user))
            .where(SiswaProfile.nis == nis)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NIS tidak ditemukan"
            )

        if profile.user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun dengan NIS ini sudah terdaftar"
            )

        return StudentLookupResponseDTO(
            siswa_id=profile.siswa_id,
            nis=profile.nis,
            nama_lengkap=profile.nama_lengkap,
            kelas_jurusan=profile.kelas_jurusan,
            jenis_kelamin=profile.jenis_kelamin,
        )

    async def lookup_teacher_by_nip(self, nip: str) -> TeacherLookupResponseDTO:
        """
        Lookup a PENDING teacher by NIP.

        Raises:
            HTTPException: 404 if NIP not found or not PENDING
        """
        result = await self.db.execute(
            select(GuruProfile)
            .options(joinedload(GuruProfile.user))
            .where(GuruProfile.nip == nip)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NIP tidak ditemukan"
            )

        if profile.user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun dengan NIP ini sudah terdaftar"
            )

        return TeacherLookupResponseDTO(
            guru_id=profile.guru_id,
            nip=profile.nip,
            nama_lengkap=profile.nama_lengkap,
            jenis_kelamin=profile.jenis_kelamin,
        )

    # ── Claim (Step 3: set credentials) ──────────────────────────────────────

    async def claim_student(self, request: ClaimStudentRequestDTO) -> ClaimResponseDTO:
        """
        Student claims a PENDING entry by NIS and sets username + password.

        Raises:
            HTTPException: 404 if NIS not found
            HTTPException: 400 if not PENDING or username taken
        """
        result = await self.db.execute(
            select(SiswaProfile)
            .options(joinedload(SiswaProfile.user))
            .where(SiswaProfile.nis == request.nis)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NIS tidak ditemukan"
            )

        user = profile.user
        if user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun dengan NIS ini sudah terdaftar"
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

        # Activate account
        user.username = request.username
        user.set_password(request.password)
        user.registration_status = RegistrationStatus.completed
        user.is_active = True

        await self.db.commit()

        return ClaimResponseDTO(
            message="Registrasi berhasil! Silakan login.",
            username=user.username,
            user_type=user.user_type.value,
        )

    async def claim_teacher(self, request: ClaimTeacherRequestDTO) -> ClaimResponseDTO:
        """
        Teacher claims a PENDING entry by NIP and sets username + password.

        Raises:
            HTTPException: 404 if NIP not found
            HTTPException: 400 if not PENDING or username taken
        """
        result = await self.db.execute(
            select(GuruProfile)
            .options(joinedload(GuruProfile.user))
            .where(GuruProfile.nip == request.nip)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NIP tidak ditemukan"
            )

        user = profile.user
        if user.registration_status != RegistrationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Akun dengan NIP ini sudah terdaftar"
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

        # Activate account
        user.username = request.username
        user.set_password(request.password)
        user.registration_status = RegistrationStatus.completed
        user.is_active = True

        await self.db.commit()

        return ClaimResponseDTO(
            message="Registrasi berhasil! Silakan login.",
            username=user.username,
            user_type=user.user_type.value,
        )

    # ── Admin Pre-Register ──────────────────────────────────────────────────

    async def pre_register_student(self, request: PreRegisterStudentDTO) -> PreRegisterResponseDTO:
        """
        Admin creates a PENDING student entry (nis + nama required, rest optional).

        Raises:
            HTTPException: 400 if NIS already exists
        """
        nis_check = await self.db.execute(
            select(SiswaProfile).where(SiswaProfile.nis == request.nis)
        )
        if nis_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"NIS '{request.nis}' sudah digunakan"
            )

        user = User(
            user_type=UserType.siswa,
            registration_status=RegistrationStatus.pending,
            username=None,
            password_hash=None,
            is_active=False,
        )
        self.db.add(user)
        await self.db.flush()

        profile_data = request.model_dump(exclude_unset=True)
        profile = SiswaProfile(
            user_id=user.user_id,
            nama_lengkap=request.nama_lengkap,
            nis=request.nis,
            status_siswa=StatusSiswa.aktif,
            kewarganegaraan=profile_data.get("kewarganegaraan", "Indonesia"),
        )
        optional_fields = [
            "dob", "tempat_lahir", "jenis_kelamin", "alamat",
            "nama_wali", "nik", "kelas_jurusan", "tahun_masuk", "kontak",
        ]
        for field in optional_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])

        self.db.add(profile)
        await self.db.commit()

        return PreRegisterResponseDTO(
            message=f"Siswa '{request.nama_lengkap}' berhasil didaftarkan (PENDING)"
        )

    async def pre_register_teacher(self, request: PreRegisterTeacherDTO) -> PreRegisterResponseDTO:
        """
        Admin creates a PENDING teacher entry (nip + nama required, rest optional).

        Raises:
            HTTPException: 400 if NIP already exists
        """
        nip_check = await self.db.execute(
            select(GuruProfile).where(GuruProfile.nip == request.nip)
        )
        if nip_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"NIP '{request.nip}' sudah digunakan"
            )

        user = User(
            user_type=UserType.guru,
            registration_status=RegistrationStatus.pending,
            username=None,
            password_hash=None,
            is_active=False,
        )
        self.db.add(user)
        await self.db.flush()

        profile_data = request.model_dump(exclude_unset=True)
        profile = GuruProfile(
            user_id=user.user_id,
            nama_lengkap=request.nama_lengkap,
            nip=request.nip,
            status_guru=StatusGuru.aktif,
            kewarganegaraan=profile_data.get("kewarganegaraan", "Indonesia"),
        )
        optional_fields = [
            "dob", "tempat_lahir", "jenis_kelamin", "alamat",
            "nik", "tahun_masuk", "kontak", "structural_role",
            "bidang_wakasek", "mata_pelajaran", "pendidikan_terakhir",
        ]
        for field in optional_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])

        self.db.add(profile)
        await self.db.commit()

        return PreRegisterResponseDTO(
            message=f"Guru '{request.nama_lengkap}' berhasil didaftarkan (PENDING)"
        )
