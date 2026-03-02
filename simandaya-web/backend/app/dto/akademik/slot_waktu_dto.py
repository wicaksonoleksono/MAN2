from typing import Optional
from datetime import time
from pydantic import BaseModel, Field
from uuid import UUID


class CreateSlotWaktuDTO(BaseModel):
    nama: str = Field(..., min_length=1, max_length=50, description="e.g. Jam 1")
    jam_mulai: time = Field(...)
    jam_selesai: time = Field(...)
    urutan: int = Field(..., ge=1)
    is_piket: bool = Field(default=False, description="True for non-lesson slots like doa, istirahat")


class UpdateSlotWaktuDTO(BaseModel):
    nama: Optional[str] = Field(default=None, max_length=50)
    jam_mulai: Optional[time] = None
    jam_selesai: Optional[time] = None
    urutan: Optional[int] = Field(default=None, ge=1)
    is_piket: Optional[bool] = None


class SlotWaktuResponseDTO(BaseModel):
    slot_id: UUID
    nama: str
    jam_mulai: time
    jam_selesai: time
    urutan: int
    is_piket: bool
