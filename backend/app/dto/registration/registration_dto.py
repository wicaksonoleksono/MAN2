from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.enums import JenisKelamin


# ── Search responses (public, no auth) ──────────────────────────────────────


class PendingStudentDTO(BaseModel):
    siswa_id: UUID
    nama_lengkap: str
    kelas_jurusan: str
    jenis_kelamin: JenisKelamin

    model_config = {"from_attributes": True}


class PendingTeacherDTO(BaseModel):
    guru_id: UUID
    nama_lengkap: str
    jenis_kelamin: JenisKelamin

    model_config = {"from_attributes": True}


class PendingStudentSearchResponse(BaseModel):
    items: list[PendingStudentDTO]
    total: int


class PendingTeacherSearchResponse(BaseModel):
    items: list[PendingTeacherDTO]
    total: int


# ── Claim requests ──────────────────────────────────────────────────────────


class ClaimStudentRequestDTO(BaseModel):
    siswa_id: UUID = Field(..., description="ID profil siswa yang diklaim")
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    nis: str = Field(..., min_length=1, max_length=50)
    dob: str = Field(..., min_length=1, max_length=50)
    tempat_lahir: str = Field(..., min_length=1, max_length=100)
    alamat: str = Field(..., min_length=1, max_length=500)
    nama_wali: str = Field(..., min_length=2, max_length=225)
    nik: str = Field(..., min_length=1, max_length=20)
    tahun_masuk: int = Field(..., ge=2000, le=2100)


class ClaimTeacherRequestDTO(BaseModel):
    guru_id: UUID = Field(..., description="ID profil guru yang diklaim")
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    nip: str = Field(..., min_length=1, max_length=50)
    dob: str = Field(..., min_length=1, max_length=50)
    tempat_lahir: str = Field(..., min_length=1, max_length=100)
    alamat: str = Field(..., min_length=1, max_length=500)
    nik: str = Field(..., min_length=1, max_length=20)
    tahun_masuk: int = Field(..., ge=2000, le=2100)
    kontak: Optional[str] = Field(default=None, max_length=100)
    mata_pelajaran: Optional[str] = Field(default=None, max_length=100)
    pendidikan_terakhir: Optional[str] = Field(default=None, max_length=100)


class ClaimResponseDTO(BaseModel):
    message: str
    username: str
    user_type: str


# ── Admin pre-register requests ─────────────────────────────────────────────


class PreRegisterStudentDTO(BaseModel):
    nama_lengkap: str = Field(..., min_length=2, max_length=225)
    jenis_kelamin: JenisKelamin
    kelas_jurusan: str = Field(..., min_length=1, max_length=100)
    kontak: Optional[str] = Field(default=None, max_length=100)


class PreRegisterTeacherDTO(BaseModel):
    nama_lengkap: str = Field(..., min_length=2, max_length=225)
    jenis_kelamin: JenisKelamin
    kontak: Optional[str] = Field(default=None, max_length=100)


class PreRegisterResponseDTO(BaseModel):
    message: str
