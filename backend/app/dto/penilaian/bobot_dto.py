from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from app.enums import JenisTugas


class CreateBobotDTO(BaseModel):
    mapel_id: UUID = Field(...)
    kelas_id: UUID = Field(...)
    semester_id: UUID = Field(...)
    jenis: JenisTugas = Field(...)
    bobot: int = Field(..., ge=0, le=100, description="Weight percentage 0-100")


class UpdateBobotDTO(BaseModel):
    bobot: Optional[int] = Field(default=None, ge=0, le=100)


class BobotResponseDTO(BaseModel):
    bobot_id: UUID
    mapel_id: UUID
    kelas_id: UUID
    semester_id: UUID
    jenis: JenisTugas
    bobot: int


class MessageResponseDTO(BaseModel):
    message: str
