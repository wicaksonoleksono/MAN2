export type JenisKelamin = "Laki-Laki" | "Perempuan";
export type StatusSiswa = "Aktif" | "Non-Aktif" | "Lulus";
export type StatusGuru = "Aktif" | "Non-Aktif";
export type StructuralRole =
  | "Kepala Sekolah"
  | "Wakasek"
  | "Guru"
  | "Wali Kelas"
  | "Guru BK / Konselor"
  | "Kepala Tata Usaha"
  | "Staf Tata Usaha"
  | "Pustakawan"
  | "Laboran"
  | "Petugas UKS";

  
export type BidangWakasek =
  | "Kurikulum"
  | "Kesiswaan"
  | "Sarana dan Prasarana"
  | "Humas";

// ── Student ───────────────────────────────────────────────────────────────────

export interface StudentProfile {
  siswa_id: string;
  nis: string;
  nama_lengkap: string;
  dob: string;
  tempat_lahir: string;
  jenis_kelamin: JenisKelamin;
  alamat: string;
  nama_wali: string;
  nik: string;
  kelas_jurusan: string;
  tahun_masuk: number;
  status_siswa: StatusSiswa;
  kontak: string;
  kewarganegaraan: string;
}

export interface CreateStudentRequest {
  nis: string;
  nama_lengkap: string;
  dob: string;
  tempat_lahir: string;
  jenis_kelamin: JenisKelamin;
  alamat: string;
  nama_wali: string;
  nik: string;
  kelas_jurusan: string;
  tahun_masuk: number;
  kontak: string;
  kewarganegaraan?: string;
}

export interface CreateStudentResponse {
  message: string;
  username: string;
  generated_password: string;
  profile: StudentProfile;
}

export interface UpdateStudentRequest {
  nis?: string;
  nama_lengkap?: string;
  dob?: string;
  tempat_lahir?: string;
  jenis_kelamin?: JenisKelamin;
  alamat?: string;
  nama_wali?: string;
  nik?: string;
  kelas_jurusan?: string;
  tahun_masuk?: number;
  status_siswa?: StatusSiswa;
  kontak?: string;
  kewarganegaraan?: string;
}

// ── Teacher ───────────────────────────────────────────────────────────────────

export interface GuruProfile {
  guru_id: string;
  nip: string;
  nama_lengkap: string;
  dob: string;
  tempat_lahir: string;
  jenis_kelamin: JenisKelamin;
  alamat: string;
  nik: string;
  tahun_masuk: number;
  status_guru: StatusGuru;
  kontak: string;
  kewarganegaraan: string;
  structural_role: StructuralRole;
  bidang_wakasek: BidangWakasek | null;
  mata_pelajaran: string | null;
  pendidikan_terakhir: string | null;
}

export interface CreateGuruRequest {
  nip: string;
  nama_lengkap: string;
  dob: string;
  tempat_lahir: string;
  jenis_kelamin: JenisKelamin;
  alamat: string;
  nik: string;
  tahun_masuk: number;
  kontak: string;
  kewarganegaraan?: string;
  structural_role?: StructuralRole;
  bidang_wakasek?: BidangWakasek | null;
  mata_pelajaran?: string | null;
  pendidikan_terakhir?: string | null;
}

export interface CreateGuruResponse {
  message: string;
  username: string;
  generated_password: string;
  profile: GuruProfile;
}

export interface UpdateGuruRequest {
  nip?: string;
  nama_lengkap?: string;
  dob?: string;
  tempat_lahir?: string;
  jenis_kelamin?: JenisKelamin;
  alamat?: string;
  nik?: string;
  tahun_masuk?: number;
  status_guru?: StatusGuru;
  kontak?: string;
  kewarganegaraan?: string;
  structural_role?: StructuralRole;
  bidang_wakasek?: BidangWakasek | null;
  mata_pelajaran?: string | null;
  pendidikan_terakhir?: string | null;
}

export interface MessageResponse {
  message: string;
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PaginatedStudentsResponse {
  items: StudentProfile[];
  total: number;
  skip: number;
  limit: number;
}

export interface ListStudentsParams {
  skip: number;
  limit: number;
}
