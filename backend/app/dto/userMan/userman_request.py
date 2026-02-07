from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.enums import JenisKelamin, StatusSiswa, StatusGuru, StructuralRole, BidangWakasek


# ── Student ──────────────────────────────────────────────────────────────────


class CreateStudentRequestDTO(BaseModel):
    """Request DTO for creating a student (Admin only)"""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nis": "012310230",
                    "nama_lengkap": "Ahmad Rizki",
                    "dob": "23/09/2001",
                    "tempat_lahir": "Jakarta",
                    "jenis_kelamin": "Laki-Laki",
                    "alamat": "Jl. Merdeka No. 10",
                    "nama_wali": "Budi Santoso",
                    "nik": "3201010101010001",
                    "kelas_jurusan": "XII IPA 1",
                    "tahun_masuk": 2022,
                    "kontak": "081234567890",
                    "kewarganegaraan": "Indonesia",
                }
            ]
        }
    }

    nis: str = Field(..., min_length=1, max_length=50, description="Nomor Induk Siswa")
    nama_lengkap: str = Field(..., min_length=2, max_length=225, description="Nama lengkap siswa")
    dob: str = Field(..., min_length=1, max_length=50, description="Tanggal lahir (DD/MM/YYYY)")
    tempat_lahir: str = Field(..., min_length=1, max_length=100, description="Tempat lahir")
    jenis_kelamin: JenisKelamin = Field(..., description="Jenis kelamin")
    alamat: str = Field(..., min_length=1, max_length=500, description="Alamat lengkap")
    nama_wali: str = Field(..., min_length=2, max_length=225, description="Nama orang tua / wali")
    nik: str = Field(..., min_length=1, max_length=20, description="NIK")
    kelas_jurusan: str = Field(..., min_length=1, max_length=100, description="Kelas / jurusan")
    tahun_masuk: int = Field(..., ge=2000, le=2100, description="Tahun masuk")
    kontak: str = Field(..., min_length=1, max_length=100, description="Nomor telepon atau email")
    kewarganegaraan: str = Field(default="Indonesia", max_length=50, description="Kewarganegaraan")


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


class CreateGuruRequestDTO(BaseModel):
    """Request DTO for creating a teacher (Admin only)"""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nip": "198501012010011001",
                    "nama_lengkap": "Siti Rahmawati",
                    "dob": "01/01/1985",
                    "tempat_lahir": "Bandung",
                    "jenis_kelamin": "Perempuan",
                    "alamat": "Jl. Pendidikan No. 5",
                    "nik": "3201010101010002",
                    "tahun_masuk": 2010,
                    "kontak": "081298765432",
                    "kewarganegaraan": "Indonesia",
                    "structural_role": "Guru",
                    "bidang_wakasek": None,
                    "mata_pelajaran": "Matematika",
                    "pendidikan_terakhir": "S1 Pendidikan Matematika",
                }
            ]
        }
    }

    nip: str = Field(..., min_length=1, max_length=50, description="Nomor Induk Pegawai")
    nama_lengkap: str = Field(..., min_length=2, max_length=225, description="Nama lengkap guru")
    dob: str = Field(..., min_length=1, max_length=50, description="Tanggal lahir (DD/MM/YYYY)")
    tempat_lahir: str = Field(..., min_length=1, max_length=100, description="Tempat lahir")
    jenis_kelamin: JenisKelamin = Field(..., description="Jenis kelamin")
    alamat: str = Field(..., min_length=1, max_length=500, description="Alamat lengkap")
    nik: str = Field(..., min_length=1, max_length=20, description="NIK")
    tahun_masuk: int = Field(..., ge=2000, le=2100, description="Tahun masuk")
    kontak: str = Field(..., min_length=1, max_length=100, description="Nomor telepon atau email")
    kewarganegaraan: str = Field(default="Indonesia", max_length=50, description="Kewarganegaraan")
    structural_role: StructuralRole = Field(default=StructuralRole.guru, description="Jabatan struktural")
    bidang_wakasek: Optional[BidangWakasek] = Field(default=None, description="Bidang wakasek (only if structural_role is Wakasek)")
    mata_pelajaran: Optional[str] = Field(default=None, max_length=100, description="Mata pelajaran yang diampu")
    pendidikan_terakhir: Optional[str] = Field(default=None, max_length=100, description="Pendidikan terakhir")

    @model_validator(mode="after")
    def validate_bidang_wakasek(self):
        if self.structural_role == StructuralRole.wakasek and self.bidang_wakasek is None:
            raise ValueError("bidang_wakasek is required when structural_role is Wakasek")
        if self.structural_role != StructuralRole.wakasek and self.bidang_wakasek is not None:
            raise ValueError("bidang_wakasek must be null when structural_role is not Wakasek")
        return self


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
