from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.nilai import Nilai
from app.models.tugas import Tugas
from app.models.guru_mapel import GuruMapel
from app.models.siswa_kelas import SiswaKelas
from app.models.user import User
from app.enums import UserType
from app.dto.penilaian.nilai_dto import (
    CreateNilaiDTO, BulkCreateNilaiDTO, UpdateNilaiDTO,
    NilaiResponseDTO, BulkNilaiResponseDTO, MessageResponseDTO,
)


class NilaiService:
    """
    Service for student grade management.

    Raises:
        HTTPException: 400, 403, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _to_dto(self, nilai: Nilai) -> NilaiResponseDTO:
        return NilaiResponseDTO(
            nilai_id=nilai.nilai_id,
            tugas_id=nilai.tugas_id,
            user_id=nilai.user_id,
            nilai=float(nilai.nilai),
            catatan=nilai.catatan,
        )

    async def _get_tugas(self, tugas_id: UUID) -> Tugas:
        """Fetch tugas or raise 404."""
        result = await self.db.execute(
            select(Tugas).where(Tugas.tugas_id == tugas_id)
        )
        tugas = result.scalar_one_or_none()
        if not tugas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tugas with ID {tugas_id} not found"
            )
        return tugas

    async def _validate_guru_permission(
        self, current_user: User, tugas: Tugas
    ) -> None:
        """Guru must be creator or teach the mapel+kelas."""
        if current_user.user_type == UserType.admin:
            return

        # Check if creator
        if tugas.created_by == current_user.user_id:
            return

        # Check if teaches this mapel in this kelas
        result = await self.db.execute(
            select(GuruMapel).where(
                and_(
                    GuruMapel.user_id == current_user.user_id,
                    GuruMapel.kelas_id == tugas.kelas_id,
                    GuruMapel.mapel_id == tugas.mapel_id,
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to manage scores for this tugas"
            )

    async def _validate_student_in_kelas(
        self, user_id: UUID, kelas_id: UUID
    ) -> None:
        """Verify user is a siswa and in the kelas."""
        # Check user is siswa
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        if user.user_type != UserType.siswa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user.username} is not a student"
            )

        # Check student in kelas
        result = await self.db.execute(
            select(SiswaKelas).where(
                and_(
                    SiswaKelas.user_id == user_id,
                    SiswaKelas.kelas_id == kelas_id,
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {user_id} is not in this class"
            )

    # ── CRUD ───────────────────────────────────────────────────────────────────

    async def create_nilai(
        self, tugas_id: UUID, request: CreateNilaiDTO, current_user: User
    ) -> NilaiResponseDTO:
        """
        Create a single score for a student.

        Raises:
            HTTPException: 404 if tugas/user not found
            HTTPException: 403 if no permission
            HTTPException: 400 if student not in class or duplicate
            HTTPException: 500 on database error
        """
        try:
            tugas = await self._get_tugas(tugas_id)
            await self._validate_guru_permission(current_user, tugas)
            await self._validate_student_in_kelas(request.user_id, tugas.kelas_id)

            # Check duplicate
            existing = await self.db.execute(
                select(Nilai).where(
                    and_(
                        Nilai.tugas_id == tugas_id,
                        Nilai.user_id == request.user_id,
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Score already exists for student {request.user_id} on this tugas"
                )

            nilai = Nilai(
                tugas_id=tugas_id,
                user_id=request.user_id,
                nilai=request.nilai,
                catatan=request.catatan,
            )

            self.db.add(nilai)
            await self.db.commit()
            await self.db.refresh(nilai)

            return self._to_dto(nilai)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create nilai: {str(e)}"
            )

    async def bulk_create_nilai(
        self, tugas_id: UUID, request: BulkCreateNilaiDTO, current_user: User
    ) -> BulkNilaiResponseDTO:
        """
        Bulk create/update scores for a tugas (upsert).

        Raises:
            HTTPException: 404 if tugas not found
            HTTPException: 403 if no permission
            HTTPException: 500 on database error
        """
        try:
            tugas = await self._get_tugas(tugas_id)
            await self._validate_guru_permission(current_user, tugas)

            created = 0
            updated = 0

            for entry in request.entries:
                await self._validate_student_in_kelas(entry.user_id, tugas.kelas_id)

                # Check existing
                result = await self.db.execute(
                    select(Nilai).where(
                        and_(
                            Nilai.tugas_id == tugas_id,
                            Nilai.user_id == entry.user_id,
                        )
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.nilai = entry.nilai
                    existing.catatan = entry.catatan
                    updated += 1
                else:
                    nilai = Nilai(
                        tugas_id=tugas_id,
                        user_id=entry.user_id,
                        nilai=entry.nilai,
                        catatan=entry.catatan,
                    )
                    self.db.add(nilai)
                    created += 1

            await self.db.commit()

            return BulkNilaiResponseDTO(
                created_count=created,
                updated_count=updated,
                message=f"Bulk nilai: {created} created, {updated} updated"
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to bulk create nilai: {str(e)}"
            )

    async def list_nilai_by_tugas(
        self, tugas_id: UUID, current_user: User
    ) -> list[NilaiResponseDTO]:
        """
        List all scores for a tugas.

        Raises:
            HTTPException: 404 if tugas not found
            HTTPException: 403 if no permission
        """
        tugas = await self._get_tugas(tugas_id)
        await self._validate_guru_permission(current_user, tugas)

        result = await self.db.execute(
            select(Nilai).where(Nilai.tugas_id == tugas_id)
        )
        return [self._to_dto(n) for n in result.scalars().all()]

    async def list_my_scores(
        self, current_user: User, semester_id: Optional[UUID] = None
    ) -> list[NilaiResponseDTO]:
        """
        List scores for the current student, optionally filtered by semester.

        Raises:
            HTTPException: 500 on database error
        """
        if semester_id:
            result = await self.db.execute(
                select(Nilai)
                .join(Tugas, Nilai.tugas_id == Tugas.tugas_id)
                .where(
                    and_(
                        Nilai.user_id == current_user.user_id,
                        Tugas.semester_id == semester_id,
                    )
                )
            )
        else:
            result = await self.db.execute(
                select(Nilai).where(Nilai.user_id == current_user.user_id)
            )
        return [self._to_dto(n) for n in result.scalars().all()]

    async def update_nilai(
        self, nilai_id: UUID, request: UpdateNilaiDTO, current_user: User
    ) -> NilaiResponseDTO:
        """
        Update a score.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if no permission
            HTTPException: 400 if no fields to update
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(Nilai).where(Nilai.nilai_id == nilai_id)
            )
            nilai = result.scalar_one_or_none()
            if not nilai:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nilai with ID {nilai_id} not found"
                )

            tugas = await self._get_tugas(nilai.tugas_id)
            await self._validate_guru_permission(current_user, tugas)

            update_data = request.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )

            for field, value in update_data.items():
                setattr(nilai, field, value)

            await self.db.commit()
            await self.db.refresh(nilai)

            return self._to_dto(nilai)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update nilai: {str(e)}"
            )

    async def delete_nilai(
        self, nilai_id: UUID, current_user: User
    ) -> MessageResponseDTO:
        """
        Delete a score.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if no permission
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(Nilai).where(Nilai.nilai_id == nilai_id)
            )
            nilai = result.scalar_one_or_none()
            if not nilai:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nilai with ID {nilai_id} not found"
                )

            tugas = await self._get_tugas(nilai.tugas_id)
            await self._validate_guru_permission(current_user, tugas)

            await self.db.delete(nilai)
            await self.db.commit()

            return MessageResponseDTO(message="Nilai deleted successfully")

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete nilai: {str(e)}"
            )
