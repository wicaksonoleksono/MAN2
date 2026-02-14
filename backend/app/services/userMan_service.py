import secrets
import string
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.guru_profile import GuruProfile
from app.enums import UserType
from app.dto.userMan.userman_request import (
    CreateStudentRequestDTO, UpdateStudentRequestDTO,
    CreateGuruRequestDTO, UpdateGuruRequestDTO,
)
from app.dto.userMan.userman_response import (
    CreateStudentResponseDTO, StudentProfileResponseDTO,
    CreateGuruResponseDTO, GuruProfileResponseDTO,
    PaginatedStudentsResponse, PaginatedTeachersResponse, MessageResponseDTO,
)


class UserManagementService:
    """
    User management service for CRUD on students and teachers.

    Only accessible by Admin.

    Raises:
        HTTPException: 400, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_password(self, length: int = 10) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_username(self, nama_lengkap: str, identifier: str) -> str:
        base = nama_lengkap.lower().strip().replace(" ", "_")
        base = ''.join(c for c in base if c.isalnum() or c == '_')
        suffix = identifier[-4:] if len(identifier) >= 4 else identifier
        return f"{base}_{suffix}"

    async def create_student(self, request: CreateStudentRequestDTO) -> CreateStudentResponseDTO:
        """
        Create a new student: auth user (users) + profile (siswa_profiles) in one transaction.

        Raises:
            HTTPException: 400 if NIS already exists
            HTTPException: 500 if database error
        """
        try:
            # Check if NIS already exists
            result = await self.db.execute(
                select(SiswaProfile).where(SiswaProfile.nis == request.nis)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NIS '{request.nis}' already exists"
                )

            # Generate unique username
            username = self._generate_username(request.nama_lengkap, request.nis)
            base_username = username
            counter = 1
            while True:
                result = await self.db.execute(
                    select(User).where(User.username == username)
                )
                if not result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            generated_password = self._generate_password()

            # Create auth user
            user = User(
                username=username,
                user_type=UserType.siswa,
            )
            user.set_password(generated_password)
            self.db.add(user)
            await self.db.flush()  # get user_id without committing

            # Create profile
            profile = SiswaProfile(
                user_id=user.user_id,
                nis=request.nis,
                nama_lengkap=request.nama_lengkap,
                dob=request.dob,
                tempat_lahir=request.tempat_lahir,
                jenis_kelamin=request.jenis_kelamin,
                alamat=request.alamat,
                nama_wali=request.nama_wali,
                nik=request.nik,
                kelas_jurusan=request.kelas_jurusan,
                tahun_masuk=request.tahun_masuk,
                kontak=request.kontak,
                kewarganegaraan=request.kewarganegaraan,
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

            return CreateStudentResponseDTO(
                message="Student created successfully",
                username=username,
                generated_password=generated_password,
                profile=self._to_student_dto(profile),
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create student: {str(e)}"
            )

    async def create_guru(self, request: CreateGuruRequestDTO) -> CreateGuruResponseDTO:
        """
        Create a new teacher: auth user (users) + profile (guru_profiles) in one transaction.

        Raises:
            HTTPException: 400 if NIP already exists
            HTTPException: 500 if database error
        """
        try:
            # Check if NIP already exists
            result = await self.db.execute(
                select(GuruProfile).where(GuruProfile.nip == request.nip)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NIP '{request.nip}' already exists"
                )

            # Generate unique username
            username = self._generate_username(request.nama_lengkap, request.nip)
            base_username = username
            counter = 1
            while True:
                result = await self.db.execute(
                    select(User).where(User.username == username)
                )
                if not result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            generated_password = self._generate_password()

            # Create auth user
            user = User(
                username=username,
                user_type=UserType.guru,
            )
            user.set_password(generated_password)
            self.db.add(user)
            await self.db.flush()

            # Create profile
            profile = GuruProfile(
                user_id=user.user_id,
                nip=request.nip,
                nama_lengkap=request.nama_lengkap,
                dob=request.dob,
                tempat_lahir=request.tempat_lahir,
                jenis_kelamin=request.jenis_kelamin,
                alamat=request.alamat,
                nik=request.nik,
                tahun_masuk=request.tahun_masuk,
                kontak=request.kontak,
                kewarganegaraan=request.kewarganegaraan,
                structural_role=request.structural_role,
                bidang_wakasek=request.bidang_wakasek,
                mata_pelajaran=request.mata_pelajaran,
                pendidikan_terakhir=request.pendidikan_terakhir,
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

            return CreateGuruResponseDTO(
                message="Teacher created successfully",
                username=username,
                generated_password=generated_password,
                profile=self._to_guru_dto(profile),
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create teacher: {str(e)}"
            )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _to_student_dto(self, profile: SiswaProfile) -> StudentProfileResponseDTO:
        return StudentProfileResponseDTO(
            siswa_id=profile.siswa_id,
            nis=profile.nis,
            nama_lengkap=profile.nama_lengkap,
            dob=profile.dob,
            tempat_lahir=profile.tempat_lahir,
            jenis_kelamin=profile.jenis_kelamin,
            alamat=profile.alamat,
            nama_wali=profile.nama_wali,
            nik=profile.nik,
            kelas_jurusan=profile.kelas_jurusan,
            tahun_masuk=profile.tahun_masuk,
            status_siswa=profile.status_siswa,
            kontak=profile.kontak,
            kewarganegaraan=profile.kewarganegaraan,
        )

    def _to_guru_dto(self, profile: GuruProfile) -> GuruProfileResponseDTO:
        return GuruProfileResponseDTO(
            guru_id=profile.guru_id,
            nip=profile.nip,
            nama_lengkap=profile.nama_lengkap,
            dob=profile.dob,
            tempat_lahir=profile.tempat_lahir,
            jenis_kelamin=profile.jenis_kelamin,
            alamat=profile.alamat,
            nik=profile.nik,
            tahun_masuk=profile.tahun_masuk,
            status_guru=profile.status_guru,
            kontak=profile.kontak,
            kewarganegaraan=profile.kewarganegaraan,
            structural_role=profile.structural_role,
            bidang_wakasek=profile.bidang_wakasek,
            mata_pelajaran=profile.mata_pelajaran,
            pendidikan_terakhir=profile.pendidikan_terakhir,
        )

    # ── Student CRUD ─────────────────────────────────────────────────────────

    async def list_students(
        self, skip: int = 0, limit: int = 30, search: Optional[str] = None
    ) -> PaginatedStudentsResponse:
        """
        List student profiles with pagination and optional search.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            search: Optional search term (ILIKE across nis, nama_lengkap, nik, kelas_jurusan, kontak, tempat_lahir)

        Raises:
            HTTPException: 500 if database error
        """
        search_filter = None
        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                SiswaProfile.nis.ilike(pattern),
                SiswaProfile.nama_lengkap.ilike(pattern),
                SiswaProfile.nik.ilike(pattern),
                SiswaProfile.kelas_jurusan.ilike(pattern),
                SiswaProfile.kontak.ilike(pattern),
                SiswaProfile.tempat_lahir.ilike(pattern),
            )

        count_query = select(func.count()).select_from(SiswaProfile)
        data_query = select(SiswaProfile)

        if search_filter is not None:
            count_query = count_query.where(search_filter)
            data_query = data_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        result = await self.db.execute(data_query.offset(skip).limit(limit))
        profiles = result.scalars().all()

        return PaginatedStudentsResponse(
            items=[self._to_student_dto(p) for p in profiles],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_student(self, siswa_id: UUID) -> StudentProfileResponseDTO:
        """
        Get a single student profile by ID.

        Raises:
            HTTPException: 404 if student not found
        """
        result = await self.db.execute(
            select(SiswaProfile).where(SiswaProfile.siswa_id == siswa_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        return self._to_student_dto(profile)

    async def update_student(
        self, siswa_id: UUID, request: UpdateStudentRequestDTO
    ) -> StudentProfileResponseDTO:
        """
        Partial update a student profile.

        Raises:
            HTTPException: 404 if student not found
            HTTPException: 400 if NIS conflict
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(SiswaProfile).where(SiswaProfile.siswa_id == siswa_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Check NIS uniqueness if being changed
        if "nis" in update_data and update_data["nis"] != profile.nis:
            nis_check = await self.db.execute(
                select(SiswaProfile).where(SiswaProfile.nis == update_data["nis"])
            )
            if nis_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NIS '{update_data['nis']}' already exists"
                )

        for field, value in update_data.items():
            setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return self._to_student_dto(profile)

    async def delete_student(self, siswa_id: UUID) -> MessageResponseDTO:
        """
        Delete a student profile and its associated user account.

        Raises:
            HTTPException: 404 if student not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(SiswaProfile).where(SiswaProfile.siswa_id == siswa_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Delete the user row — CASCADE will remove the profile
        user_result = await self.db.execute(
            select(User).where(User.user_id == profile.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            await self.db.delete(user)

        await self.db.commit()
        return MessageResponseDTO(message="Student deleted successfully")

    # ── Guru CRUD ────────────────────────────────────────────────────────────

    async def list_gurus(
        self, skip: int = 0, limit: int = 30, search: Optional[str] = None
    ) -> PaginatedTeachersResponse:
        """
        List teacher profiles with pagination and optional search.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            search: Optional search term (ILIKE across nip, nama_lengkap, nik, kontak, mata_pelajaran, tempat_lahir)

        Raises:
            HTTPException: 500 if database error
        """
        search_filter = None
        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                GuruProfile.nip.ilike(pattern),
                GuruProfile.nama_lengkap.ilike(pattern),
                GuruProfile.nik.ilike(pattern),
                GuruProfile.kontak.ilike(pattern),
                GuruProfile.mata_pelajaran.ilike(pattern),
                GuruProfile.tempat_lahir.ilike(pattern),
            )

        count_query = select(func.count()).select_from(GuruProfile)
        data_query = select(GuruProfile)

        if search_filter is not None:
            count_query = count_query.where(search_filter)
            data_query = data_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        result = await self.db.execute(data_query.offset(skip).limit(limit))
        profiles = result.scalars().all()

        return PaginatedTeachersResponse(
            items=[self._to_guru_dto(p) for p in profiles],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_guru(self, guru_id: UUID) -> GuruProfileResponseDTO:
        """
        Get a single teacher profile by ID.

        Raises:
            HTTPException: 404 if teacher not found
        """
        result = await self.db.execute(
            select(GuruProfile).where(GuruProfile.guru_id == guru_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        return self._to_guru_dto(profile)

    async def update_guru(
        self, guru_id: UUID, request: UpdateGuruRequestDTO
    ) -> GuruProfileResponseDTO:
        """
        Partial update a teacher profile.

        Raises:
            HTTPException: 404 if teacher not found
            HTTPException: 400 if NIP conflict
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(GuruProfile).where(GuruProfile.guru_id == guru_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Check NIP uniqueness if being changed
        if "nip" in update_data and update_data["nip"] != profile.nip:
            nip_check = await self.db.execute(
                select(GuruProfile).where(GuruProfile.nip == update_data["nip"])
            )
            if nip_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NIP '{update_data['nip']}' already exists"
                )

        for field, value in update_data.items():
            setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return self._to_guru_dto(profile)

    async def delete_guru(self, guru_id: UUID) -> MessageResponseDTO:
        """
        Delete a teacher profile and its associated user account.

        Raises:
            HTTPException: 404 if teacher not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(GuruProfile).where(GuruProfile.guru_id == guru_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        user_result = await self.db.execute(
            select(User).where(User.user_id == profile.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            await self.db.delete(user)

        await self.db.commit()
        return MessageResponseDTO(message="Teacher deleted successfully")
