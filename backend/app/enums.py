from enum import Enum


class UserType(Enum):
    siswa = "Siswa"
    guru = "Guru"
    admin = "Admin"


class StatusSiswa(Enum):
    aktif = "Aktif"
    nonaktif = "Non-Aktif"
    lulus = "Lulus"


class StatusGuru(Enum):
    aktif = "Aktif"
    nonaktif = "Non-Aktif"


class JenisKelamin(Enum):
    laki_laki = "Laki-Laki"
    perempuan = "Perempuan"


class StructuralRole(Enum):
    kepala_sekolah = "Kepala Sekolah"
    wakasek = "Wakasek"
    guru = "Guru"
    wali_kelas = "Wali Kelas"
    guru_bk = "Guru BK / Konselor"
    kepala_tata_usaha = "Kepala Tata Usaha"
    staf_tata_usaha = "Staf Tata Usaha"
    pustakawan = "Pustakawan"
    laboran = "Laboran"
    petugas_uks = "Petugas UKS"


class BidangWakasek(Enum):
    kurikulum = "Kurikulum"
    kesiswaan = "Kesiswaan"
    sarana_prasarana = "Sarana dan Prasarana"
    humas = "Humas"


class StatusAbsensi(Enum):
    hadir = "Hadir"
    terlambat = "Terlambat"
    alfa = "Alfa"
    sakit = "Sakit"
    izin = "Izin"
