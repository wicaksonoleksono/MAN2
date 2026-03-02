"""
Seed admin, student, and teacher accounts into the database.

Usage (from host, with Docker running):
    docker exec simandaya-backend python scripts/seed_admins.py

Creates:
  - 1 admin (completed)
  - 10 students (PENDING, pre-registered with NIS + nama)
  - 10 teachers (PENDING, pre-registered with NIP + nama + structural roles)
Skips any that already exist.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.config.database import engine, async_session_maker
from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.guru_profile import GuruProfile
from app.enums import (
    UserType, RegistrationStatus,
    StatusSiswa, StatusGuru,
    JenisKelamin, StructuralRole, BidangWakasek,
)


ADMINS = [
    {"username": "admin", "password": "1qaz2wsx3edc"},
]

STUDENTS = [
    {"nis": "24001", "nama_lengkap": "Ahmad Fauzan", "jenis_kelamin": JenisKelamin.laki_laki, "kelas_jurusan": "X IPA 1"},
    {"nis": "24002", "nama_lengkap": "Siti Aisyah", "jenis_kelamin": JenisKelamin.perempuan, "kelas_jurusan": "X IPA 2"},
    {"nis": "24003", "nama_lengkap": "Muhammad Rizky", "jenis_kelamin": JenisKelamin.laki_laki, "kelas_jurusan": "X IPS 1"},
    {"nis": "24004", "nama_lengkap": "Nur Halimah", "jenis_kelamin": JenisKelamin.perempuan, "kelas_jurusan": "XI IPA 1"},
    {"nis": "24005", "nama_lengkap": "Dimas Prasetyo", "jenis_kelamin": JenisKelamin.laki_laki, "kelas_jurusan": "XI IPA 2"},
    {"nis": "24006", "nama_lengkap": "Fatimah Zahra", "jenis_kelamin": JenisKelamin.perempuan, "kelas_jurusan": "XI IPS 1"},
    {"nis": "24007", "nama_lengkap": "Ilham Maulana", "jenis_kelamin": JenisKelamin.laki_laki, "kelas_jurusan": "XII IPA 1"},
    {"nis": "24008", "nama_lengkap": "Rina Safitri", "jenis_kelamin": JenisKelamin.perempuan, "kelas_jurusan": "XII IPA 2"},
    {"nis": "24009", "nama_lengkap": "Bayu Aditya", "jenis_kelamin": JenisKelamin.laki_laki, "kelas_jurusan": "XII IPS 1"},
    {"nis": "24010", "nama_lengkap": "Dewi Lestari", "jenis_kelamin": JenisKelamin.perempuan, "kelas_jurusan": "XII Keagamaan"},
]

TEACHERS = [
    {
        "nip": "196705151993031002",
        "nama_lengkap": "Singgih Sampurno, S.Pd., M.A.",
        "jenis_kelamin": JenisKelamin.laki_laki,
        "structural_role": StructuralRole.kepala_sekolah,
        "mata_pelajaran": "Bahasa Inggris",
        "pendidikan_terakhir": "S2",
    },
    {
        "nip": "197201081998032001",
        "nama_lengkap": "Isti Wahyuni, S.E., M.M",
        "jenis_kelamin": JenisKelamin.perempuan,
        "structural_role": StructuralRole.kepala_tata_usaha,
        "pendidikan_terakhir": "S2",
    },
    {
        "nip": "197308202000031001",
        "nama_lengkap": "Fajar Basuki Rahmat, S.Ag",
        "jenis_kelamin": JenisKelamin.laki_laki,
        "structural_role": StructuralRole.wakasek,
        "bidang_wakasek": BidangWakasek.kurikulum,
        "mata_pelajaran": "Pendidikan Agama Islam",
        "pendidikan_terakhir": "S1",
    },
    {
        "nip": "198005152005012001",
        "nama_lengkap": "Leni, S.Si., M.Pd",
        "jenis_kelamin": JenisKelamin.perempuan,
        "structural_role": StructuralRole.wakasek,
        "bidang_wakasek": BidangWakasek.kesiswaan,
        "mata_pelajaran": "Matematika",
        "pendidikan_terakhir": "S2",
    },
    {
        "nip": "198112302006041001",
        "nama_lengkap": "Afwan Suhaimi DR, S.Pd",
        "jenis_kelamin": JenisKelamin.laki_laki,
        "structural_role": StructuralRole.wakasek,
        "bidang_wakasek": BidangWakasek.sarana_prasarana,
        "mata_pelajaran": "Fisika",
        "pendidikan_terakhir": "S1",
    },
    {
        "nip": "197609152003122001",
        "nama_lengkap": "Rita Setyowati, S.Pd., M.Pd",
        "jenis_kelamin": JenisKelamin.perempuan,
        "structural_role": StructuralRole.wakasek,
        "bidang_wakasek": BidangWakasek.humas,
        "mata_pelajaran": "Bahasa Indonesia",
        "pendidikan_terakhir": "S2",
    },
    {
        "nip": "198503172010011001",
        "nama_lengkap": "Hendra Kurniawan, S.Pd",
        "jenis_kelamin": JenisKelamin.laki_laki,
        "structural_role": StructuralRole.wali_kelas,
        "mata_pelajaran": "Biologi",
        "pendidikan_terakhir": "S1",
    },
    {
        "nip": "198711252012012001",
        "nama_lengkap": "Sari Rahmawati, S.Pd",
        "jenis_kelamin": JenisKelamin.perempuan,
        "structural_role": StructuralRole.guru_bk,
        "mata_pelajaran": "Bimbingan Konseling",
        "pendidikan_terakhir": "S1",
    },
    {
        "nip": "199002082015031001",
        "nama_lengkap": "Eko Prasetyo, S.Kom",
        "jenis_kelamin": JenisKelamin.laki_laki,
        "structural_role": StructuralRole.laboran,
        "mata_pelajaran": "Informatika",
        "pendidikan_terakhir": "S1",
    },
    {
        "nip": "199205152018012001",
        "nama_lengkap": "Anisa Putri, S.Pd",
        "jenis_kelamin": JenisKelamin.perempuan,
        "structural_role": StructuralRole.guru,
        "mata_pelajaran": "Kimia",
        "pendidikan_terakhir": "S1",
    },
]


async def seed():
    async with async_session_maker() as session:
        # ── Admins ─────────────────────────────────────────────────────────
        for admin in ADMINS:
            result = await session.execute(
                select(User).where(User.username == admin["username"])
            )
            if result.scalar_one_or_none():
                print(f"  SKIP admin (exists): {admin['username']}")
                continue

            user = User(
                username=admin["username"],
                user_type=UserType.admin,
                registration_status=RegistrationStatus.completed,
                is_active=True,
            )
            user.set_password(admin["password"])
            session.add(user)
            print(f"  CREATED admin: {admin['username']}")

        # ── Students (PENDING) ─────────────────────────────────────────────
        for s in STUDENTS:
            result = await session.execute(
                select(SiswaProfile).where(SiswaProfile.nis == s["nis"])
            )
            if result.scalar_one_or_none():
                print(f"  SKIP student (NIS exists): {s['nis']} - {s['nama_lengkap']}")
                continue

            user = User(
                user_type=UserType.siswa,
                registration_status=RegistrationStatus.pending,
                username=None,
                password_hash=None,
                is_active=False,
            )
            session.add(user)
            await session.flush()

            profile = SiswaProfile(
                user_id=user.user_id,
                nis=s["nis"],
                nama_lengkap=s["nama_lengkap"],
                jenis_kelamin=s.get("jenis_kelamin"),
                kelas_jurusan=s.get("kelas_jurusan"),
                status_siswa=StatusSiswa.aktif,
            )
            session.add(profile)
            print(f"  CREATED student: {s['nis']} - {s['nama_lengkap']}")

        # ── Teachers (PENDING) ─────────────────────────────────────────────
        for t in TEACHERS:
            result = await session.execute(
                select(GuruProfile).where(GuruProfile.nip == t["nip"])
            )
            if result.scalar_one_or_none():
                print(f"  SKIP teacher (NIP exists): {t['nip']} - {t['nama_lengkap']}")
                continue

            user = User(
                user_type=UserType.guru,
                registration_status=RegistrationStatus.pending,
                username=None,
                password_hash=None,
                is_active=False,
            )
            session.add(user)
            await session.flush()

            profile = GuruProfile(
                user_id=user.user_id,
                nip=t["nip"],
                nama_lengkap=t["nama_lengkap"],
                jenis_kelamin=t.get("jenis_kelamin"),
                structural_role=t.get("structural_role", StructuralRole.guru),
                bidang_wakasek=t.get("bidang_wakasek"),
                mata_pelajaran=t.get("mata_pelajaran"),
                pendidikan_terakhir=t.get("pendidikan_terakhir"),
                status_guru=StatusGuru.aktif,
            )
            session.add(profile)
            role_label = t.get("structural_role", StructuralRole.guru).value
            if t.get("bidang_wakasek"):
                role_label += f" ({t['bidang_wakasek'].value})"
            print(f"  CREATED teacher: {t['nip']} - {t['nama_lengkap']} [{role_label}]")

        await session.commit()

    await engine.dispose()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
