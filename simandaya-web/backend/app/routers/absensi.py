from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.dependencies import require_role
from app.enums import UserType
from app.models.user import User
from app.services.absensi_service import AbsensiService
from app.dto.absensi.absensi_response import (
    AbsensiResponseDTO,
    IzinKeluarResponseDTO,
)
from app.dto.absensi.public_response import (
    PublicAbsensiDTO,
    PublicIzinKeluarDTO,
)
from app.dto.absensi.bulk_absensi_dto import (
    BulkAbsensiCreateDTO,
    BulkAbsensiResponseDTO,
)

router = APIRouter(
    prefix="/api/v1/absensi",
    tags=["Absensi"]
)


# ── Attendance ───────────────────────────────────────────────────────────────


@router.get(
    "/attendance",
    response_model=list[AbsensiResponseDTO],
    summary="List All Attendance",
    description="List all attendance records (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_absensi(
    db: AsyncSession = Depends(get_db),
) -> list[AbsensiResponseDTO]:
    service = AbsensiService(db)
    return await service.list_absensi()


@router.get(
    "/attendance/student/{user_id}",
    response_model=list[AbsensiResponseDTO],
    summary="List Attendance by Student",
    description="List attendance records for a specific student (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_absensi_by_student(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[AbsensiResponseDTO]:
    service = AbsensiService(db)
    return await service.list_absensi_by_student(user_id)


@router.get(
    "/attendance/{absensi_id}",
    response_model=AbsensiResponseDTO,
    summary="Get Attendance Record",
    description="Get a single attendance record by ID (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def get_absensi(
    absensi_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AbsensiResponseDTO:
    service = AbsensiService(db)
    return await service.get_absensi(absensi_id)


@router.post(
    "/attendance/bulk",
    response_model=BulkAbsensiResponseDTO,
    summary="Bulk Mark Attendance",
    description="Mark attendance for an entire class at once (Guru/Admin).",
)
async def bulk_create_absensi(
    request: BulkAbsensiCreateDTO,
    current_user: User = Depends(require_role(UserType.guru, UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> BulkAbsensiResponseDTO:
    service = AbsensiService(db)
    return await service.bulk_create_absensi(request, current_user)


# ── Izin Keluar ──────────────────────────────────────────────────────────────


@router.get(
    "/izin-keluar",
    response_model=list[IzinKeluarResponseDTO],
    summary="List All Izin Keluar",
    description="List all izin keluar records (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_izin_keluar(
    db: AsyncSession = Depends(get_db),
) -> list[IzinKeluarResponseDTO]:
    service = AbsensiService(db)
    return await service.list_izin_keluar()


@router.get(
    "/izin-keluar/student/{user_id}",
    response_model=list[IzinKeluarResponseDTO],
    summary="List Izin Keluar by Student",
    description="List izin keluar records for a specific student (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def list_izin_keluar_by_student(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[IzinKeluarResponseDTO]:
    service = AbsensiService(db)
    return await service.list_izin_keluar_by_student(user_id)


@router.get(
    "/izin-keluar/{izin_id}",
    response_model=IzinKeluarResponseDTO,
    summary="Get Izin Keluar Record",
    description="Get a single izin keluar record by ID (Admin only).",
    dependencies=[Depends(require_role(UserType.admin))]
)
async def get_izin_keluar(
    izin_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> IzinKeluarResponseDTO:
    service = AbsensiService(db)
    return await service.get_izin_keluar(izin_id)


# ── Public (no auth) ────────────────────────────────────────────────────────


@router.get(
    "/public/attendance",
    response_model=list[PublicAbsensiDTO],
    summary="Public Attendance List",
    description="List attendance records with student names. No auth required.",
)
async def list_absensi_public(
    tanggal: date = Query(description="Filter date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by student name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[PublicAbsensiDTO]:
    service = AbsensiService(db)
    return await service.list_absensi_public(
        tanggal=tanggal, search=search, skip=skip, limit=limit
    )


@router.get(
    "/public/izin-keluar",
    response_model=list[PublicIzinKeluarDTO],
    summary="Public Izin Keluar List",
    description="List izin keluar records with student names. No auth required.",
)
async def list_izin_keluar_public(
    tanggal: date = Query(description="Filter date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by student name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[PublicIzinKeluarDTO]:
    service = AbsensiService(db)
    return await service.list_izin_keluar_public(
        tanggal=tanggal, search=search, skip=skip, limit=limit
    )
