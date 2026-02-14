from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.services.registration_service import RegistrationService
from app.dto.registration.registration_dto import (
    PendingStudentSearchResponse, PendingTeacherSearchResponse,
    ClaimStudentRequestDTO, ClaimTeacherRequestDTO, ClaimResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/registration",
    tags=["Registration"]
)


@router.get(
    "/students/search",
    response_model=PendingStudentSearchResponse,
    summary="Search Pending Students",
    description="Search for pre-registered students by name (no auth required).",
)
async def search_pending_students(
    name: str = Query(..., min_length=2, description="Nama siswa (minimal 2 karakter)"),
    db: AsyncSession = Depends(get_db),
) -> PendingStudentSearchResponse:
    service = RegistrationService(db)
    return await service.search_pending_students(name)


@router.get(
    "/teachers/search",
    response_model=PendingTeacherSearchResponse,
    summary="Search Pending Teachers",
    description="Search for pre-registered teachers by name (no auth required).",
)
async def search_pending_teachers(
    name: str = Query(..., min_length=2, description="Nama guru (minimal 2 karakter)"),
    db: AsyncSession = Depends(get_db),
) -> PendingTeacherSearchResponse:
    service = RegistrationService(db)
    return await service.search_pending_teachers(name)


@router.post(
    "/students/claim",
    response_model=ClaimResponseDTO,
    summary="Claim Student Registration",
    description="Student claims a pre-registered entry and completes registration (no auth required).",
)
async def claim_student(
    request: ClaimStudentRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> ClaimResponseDTO:
    service = RegistrationService(db)
    return await service.claim_student(request)


@router.post(
    "/teachers/claim",
    response_model=ClaimResponseDTO,
    summary="Claim Teacher Registration",
    description="Teacher claims a pre-registered entry and completes registration (no auth required).",
)
async def claim_teacher(
    request: ClaimTeacherRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> ClaimResponseDTO:
    service = RegistrationService(db)
    return await service.claim_teacher(request)
