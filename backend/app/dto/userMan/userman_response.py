from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from app.enums import StatusSiswa, StatusGuru, JenisKelamin, StructuralRole, BidangWakasek


class StudentProfileResponseDTO(BaseModel):
    siswa_id: UUID
    nis: str
    nama_lengkap: str
    dob: str
    tempat_lahir: str
    jenis_kelamin: JenisKelamin
    alamat: str
    nama_wali: str
    nik: str
    kelas_jurusan: str
    tahun_masuk: int
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
    nip: str
    nama_lengkap: str
    dob: str
    tempat_lahir: str
    jenis_kelamin: JenisKelamin
    alamat: str
    nik: str
    tahun_masuk: int
    status_guru: StatusGuru
    kontak: str
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


class MessageResponseDTO(BaseModel):
    message: str
