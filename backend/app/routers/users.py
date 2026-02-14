from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import require_role
from app.enums import UserType
from app.services.userMan_service import UserManagementService
from app.dto.userMan.userman_request import (
    CreateStudentRequestDTO, UpdateStudentRequestDTO,
    CreateGuruRequestDTO, UpdateGuruRequestDTO,
)
from app.dto.userMan.userman_response import (
    CreateStudentResponseDTO, StudentProfileResponseDTO,
    CreateGuruResponseDTO, GuruProfileResponseDTO,
    PaginatedStudentsResponse, PaginatedTeachersResponse, MessageResponseDTO,
)
from app.services.registration_service import RegistrationService
from app.dto.registration.registration_dto import (
    PreRegisterStudentDTO, PreRegisterTeacherDTO, PreRegisterResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/users",
    tags=["User Management"]
)


# ── Student Endpoints ────────────────────────────────────────────────────────


@router.post(
    "/students",
    response_model=CreateStudentResponseDTO,
    status_code=201,
    summary="Create Student",
    description="Create a new student account (Admin only). Username and password are auto-generated.",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def create_student(
    request: CreateStudentRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> CreateStudentResponseDTO:
    service = UserManagementService(db)
    return await service.create_student(request)


@router.get(
    "/students",
    response_model=PaginatedStudentsResponse,
    summary="List Students",
    description="List student profiles with pagination (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_students(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=30, ge=1, le=100, description="Max records to return (1-100)"),
    search: Optional[str] = Query(default=None, description="Search across nis, nama, nik, kelas, kontak, tempat_lahir"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedStudentsResponse:
    service = UserManagementService(db)
    return await service.list_students(skip=skip, limit=limit, search=search)


@router.get(
    "/students/{siswa_id}",
    response_model=StudentProfileResponseDTO,
    summary="Get Student",
    description="Get a student profile by ID (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def get_student(
    siswa_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponseDTO:
    service = UserManagementService(db)
    return await service.get_student(siswa_id)


@router.patch(
    "/students/{siswa_id}",
    response_model=StudentProfileResponseDTO,
    summary="Update Student",
    description="Partial update a student profile (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def update_student(
    siswa_id: UUID,
    request: UpdateStudentRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponseDTO:
    service = UserManagementService(db)
    return await service.update_student(siswa_id, request)


@router.delete(
    "/students/{siswa_id}",
    response_model=MessageResponseDTO,
    summary="Delete Student",
    description="Delete a student and their user account (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def delete_student(
    siswa_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MessageResponseDTO:
    service = UserManagementService(db)
    return await service.delete_student(siswa_id)


# ── Teacher Endpoints ────────────────────────────────────────────────────────


@router.post(
    "/teachers",
    response_model=CreateGuruResponseDTO,
    status_code=201,
    summary="Create Teacher",
    description="Create a new teacher account (Admin only). Username and password are auto-generated.",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def create_teacher(
    request: CreateGuruRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> CreateGuruResponseDTO:
    service = UserManagementService(db)
    return await service.create_guru(request)


@router.get(
    "/teachers",
    response_model=PaginatedTeachersResponse,
    summary="List Teachers",
    description="List teacher profiles with pagination and search (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_teachers(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=30, ge=1, le=100, description="Max records to return (1-100)"),
    search: Optional[str] = Query(default=None, description="Search across nip, nama, nik, kontak, mapel, tempat_lahir"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedTeachersResponse:
    service = UserManagementService(db)
    return await service.list_gurus(skip=skip, limit=limit, search=search)


@router.get(
    "/teachers/{guru_id}",
    response_model=GuruProfileResponseDTO,
    summary="Get Teacher",
    description="Get a teacher profile by ID (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def get_teacher(
    guru_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> GuruProfileResponseDTO:
    service = UserManagementService(db)
    return await service.get_guru(guru_id)


@router.patch(
    "/teachers/{guru_id}",
    response_model=GuruProfileResponseDTO,
    summary="Update Teacher",
    description="Partial update a teacher profile (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def update_teacher(
    guru_id: UUID,
    request: UpdateGuruRequestDTO,
    db: AsyncSession = Depends(get_db),
) -> GuruProfileResponseDTO:
    service = UserManagementService(db)
    return await service.update_guru(guru_id, request)


@router.delete(
    "/teachers/{guru_id}",
    response_model=MessageResponseDTO,
    summary="Delete Teacher",
    description="Delete a teacher and their user account (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def delete_teacher(
    guru_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MessageResponseDTO:
    service = UserManagementService(db)
    return await service.delete_guru(guru_id)


# ── Pre-Register Endpoints ──────────────────────────────────────────────────


@router.post(
    "/students/pre-register",
    response_model=PreRegisterResponseDTO,
    status_code=201,
    summary="Pre-Register Student",
    description="Create a PENDING student entry (Admin only). Student completes registration via /register.",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def pre_register_student(
    request: PreRegisterStudentDTO,
    db: AsyncSession = Depends(get_db),
) -> PreRegisterResponseDTO:
    service = RegistrationService(db)
    return await service.pre_register_student(request)


@router.post(
    "/teachers/pre-register",
    response_model=PreRegisterResponseDTO,
    status_code=201,
    summary="Pre-Register Teacher",
    description="Create a PENDING teacher entry (Admin only). Teacher completes registration via /register.",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def pre_register_teacher(
    request: PreRegisterTeacherDTO,
    db: AsyncSession = Depends(get_db),
) -> PreRegisterResponseDTO:
    service = RegistrationService(db)
    return await service.pre_register_teacher(request)
