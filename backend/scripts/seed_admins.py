"""
Seed admin accounts into the database.

Usage (from host, with Docker running):
    docker exec simandaya-backend python scripts/seed_admins.py

Creates: admin1, admin2, admin3 (password = username)
Skips any that already exist.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.config.database import engine, async_session_maker
from app.models.user import User
from app.enums import UserType, RegistrationStatus


ADMINS = [
    {"username": "admin1", "password": "1qaz2wsx3edc"},
    {"username": "admin2", "password": "1qaz2wsx3edc"},
    {"username": "admin3", "password": "1qaz2wsx3edc"},
]


async def seed():
    async with async_session_maker() as session:
        for admin in ADMINS:
            result = await session.execute(
                select(User).where(User.username == admin["username"])
            )
            if result.scalar_one_or_none():
                print(f"  SKIP (already exists): {admin['username']}")
                continue

            user = User(
                username=admin["username"],
                user_type=UserType.admin,
                registration_status=RegistrationStatus.completed,
                is_active=True,
            )
            user.set_password(admin["password"])
            session.add(user)
            print(f"  CREATED: {admin['username']} / {admin['password']}")

        await session.commit()

    await engine.dispose()
    print("\nAdmin seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
