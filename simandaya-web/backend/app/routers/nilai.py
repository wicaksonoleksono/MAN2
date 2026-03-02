from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import require_role
from app.enums import UserType
from app.models.user import User
from app.services.nilai_service import NilaiService
from app.dto.penilaian.nilai_dto import (
    CreateNilaiDTO, BulkCreateNilaiDTO, UpdateNilaiDTO,
    NilaiResponseDTO, BulkNilaiResponseDTO, MessageResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/penilaian",
    tags=["Nilai"]
)


@router.post(
    "/tugas/{tugas_id}/nilai",
    response_model=NilaiResponseDTO,
    status_code=201,
    summary="Create Single Score",
)
async def create_nilai(
    tugas_id: UUID,
    request: CreateNilaiDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> NilaiResponseDTO:
    service = NilaiService(db)
    return await service.create_nilai(tugas_id, request, current_user)


@router.post(
    "/tugas/{tugas_id}/nilai/bulk",
    response_model=BulkNilaiResponseDTO,
    summary="Bulk Create/Update Scores",
)
async def bulk_create_nilai(
    tugas_id: UUID,
    request: BulkCreateNilaiDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> BulkNilaiResponseDTO:
    service = NilaiService(db)
    return await service.bulk_create_nilai(tugas_id, request, current_user)


@router.get(
    "/tugas/{tugas_id}/nilai",
    response_model=list[NilaiResponseDTO],
    summary="List Scores for Tugas",
)
async def list_nilai_by_tugas(
    tugas_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> list[NilaiResponseDTO]:
    service = NilaiService(db)
    return await service.list_nilai_by_tugas(tugas_id, current_user)


@router.get(
    "/nilai/my-scores",
    response_model=list[NilaiResponseDTO],
    summary="Get My Scores (Student)",
)
async def list_my_scores(
    semester_id: Optional[UUID] = Query(default=None),
    current_user: User = Depends(require_role(UserType.siswa)),
    db: AsyncSession = Depends(get_db),
) -> list[NilaiResponseDTO]:
    service = NilaiService(db)
    return await service.list_my_scores(current_user, semester_id)


@router.patch(
    "/nilai/{nilai_id}",
    response_model=NilaiResponseDTO,
    summary="Update Score",
)
async def update_nilai(
    nilai_id: UUID,
    request: UpdateNilaiDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> NilaiResponseDTO:
    service = NilaiService(db)
    return await service.update_nilai(nilai_id, request, current_user)


@router.delete(
    "/nilai/{nilai_id}",
    response_model=MessageResponseDTO,
    summary="Delete Score",
)
async def delete_nilai(
    nilai_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseDTO:
    service = NilaiService(db)
    return await service.delete_nilai(nilai_id, current_user)
