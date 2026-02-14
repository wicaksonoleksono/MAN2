import type {
  JenisKelamin,
  StatusGuru,
  StructuralRole,
  BidangWakasek,
} from "../enums";

export interface GuruProfile {
  guru_id: string;
  nip: string | null;
  nama_lengkap: string;
  dob: string | null;
  tempat_lahir: string | null;
  jenis_kelamin: JenisKelamin | null;
  alamat: string | null;
  nik: string | null;
  tahun_masuk: number | null;
  status_guru: StatusGuru;
  kontak: string | null;
  kewarganegaraan: string;
  structural_role: StructuralRole;
  bidang_wakasek: BidangWakasek | null;
  mata_pelajaran: string | null;
  pendidikan_terakhir: string | null;
}

export interface PreRegisterTeacherRequest {
  nip: string;
  nama_lengkap: string;
  dob?: string;
  tempat_lahir?: string;
  jenis_kelamin?: JenisKelamin;
  alamat?: string;
  nik?: string;
  tahun_masuk?: number;
  kontak?: string;
  kewarganegaraan?: string;
  structural_role?: StructuralRole;
  bidang_wakasek?: BidangWakasek | null;
  mata_pelajaran?: string | null;
  pendidikan_terakhir?: string | null;
}

export interface PreRegisterResponse {
  message: string;
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

export interface PaginatedTeachersResponse {
  items: GuruProfile[];
  total: number;
  skip: number;
  limit: number;
}

export interface ListTeachersParams {
  skip: number;
  limit: number;
  search?: string;
}

export interface MessageResponse {
  message: string;
}
