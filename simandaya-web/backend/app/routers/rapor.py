from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import require_role
from app.enums import UserType
from app.models.user import User
from app.services.rapor_service import RaporService
from app.dto.rapor.rapor_dto import (
    GenerateRaporDTO, UpdateRaporDTO, OverrideNilaiDTO,
    RaporResponseDTO, RaporNilaiResponseDTO, RaporListItemDTO,
    GenerateRaporResponseDTO, MessageResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/rapor",
    tags=["Rapor"]
)


# ── Rapor Management ────────────────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=GenerateRaporResponseDTO,
    status_code=201,
    summary="Generate Rapor for Class",
)
async def generate_rapor(
    request: GenerateRaporDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> GenerateRaporResponseDTO:
    service = RaporService(db)
    return await service.generate_rapor(request, current_user)


@router.get(
    "/kelas/{kelas_id}",
    response_model=list[RaporListItemDTO],
    summary="List Rapor by Class",
)
async def list_rapor_by_kelas(
    kelas_id: UUID,
    semester_id: UUID = Query(...),
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> list[RaporListItemDTO]:
    service = RaporService(db)
    return await service.list_rapor_by_kelas(kelas_id, semester_id, current_user)


@router.get(
    "/my-rapor",
    response_model=RaporResponseDTO,
    summary="Get My Rapor (Student)",
)
async def get_my_rapor(
    semester_id: UUID = Query(...),
    current_user: User = Depends(require_role(UserType.siswa)),
    db: AsyncSession = Depends(get_db),
) -> RaporResponseDTO:
    service = RaporService(db)
    return await service.get_my_rapor(semester_id, current_user)


@router.get(
    "/{rapor_id}",
    response_model=RaporResponseDTO,
    summary="Get Full Rapor",
)
async def get_rapor(
    rapor_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> RaporResponseDTO:
    service = RaporService(db)
    return await service.get_rapor(rapor_id, current_user)


@router.patch(
    "/{rapor_id}",
    response_model=RaporResponseDTO,
    summary="Update Rapor Notes",
)
async def update_rapor(
    rapor_id: UUID,
    request: UpdateRaporDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> RaporResponseDTO:
    service = RaporService(db)
    return await service.update_rapor(rapor_id, request, current_user)


@router.post(
    "/{rapor_id}/publish",
    response_model=RaporResponseDTO,
    summary="Publish Single Rapor",
)
async def publish_rapor(
    rapor_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> RaporResponseDTO:
    service = RaporService(db)
    return await service.publish_rapor(rapor_id, current_user)


@router.post(
    "/kelas/{kelas_id}/publish-all",
    response_model=MessageResponseDTO,
    summary="Publish All Rapor for Class",
)
async def publish_all(
    kelas_id: UUID,
    semester_id: UUID = Query(...),
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseDTO:
    service = RaporService(db)
    return await service.publish_all(kelas_id, semester_id, current_user)


# ── Rapor Nilai (Grade Override) ────────────────────────────────────────────


@router.patch(
    "/rapor-nilai/{rapor_nilai_id}",
    response_model=RaporNilaiResponseDTO,
    summary="Override Grade Manually",
)
async def override_nilai(
    rapor_nilai_id: UUID,
    request: OverrideNilaiDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> RaporNilaiResponseDTO:
    service = RaporService(db)
    return await service.override_nilai(rapor_nilai_id, request, current_user)


@router.post(
    "/{rapor_id}/recalculate",
    response_model=RaporResponseDTO,
    summary="Recalculate Grades from Raw Data",
)
async def recalculate_rapor(
    rapor_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> RaporResponseDTO:
    service = RaporService(db)
    return await service.recalculate_rapor(rapor_id, current_user)
