from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID
from app.enums import JenisKalender


class CreateKalenderDTO(BaseModel):
    tahun_ajaran_id: UUID = Field(...)
    tanggal: date = Field(...)
    jenis: JenisKalender = Field(...)
    keterangan: str = Field(..., min_length=1, max_length=255)


class UpdateKalenderDTO(BaseModel):
    tanggal: Optional[date] = None
    jenis: Optional[JenisKalender] = None
    keterangan: Optional[str] = Field(default=None, max_length=255)


class KalenderResponseDTO(BaseModel):
    kalender_id: UUID
    tahun_ajaran_id: UUID
    tanggal: date
    jenis: JenisKalender
    keterangan: str
