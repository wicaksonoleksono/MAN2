from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.enums import JenisKelamin, StatusSiswa, StatusGuru, StructuralRole, BidangWakasek


# ── Student ──────────────────────────────────────────────────────────────────


class UpdateStudentRequestDTO(BaseModel):
    """Request DTO for partial update of a student profile (Admin only)"""

    nis: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nama_lengkap: Optional[str] = Field(default=None, min_length=2, max_length=225)
    dob: Optional[str] = Field(default=None, min_length=1, max_length=50)
    tempat_lahir: Optional[str] = Field(default=None, max_length=100)
    jenis_kelamin: Optional[JenisKelamin] = None
    alamat: Optional[str] = Field(default=None, max_length=500)
    nama_wali: Optional[str] = Field(default=None, min_length=2, max_length=225)
    nik: Optional[str] = Field(default=None, max_length=20)
    kelas_jurusan: Optional[str] = Field(default=None, max_length=100)
    tahun_masuk: Optional[int] = Field(default=None, ge=2000, le=2100)
    status_siswa: Optional[StatusSiswa] = None
    kontak: Optional[str] = Field(default=None, max_length=100)
    kewarganegaraan: Optional[str] = Field(default=None, max_length=50)


# ── Guru ─────────────────────────────────────────────────────────────────────


class UpdateGuruRequestDTO(BaseModel):
    """Request DTO for partial update of a teacher profile (Admin only)"""

    nip: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nama_lengkap: Optional[str] = Field(default=None, min_length=2, max_length=225)
    dob: Optional[str] = Field(default=None, min_length=1, max_length=50)
    tempat_lahir: Optional[str] = Field(default=None, max_length=100)
    jenis_kelamin: Optional[JenisKelamin] = None
    alamat: Optional[str] = Field(default=None, max_length=500)
    nik: Optional[str] = Field(default=None, max_length=20)
    tahun_masuk: Optional[int] = Field(default=None, ge=2000, le=2100)
    status_guru: Optional[StatusGuru] = None
    kontak: Optional[str] = Field(default=None, max_length=100)
    kewarganegaraan: Optional[str] = Field(default=None, max_length=50)
    structural_role: Optional[StructuralRole] = None
    bidang_wakasek: Optional[BidangWakasek] = None
    mata_pelajaran: Optional[str] = Field(default=None, max_length=100)
    pendidikan_terakhir: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_bidang_wakasek(self):
        if self.structural_role is not None and self.structural_role == StructuralRole.wakasek and self.bidang_wakasek is None:
            raise ValueError("bidang_wakasek is required when structural_role is Wakasek")
        if self.structural_role is not None and self.structural_role != StructuralRole.wakasek and self.bidang_wakasek is not None:
            raise ValueError("bidang_wakasek must be null when structural_role is not Wakasek")
        return self
