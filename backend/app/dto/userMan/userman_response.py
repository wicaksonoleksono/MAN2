from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from app.enums import StatusSiswa, StatusGuru, JenisKelamin, StructuralRole, BidangWakasek


class StudentProfileResponseDTO(BaseModel):
    siswa_id: UUID
    nis: Optional[str] = None
    nama_lengkap: str
    dob: Optional[str] = None
    tempat_lahir: Optional[str] = None
    jenis_kelamin: JenisKelamin
    alamat: Optional[str] = None
    nama_wali: Optional[str] = None
    nik: Optional[str] = None
    kelas_jurusan: str
    tahun_masuk: Optional[int] = None
    status_siswa: StatusSiswa
    kontak: str
    kewarganegaraan: str


class CreateStudentResponseDTO(BaseModel):
    message: str
    username: str
    generated_password: str
    profile: StudentProfileResponseDTO


class GuruProfileResponseDTO(BaseModel):
    guru_id: UUID
    nip: Optional[str] = None
    nama_lengkap: str
    dob: Optional[str] = None
    tempat_lahir: Optional[str] = None
    jenis_kelamin: JenisKelamin
    alamat: Optional[str] = None
    nik: Optional[str] = None
    tahun_masuk: Optional[int] = None
    status_guru: StatusGuru
    kontak: Optional[str] = None
    kewarganegaraan: str
    structural_role: StructuralRole
    bidang_wakasek: Optional[BidangWakasek]
    mata_pelajaran: Optional[str]
    pendidikan_terakhir: Optional[str]


class CreateGuruResponseDTO(BaseModel):
    message: str
    username: str
    generated_password: str
    profile: GuruProfileResponseDTO


class PaginatedStudentsResponse(BaseModel):
    items: list[StudentProfileResponseDTO]
    total: int
    skip: int
    limit: int


class PaginatedTeachersResponse(BaseModel):
    items: list[GuruProfileResponseDTO]
    total: int
    skip: int
    limit: int


class MessageResponseDTO(BaseModel):
    message: str
