from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tugas import Tugas
from app.models.semester import Semester
from app.models.kelas import Kelas
from app.models.mata_pelajaran import MataPelajaran
from app.models.guru_mapel import GuruMapel
from app.models.siswa_kelas import SiswaKelas
from app.models.user import User
from app.enums import UserType
from app.dto.penilaian.tugas_dto import (
    CreateTugasDTO, UpdateTugasDTO, TugasResponseDTO, MessageResponseDTO,
)


class TugasService:
    """
    Service for assignment/assessment management.

    Raises:
        HTTPException: 400, 403, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _to_dto(self, tugas: Tugas) -> TugasResponseDTO:
        return TugasResponseDTO(
            tugas_id=tugas.tugas_id,
            semester_id=tugas.semester_id,
            kelas_id=tugas.kelas_id,
            mapel_id=tugas.mapel_id,
            created_by=tugas.created_by,
            jenis=tugas.jenis,
            judul=tugas.judul,
            deskripsi=tugas.deskripsi,
            link_tugas=tugas.link_tugas,
            deadline=tugas.deadline,
            created_at=tugas.created_at,
        )

    async def _validate_guru_teaches(
        self, user_id: UUID, kelas_id: UUID, mapel_id: UUID
    ) -> None:
        """Check guru_mapel table to verify teacher teaches this mapel in this kelas."""
        result = await self.db.execute(
            select(GuruMapel).where(
                and_(
                    GuruMapel.user_id == user_id,
                    GuruMapel.kelas_id == kelas_id,
                    GuruMapel.mapel_id == mapel_id,
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to teach this subject in this class"
            )

    async def _get_student_kelas_id(
        self, user_id: UUID, semester_id: UUID
    ) -> UUID:
        """Resolve student's kelas for the given semester's tahun_ajaran."""
        result = await self.db.execute(
            select(SiswaKelas.kelas_id)
            .join(Kelas, SiswaKelas.kelas_id == Kelas.kelas_id)
            .join(Semester, Semester.tahun_ajaran_id == Kelas.tahun_ajaran_id)
            .where(
                and_(
                    SiswaKelas.user_id == user_id,
                    Semester.semester_id == semester_id,
                )
            )
        )
        kelas_id = result.scalar_one_or_none()
        if not kelas_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student is not assigned to any class for this semester"
            )
        return kelas_id

    # ── CRUD ───────────────────────────────────────────────────────────────────

    async def create_tugas(
        self, request: CreateTugasDTO, current_user: User
    ) -> TugasResponseDTO:
        """
        Create a new tugas entry.

        Raises:
            HTTPException: 404 if semester/kelas/mapel not found
            HTTPException: 403 if guru doesn't teach this mapel+kelas
            HTTPException: 500 on database error
        """
        try:
            # Validate FK existence
            semester = await self.db.execute(
                select(Semester).where(Semester.semester_id == request.semester_id)
            )
            if not semester.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Semester with ID {request.semester_id} not found"
                )

            kelas = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == request.kelas_id)
            )
            if not kelas.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {request.kelas_id} not found"
                )

            mapel = await self.db.execute(
                select(MataPelajaran).where(MataPelajaran.mapel_id == request.mapel_id)
            )
            if not mapel.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mata pelajaran with ID {request.mapel_id} not found"
                )

            # Permission: guru must teach this mapel in this kelas
            if current_user.user_type == UserType.guru:
                await self._validate_guru_teaches(
                    current_user.user_id, request.kelas_id, request.mapel_id
                )

            tugas = Tugas(
                semester_id=request.semester_id,
                kelas_id=request.kelas_id,
                mapel_id=request.mapel_id,
                created_by=current_user.user_id,
                jenis=request.jenis,
                judul=request.judul,
                deskripsi=request.deskripsi,
                link_tugas=request.link_tugas,
                deadline=request.deadline,
            )

            self.db.add(tugas)
            await self.db.commit()
            await self.db.refresh(tugas)

            return self._to_dto(tugas)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create tugas: {str(e)}"
            )

    async def get_tugas(self, tugas_id: UUID) -> TugasResponseDTO:
        """
        Get tugas by ID.

        Raises:
            HTTPException: 404 if not found
        """
        result = await self.db.execute(
            select(Tugas).where(Tugas.tugas_id == tugas_id)
        )
        tugas = result.scalar_one_or_none()
        if not tugas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tugas with ID {tugas_id} not found"
            )
        return self._to_dto(tugas)

    async def list_tugas_by_kelas(
        self,
        kelas_id: UUID,
        semester_id: UUID,
        mapel_id: Optional[UUID] = None,
    ) -> list[TugasResponseDTO]:
        """
        List tugas for a kelas in a semester, optionally filtered by mapel.

        Raises:
            HTTPException: 500 on database error
        """
        conditions = [
            Tugas.kelas_id == kelas_id,
            Tugas.semester_id == semester_id,
        ]
        if mapel_id:
            conditions.append(Tugas.mapel_id == mapel_id)

        result = await self.db.execute(
            select(Tugas).where(and_(*conditions)).order_by(Tugas.created_at.desc())
        )
        return [self._to_dto(t) for t in result.scalars().all()]

    async def list_tugas_my_class(
        self, current_user: User, semester_id: UUID
    ) -> list[TugasResponseDTO]:
        """
        List tugas for the student's own class.

        Raises:
            HTTPException: 404 if student not in any class
        """
        kelas_id = await self._get_student_kelas_id(
            current_user.user_id, semester_id
        )
        return await self.list_tugas_by_kelas(kelas_id, semester_id)

    async def update_tugas(
        self, tugas_id: UUID, request: UpdateTugasDTO, current_user: User
    ) -> TugasResponseDTO:
        """
        Update a tugas entry. Only creator or admin can update.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if not creator and not admin
            HTTPException: 400 if no fields to update
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(Tugas).where(Tugas.tugas_id == tugas_id)
            )
            tugas = result.scalar_one_or_none()
            if not tugas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tugas with ID {tugas_id} not found"
                )

            # Permission: only creator or admin
            if (
                current_user.user_type != UserType.admin
                and tugas.created_by != current_user.user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator or admin can update this tugas"
                )

            update_data = request.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )

            for field, value in update_data.items():
                setattr(tugas, field, value)

            await self.db.commit()
            await self.db.refresh(tugas)

            return self._to_dto(tugas)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update tugas: {str(e)}"
            )

    async def delete_tugas(
        self, tugas_id: UUID, current_user: User
    ) -> MessageResponseDTO:
        """
        Delete a tugas entry. Only creator or admin can delete.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if not creator and not admin
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(Tugas).where(Tugas.tugas_id == tugas_id)
            )
            tugas = result.scalar_one_or_none()
            if not tugas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tugas with ID {tugas_id} not found"
                )

            if (
                current_user.user_type != UserType.admin
                and tugas.created_by != current_user.user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator or admin can delete this tugas"
                )

            await self.db.delete(tugas)
            await self.db.commit()

            return MessageResponseDTO(message="Tugas deleted successfully")

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete tugas: {str(e)}"
            )
