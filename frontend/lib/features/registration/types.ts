import type { JenisKelamin } from "../users/enums";

export interface PendingStudentDTO {
  siswa_id: string;
  nama_lengkap: string;
  kelas_jurusan: string;
  jenis_kelamin: JenisKelamin;
}

export interface PendingTeacherDTO {
  guru_id: string;
  nama_lengkap: string;
  jenis_kelamin: JenisKelamin;
}

export interface PendingStudentSearchResponse {
  items: PendingStudentDTO[];
  total: number;
}

export interface PendingTeacherSearchResponse {
  items: PendingTeacherDTO[];
  total: number;
}

export interface ClaimStudentRequest {
  siswa_id: string;
  username: string;
  password: string;
  nis: string;
  dob: string;
  tempat_lahir: string;
  alamat: string;
  nama_wali: string;
  nik: string;
  tahun_masuk: number;
}

export interface ClaimTeacherRequest {
  guru_id: string;
  username: string;
  password: string;
  nip: string;
  dob: string;
  tempat_lahir: string;
  alamat: string;
  nik: string;
  tahun_masuk: number;
  kontak?: string;
  mata_pelajaran?: string;
  pendidikan_terakhir?: string;
}

export interface ClaimResponse {
  message: string;
  username: string;
  user_type: string;
}
