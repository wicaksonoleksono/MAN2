from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.kelas import Kelas
from app.models.siswa_kelas import SiswaKelas
from app.models.tahun_ajaran import TahunAjaran
from app.models.user import User
from app.enums import UserType
from app.dto.akademik.kelas_dto import (
    CreateKelasDTO,
    UpdateKelasDTO,
    KelasResponseDTO,
    AssignSiswaDTO,
    SiswaKelasResponseDTO,
    MessageResponseDTO
)


class KelasService:
    """
    Service for managing Kelas (class/rombel) and SiswaKelas (student-class assignment)

    Raises:
        HTTPException: 400, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_kelas_dto(self, kelas: Kelas) -> KelasResponseDTO:
        """Convert Kelas model to KelasResponseDTO"""
        return KelasResponseDTO(
            kelas_id=kelas.kelas_id,
            tahun_ajaran_id=kelas.tahun_ajaran_id,
            nama_kelas=kelas.nama_kelas,
            tingkat=kelas.tingkat,
            jurusan=kelas.jurusan,
            wali_kelas_id=kelas.wali_kelas_id,
            kapasitas=kelas.kapasitas
        )

    def _to_siswa_kelas_dto(self, siswa_kelas: SiswaKelas) -> SiswaKelasResponseDTO:
        """Convert SiswaKelas model to SiswaKelasResponseDTO"""
        return SiswaKelasResponseDTO(
            siswa_kelas_id=siswa_kelas.siswa_kelas_id,
            kelas_id=siswa_kelas.kelas_id,
            user_id=siswa_kelas.user_id
        )

    async def create_kelas(self, request: CreateKelasDTO) -> KelasResponseDTO:
        """
        Create a new kelas (class/rombel)

        Args:
            request: Kelas creation data

        Returns:
            KelasResponseDTO: Created kelas information

        Raises:
            HTTPException: 404 if tahun_ajaran not found
            HTTPException: 404 if wali_kelas not found
            HTTPException: 400 if wali_kelas is not a guru
            HTTPException: 400 if kelas with same name exists in tahun_ajaran
            HTTPException: 500 if database error occurs
        """
        try:
            # Validate tahun_ajaran exists
            result = await self.db.execute(
                select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == request.tahun_ajaran_id)
            )
            tahun_ajaran = result.scalar_one_or_none()

            if not tahun_ajaran:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tahun ajaran with ID {request.tahun_ajaran_id} not found"
                )

            # Validate wali_kelas if provided
            if request.wali_kelas_id:
                result = await self.db.execute(
                    select(User).where(User.user_id == request.wali_kelas_id)
                )
                wali_kelas = result.scalar_one_or_none()

                if not wali_kelas:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with ID {request.wali_kelas_id} not found"
                    )

                if wali_kelas.user_type != UserType.guru:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {wali_kelas.username} is not a guru (current type: {wali_kelas.user_type.value})"
                    )

            # Check for duplicate kelas name in same tahun_ajaran
            result = await self.db.execute(
                select(Kelas).where(
                    Kelas.tahun_ajaran_id == request.tahun_ajaran_id,
                    Kelas.nama_kelas == request.nama_kelas
                )
            )
            existing_kelas = result.scalar_one_or_none()

            if existing_kelas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kelas '{request.nama_kelas}' already exists in tahun ajaran {tahun_ajaran.nama}"
                )

            # Create kelas
            kelas = Kelas(
                tahun_ajaran_id=request.tahun_ajaran_id,
                nama_kelas=request.nama_kelas,
                tingkat=request.tingkat,
                jurusan=request.jurusan,
                wali_kelas_id=request.wali_kelas_id,
                kapasitas=request.kapasitas
            )

            self.db.add(kelas)
            await self.db.commit()
            await self.db.refresh(kelas)

            return self._to_kelas_dto(kelas)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create kelas: {str(e)}"
            )

    async def list_kelas(self) -> list[KelasResponseDTO]:
        """
        List all kelas

        Returns:
            list[KelasResponseDTO]: List of all kelas

        Raises:
            HTTPException: 500 if database error occurs
        """
        try:
            result = await self.db.execute(select(Kelas))
            kelas_list = result.scalars().all()
            return [self._to_kelas_dto(kelas) for kelas in kelas_list]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list kelas: {str(e)}"
            )

    async def get_kelas(self, kelas_id: UUID) -> KelasResponseDTO:
        """
        Get a specific kelas by ID

        Args:
            kelas_id: Kelas ID

        Returns:
            KelasResponseDTO: Kelas information

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 500 if database error occurs
        """
        try:
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == kelas_id)
            )
            kelas = result.scalar_one_or_none()

            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {kelas_id} not found"
                )

            return self._to_kelas_dto(kelas)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get kelas: {str(e)}"
            )

    async def list_kelas_by_tahun_ajaran(self, tahun_ajaran_id: UUID) -> list[KelasResponseDTO]:
        """
        List all kelas in a specific tahun ajaran

        Args:
            tahun_ajaran_id: Tahun ajaran ID

        Returns:
            list[KelasResponseDTO]: List of kelas in the tahun ajaran

        Raises:
            HTTPException: 500 if database error occurs
        """
        try:
            result = await self.db.execute(
                select(Kelas).where(Kelas.tahun_ajaran_id == tahun_ajaran_id)
            )
            kelas_list = result.scalars().all()
            return [self._to_kelas_dto(kelas) for kelas in kelas_list]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list kelas by tahun ajaran: {str(e)}"
            )

    async def update_kelas(self, kelas_id: UUID, request: UpdateKelasDTO) -> KelasResponseDTO:
        """
        Update a kelas

        Args:
            kelas_id: Kelas ID
            request: Update data

        Returns:
            KelasResponseDTO: Updated kelas information

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 404 if wali_kelas not found
            HTTPException: 400 if wali_kelas is not a guru
            HTTPException: 400 if no fields to update
            HTTPException: 500 if database error occurs
        """
        try:
            # Get existing kelas
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == kelas_id)
            )
            kelas = result.scalar_one_or_none()

            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {kelas_id} not found"
                )

            # Get update data
            update_data = request.model_dump(exclude_unset=True)

            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )

            # Validate wali_kelas if being updated
            if "wali_kelas_id" in update_data and update_data["wali_kelas_id"] is not None:
                result = await self.db.execute(
                    select(User).where(User.user_id == update_data["wali_kelas_id"])
                )
                wali_kelas = result.scalar_one_or_none()

                if not wali_kelas:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with ID {update_data['wali_kelas_id']} not found"
                    )

                if wali_kelas.user_type != UserType.guru:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {wali_kelas.username} is not a guru (current type: {wali_kelas.user_type.value})"
                    )

            # Update fields
            for field, value in update_data.items():
                setattr(kelas, field, value)

            await self.db.commit()
            await self.db.refresh(kelas)

            return self._to_kelas_dto(kelas)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update kelas: {str(e)}"
            )

    async def delete_kelas(self, kelas_id: UUID) -> MessageResponseDTO:
        """
        Delete a kelas

        Args:
            kelas_id: Kelas ID

        Returns:
            MessageResponseDTO: Success message

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 500 if database error occurs
        """
        try:
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == kelas_id)
            )
            kelas = result.scalar_one_or_none()

            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {kelas_id} not found"
                )

            await self.db.delete(kelas)
            await self.db.commit()

            return MessageResponseDTO(
                message=f"Kelas '{kelas.nama_kelas}' deleted successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete kelas: {str(e)}"
            )

    async def assign_siswa(self, kelas_id: UUID, request: AssignSiswaDTO) -> SiswaKelasResponseDTO:
        """
        Assign a siswa to a kelas

        Args:
            kelas_id: Kelas ID
            request: Assignment data with user_id

        Returns:
            SiswaKelasResponseDTO: Created assignment information

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 404 if user not found
            HTTPException: 400 if user is not a siswa
            HTTPException: 400 if siswa already assigned to this kelas
            HTTPException: 400 if kelas capacity exceeded
            HTTPException: 500 if database error occurs
        """
        try:
            # Validate kelas exists
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == kelas_id)
            )
            kelas = result.scalar_one_or_none()

            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {kelas_id} not found"
                )

            # Validate user exists and is a siswa
            result = await self.db.execute(
                select(User).where(User.user_id == request.user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {request.user_id} not found"
                )

            if user.user_type != UserType.siswa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {user.username} is not a siswa (current type: {user.user_type.value})"
                )

            # Check if already assigned
            result = await self.db.execute(
                select(SiswaKelas).where(
                    SiswaKelas.kelas_id == kelas_id,
                    SiswaKelas.user_id == request.user_id
                )
            )
            existing_assignment = result.scalar_one_or_none()

            if existing_assignment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Siswa {user.username} is already assigned to kelas {kelas.nama_kelas}"
                )

            # Check capacity
            result = await self.db.execute(
                select(func.count(SiswaKelas.siswa_kelas_id)).where(
                    SiswaKelas.kelas_id == kelas_id
                )
            )
            current_count = result.scalar()

            if current_count >= kelas.kapasitas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kelas {kelas.nama_kelas} has reached maximum capacity ({kelas.kapasitas})"
                )

            # Create assignment
            siswa_kelas = SiswaKelas(
                kelas_id=kelas_id,
                user_id=request.user_id
            )

            self.db.add(siswa_kelas)
            await self.db.commit()
            await self.db.refresh(siswa_kelas)

            return self._to_siswa_kelas_dto(siswa_kelas)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to assign siswa to kelas: {str(e)}"
            )

    async def remove_siswa(self, kelas_id: UUID, user_id: UUID) -> MessageResponseDTO:
        """
        Remove a siswa from a kelas

        Args:
            kelas_id: Kelas ID
            user_id: User ID of the siswa

        Returns:
            MessageResponseDTO: Success message

        Raises:
            HTTPException: 404 if assignment not found
            HTTPException: 500 if database error occurs
        """
        try:
            result = await self.db.execute(
                select(SiswaKelas).where(
                    SiswaKelas.kelas_id == kelas_id,
                    SiswaKelas.user_id == user_id
                )
            )
            siswa_kelas = result.scalar_one_or_none()

            if not siswa_kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Siswa assignment not found for kelas_id {kelas_id} and user_id {user_id}"
                )

            await self.db.delete(siswa_kelas)
            await self.db.commit()

            return MessageResponseDTO(
                message="Siswa removed from kelas successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove siswa from kelas: {str(e)}"
            )

    async def list_siswa_in_kelas(self, kelas_id: UUID) -> list[SiswaKelasResponseDTO]:
        """
        List all siswa in a kelas

        Args:
            kelas_id: Kelas ID

        Returns:
            list[SiswaKelasResponseDTO]: List of siswa assignments in the kelas

        Raises:
            HTTPException: 404 if kelas not found
            HTTPException: 500 if database error occurs
        """
        try:
            # Validate kelas exists
            result = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == kelas_id)
            )
            kelas = result.scalar_one_or_none()

            if not kelas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {kelas_id} not found"
                )

            # Get all siswa in kelas
            result = await self.db.execute(
                select(SiswaKelas).where(SiswaKelas.kelas_id == kelas_id)
            )
            siswa_kelas_list = result.scalars().all()

            return [self._to_siswa_kelas_dto(sk) for sk in siswa_kelas_list]

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list siswa in kelas: {str(e)}"
            )
