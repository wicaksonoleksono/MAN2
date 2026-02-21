"""
Seed attendance and izin keluar records for existing students.

Usage (from host, with Docker running):
    docker exec simandaya-backend python scripts/seed_absensi.py

Creates attendance records for the last 7 days and a few izin keluar
records for today. Skips dates that already have attendance data.
"""

import sys
import asyncio
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, and_
from app.config.database import engine, async_session_maker
from app.models.user import User
from app.models.siswa_profile import SiswaProfile
from app.models.guru_profile import GuruProfile  # noqa: F401 — needed for User relationship resolution
from app.models.absensi import Absensi
from app.models.izin_keluar import IzinKeluar
from app.enums import UserType, StatusAbsensi


IZIN_REASONS = [
    "Sakit perut, perlu ke klinik",
    "Dijemput orang tua untuk keperluan keluarga",
    "Kontrol ke dokter gigi",
    "Mengambil obat di apotek",
    "Izin sholat Jumat di masjid luar",
]


async def seed():
    async with async_session_maker() as session:
        # Get all student user_ids
        result = await session.execute(
            select(User.user_id)
            .join(SiswaProfile, User.user_id == SiswaProfile.user_id)
            .where(User.user_type == UserType.siswa)
        )
        student_ids = [row[0] for row in result.all()]

        if not student_ids:
            print("No students found. Import students first:")
            print("  make seed-admins          (seeds admin + sample students)")
            print("  make import-students FILE=path/to/file.xlsx")
            await engine.dispose()
            return

        print(f"Found {len(student_ids)} students")

        today = date.today()
        statuses = list(StatusAbsensi)
        attendance_created = 0

        # Seed attendance for the last 7 days (skip weekends)
        for day_offset in range(7):
            d = today - timedelta(days=day_offset)
            if d.weekday() >= 5:  # skip Sat/Sun
                continue

            for uid in student_ids:
                # Check if already exists
                existing = await session.execute(
                    select(Absensi).where(
                        and_(Absensi.user_id == uid, Absensi.tanggal == d)
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # 70% hadir, 10% terlambat, 5% alfa, 10% sakit, 5% izin
                roll = random.random()
                if roll < 0.70:
                    st = StatusAbsensi.hadir
                elif roll < 0.80:
                    st = StatusAbsensi.terlambat
                elif roll < 0.85:
                    st = StatusAbsensi.alfa
                elif roll < 0.95:
                    st = StatusAbsensi.sakit
                else:
                    st = StatusAbsensi.izin

                time_in = None
                time_out = None
                if st in (StatusAbsensi.hadir, StatusAbsensi.terlambat):
                    hour = 7 if st == StatusAbsensi.hadir else random.randint(7, 8)
                    minute = random.randint(0, 59)
                    time_in = datetime(d.year, d.month, d.day, hour, minute, tzinfo=timezone.utc)
                    time_out = datetime(d.year, d.month, d.day, random.randint(14, 16), random.randint(0, 59), tzinfo=timezone.utc)

                record = Absensi(
                    user_id=uid,
                    tanggal=d,
                    status=st,
                    time_in=time_in,
                    time_out=time_out,
                )
                session.add(record)
                attendance_created += 1

        print(f"Created {attendance_created} attendance records")

        # Seed a few izin keluar for today
        izin_created = 0
        sample_students = random.sample(student_ids, min(3, len(student_ids)))
        for uid in sample_students:
            now = datetime.now(timezone.utc)
            hour = random.randint(9, 12)
            created = now.replace(hour=hour, minute=random.randint(0, 59))

            # 50% chance already returned
            waktu_kembali = None
            if random.random() > 0.5:
                waktu_kembali = created + timedelta(minutes=random.randint(15, 90))

            record = IzinKeluar(
                user_id=uid,
                created_at=created,
                keterangan=random.choice(IZIN_REASONS),
                waktu_kembali=waktu_kembali,
            )
            session.add(record)
            izin_created += 1

        print(f"Created {izin_created} izin keluar records")

        await session.commit()

    await engine.dispose()
    print("\nAbsensi seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
