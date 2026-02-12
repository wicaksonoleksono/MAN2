from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import require_role
from app.enums import UserType
from app.models.user import User
from app.services.bobot_service import BobotService
from app.dto.penilaian.bobot_dto import (
    CreateBobotDTO, UpdateBobotDTO, BobotResponseDTO, MessageResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/penilaian",
    tags=["Bobot Penilaian"]
)


@router.post(
    "/bobot",
    response_model=BobotResponseDTO,
    status_code=201,
    summary="Create Assessment Weight",
)
async def create_bobot(
    request: CreateBobotDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> BobotResponseDTO:
    service = BobotService(db)
    return await service.create_bobot(request, current_user)


@router.get(
    "/bobot/mapel/{mapel_id}/kelas/{kelas_id}",
    response_model=list[BobotResponseDTO],
    summary="Get Weights for Context",
)
async def list_bobot_by_context(
    mapel_id: UUID,
    kelas_id: UUID,
    semester_id: UUID = Query(...),
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> list[BobotResponseDTO]:
    service = BobotService(db)
    return await service.list_bobot_by_context(mapel_id, kelas_id, semester_id)


@router.patch(
    "/bobot/{bobot_id}",
    response_model=BobotResponseDTO,
    summary="Update Assessment Weight",
)
async def update_bobot(
    bobot_id: UUID,
    request: UpdateBobotDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> BobotResponseDTO:
    service = BobotService(db)
    return await service.update_bobot(bobot_id, request, current_user)


@router.delete(
    "/bobot/{bobot_id}",
    response_model=MessageResponseDTO,
    summary="Delete Assessment Weight",
)
async def delete_bobot(
    bobot_id: UUID,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseDTO:
    service = BobotService(db)
    return await service.delete_bobot(bobot_id, current_user)
