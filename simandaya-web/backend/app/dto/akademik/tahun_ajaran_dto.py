from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class CreateTahunAjaranDTO(BaseModel):
    nama: str = Field(..., min_length=1, max_length=20, description="e.g. 2025/2026")
    tanggal_mulai: date = Field(..., description="Start date")
    tanggal_selesai: date = Field(..., description="End date")
    is_active: bool = Field(default=False)


class UpdateTahunAjaranDTO(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=20)
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    is_active: Optional[bool] = None


class TahunAjaranResponseDTO(BaseModel):
    tahun_ajaran_id: UUID
    nama: str
    tanggal_mulai: date
    tanggal_selesai: date
    is_active: bool
