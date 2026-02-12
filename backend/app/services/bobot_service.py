from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bobot_penilaian import BobotPenilaian
from app.models.mata_pelajaran import MataPelajaran
from app.models.kelas import Kelas
from app.models.semester import Semester
from app.models.guru_mapel import GuruMapel
from app.models.user import User
from app.enums import UserType
from app.dto.penilaian.bobot_dto import (
    CreateBobotDTO, UpdateBobotDTO, BobotResponseDTO, MessageResponseDTO,
)


class BobotService:
    """
    Service for assessment weight management.

    Raises:
        HTTPException: 400, 403, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _to_dto(self, bobot: BobotPenilaian) -> BobotResponseDTO:
        return BobotResponseDTO(
            bobot_id=bobot.bobot_id,
            mapel_id=bobot.mapel_id,
            kelas_id=bobot.kelas_id,
            semester_id=bobot.semester_id,
            jenis=bobot.jenis,
            bobot=bobot.bobot,
        )

    async def _validate_guru_teaches(
        self, user_id: UUID, kelas_id: UUID, mapel_id: UUID
    ) -> None:
        """Check guru teaches this mapel in this kelas."""
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

    # ── CRUD ───────────────────────────────────────────────────────────────────

    async def create_bobot(
        self, request: CreateBobotDTO, current_user: User
    ) -> BobotResponseDTO:
        """
        Create a weight entry.

        Raises:
            HTTPException: 404 if mapel/kelas/semester not found
            HTTPException: 403 if guru doesn't teach this mapel+kelas
            HTTPException: 400 if duplicate
            HTTPException: 500 on database error
        """
        try:
            # Validate FK existence
            mapel = await self.db.execute(
                select(MataPelajaran).where(MataPelajaran.mapel_id == request.mapel_id)
            )
            if not mapel.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Mata pelajaran with ID {request.mapel_id} not found"
                )

            kelas = await self.db.execute(
                select(Kelas).where(Kelas.kelas_id == request.kelas_id)
            )
            if not kelas.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Kelas with ID {request.kelas_id} not found"
                )

            semester = await self.db.execute(
                select(Semester).where(Semester.semester_id == request.semester_id)
            )
            if not semester.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Semester with ID {request.semester_id} not found"
                )

            # Permission
            if current_user.user_type == UserType.guru:
                await self._validate_guru_teaches(
                    current_user.user_id, request.kelas_id, request.mapel_id
                )

            # Check duplicate
            existing = await self.db.execute(
                select(BobotPenilaian).where(
                    and_(
                        BobotPenilaian.mapel_id == request.mapel_id,
                        BobotPenilaian.kelas_id == request.kelas_id,
                        BobotPenilaian.semester_id == request.semester_id,
                        BobotPenilaian.jenis == request.jenis,
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Weight for {request.jenis.value} already exists in this context"
                )

            bobot = BobotPenilaian(
                mapel_id=request.mapel_id,
                kelas_id=request.kelas_id,
                semester_id=request.semester_id,
                jenis=request.jenis,
                bobot=request.bobot,
            )

            self.db.add(bobot)
            await self.db.commit()
            await self.db.refresh(bobot)

            return self._to_dto(bobot)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create bobot: {str(e)}"
            )

    async def list_bobot_by_context(
        self, mapel_id: UUID, kelas_id: UUID, semester_id: UUID
    ) -> list[BobotResponseDTO]:
        """
        List all weights for a mapel+kelas+semester context.

        Raises:
            HTTPException: 500 on database error
        """
        result = await self.db.execute(
            select(BobotPenilaian).where(
                and_(
                    BobotPenilaian.mapel_id == mapel_id,
                    BobotPenilaian.kelas_id == kelas_id,
                    BobotPenilaian.semester_id == semester_id,
                )
            )
        )
        return [self._to_dto(b) for b in result.scalars().all()]

    async def update_bobot(
        self, bobot_id: UUID, request: UpdateBobotDTO, current_user: User
    ) -> BobotResponseDTO:
        """
        Update a weight entry.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if no permission
            HTTPException: 400 if no fields to update
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(BobotPenilaian).where(BobotPenilaian.bobot_id == bobot_id)
            )
            bobot = result.scalar_one_or_none()
            if not bobot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bobot with ID {bobot_id} not found"
                )

            if current_user.user_type == UserType.guru:
                await self._validate_guru_teaches(
                    current_user.user_id, bobot.kelas_id, bobot.mapel_id
                )

            update_data = request.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )

            for field, value in update_data.items():
                setattr(bobot, field, value)

            await self.db.commit()
            await self.db.refresh(bobot)

            return self._to_dto(bobot)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update bobot: {str(e)}"
            )

    async def delete_bobot(
        self, bobot_id: UUID, current_user: User
    ) -> MessageResponseDTO:
        """
        Delete a weight entry.

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if no permission
            HTTPException: 500 on database error
        """
        try:
            result = await self.db.execute(
                select(BobotPenilaian).where(BobotPenilaian.bobot_id == bobot_id)
            )
            bobot = result.scalar_one_or_none()
            if not bobot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bobot with ID {bobot_id} not found"
                )

            if current_user.user_type == UserType.guru:
                await self._validate_guru_teaches(
                    current_user.user_id, bobot.kelas_id, bobot.mapel_id
                )

            await self.db.delete(bobot)
            await self.db.commit()

            return MessageResponseDTO(message="Bobot deleted successfully")

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete bobot: {str(e)}"
            )
