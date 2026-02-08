from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tahun_ajaran import TahunAjaran
from app.models.semester import Semester
from app.models.kalender_akademik import KalenderAkademik
from app.models.mata_pelajaran import MataPelajaran
from app.models.slot_waktu import SlotWaktu
from app.dto.akademik.tahun_ajaran_dto import (
    CreateTahunAjaranDTO, UpdateTahunAjaranDTO, TahunAjaranResponseDTO
)
from app.dto.akademik.semester_dto import (
    CreateSemesterDTO, UpdateSemesterDTO, SemesterResponseDTO
)
from app.dto.akademik.kalender_dto import (
    CreateKalenderDTO, UpdateKalenderDTO, KalenderResponseDTO
)
from app.dto.akademik.mapel_dto import (
    CreateMapelDTO, UpdateMapelDTO, MapelResponseDTO
)
from app.dto.akademik.slot_waktu_dto import (
    CreateSlotWaktuDTO, UpdateSlotWaktuDTO, SlotWaktuResponseDTO
)
from app.dto.akademik.kelas_dto import MessageResponseDTO


class AkademikService:
    """
    Academic service for CRUD on TahunAjaran, Semester, KalenderAkademik, MataPelajaran, SlotWaktu.

    Raises:
        HTTPException: 400, 404, 500
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── TahunAjaran CRUD ─────────────────────────────────────────────────────

    async def create_tahun_ajaran(self, request: CreateTahunAjaranDTO) -> TahunAjaranResponseDTO:
        """
        Create a new academic year.

        Raises:
            HTTPException: 400 if nama already exists
            HTTPException: 500 if database error
        """
        try:
            # Check if nama already exists
            result = await self.db.execute(
                select(TahunAjaran).where(TahunAjaran.nama == request.nama)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Academic year '{request.nama}' already exists"
                )

            tahun_ajaran = TahunAjaran(
                nama=request.nama,
                tanggal_mulai=request.tanggal_mulai,
                tanggal_selesai=request.tanggal_selesai,
                is_active=request.is_active,
            )
            self.db.add(tahun_ajaran)
            await self.db.commit()
            await self.db.refresh(tahun_ajaran)

            return self._to_tahun_ajaran_dto(tahun_ajaran)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create academic year: {str(e)}"
            )

    async def list_tahun_ajaran(self) -> list[TahunAjaranResponseDTO]:
        """
        List all academic years.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(TahunAjaran))
        tahun_ajaran_list = result.scalars().all()
        return [self._to_tahun_ajaran_dto(ta) for ta in tahun_ajaran_list]

    async def get_tahun_ajaran(self, tahun_ajaran_id: UUID) -> TahunAjaranResponseDTO:
        """
        Get a single academic year by ID.

        Raises:
            HTTPException: 404 if academic year not found
        """
        result = await self.db.execute(
            select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == tahun_ajaran_id)
        )
        tahun_ajaran = result.scalar_one_or_none()
        if not tahun_ajaran:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic year not found"
            )
        return self._to_tahun_ajaran_dto(tahun_ajaran)

    async def update_tahun_ajaran(
        self, tahun_ajaran_id: UUID, request: UpdateTahunAjaranDTO
    ) -> TahunAjaranResponseDTO:
        """
        Partial update an academic year.

        Raises:
            HTTPException: 404 if academic year not found
            HTTPException: 400 if nama conflict or no fields to update
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == tahun_ajaran_id)
        )
        tahun_ajaran = result.scalar_one_or_none()
        if not tahun_ajaran:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic year not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Check nama uniqueness if being changed
        if "nama" in update_data and update_data["nama"] != tahun_ajaran.nama:
            nama_check = await self.db.execute(
                select(TahunAjaran).where(TahunAjaran.nama == update_data["nama"])
            )
            if nama_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Academic year '{update_data['nama']}' already exists"
                )

        for field, value in update_data.items():
            setattr(tahun_ajaran, field, value)

        await self.db.commit()
        await self.db.refresh(tahun_ajaran)
        return self._to_tahun_ajaran_dto(tahun_ajaran)

    async def delete_tahun_ajaran(self, tahun_ajaran_id: UUID) -> MessageResponseDTO:
        """
        Delete an academic year.

        Raises:
            HTTPException: 404 if academic year not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == tahun_ajaran_id)
        )
        tahun_ajaran = result.scalar_one_or_none()
        if not tahun_ajaran:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic year not found"
            )

        await self.db.delete(tahun_ajaran)
        await self.db.commit()
        return MessageResponseDTO(message="Academic year deleted successfully")

    # ── Semester CRUD ────────────────────────────────────────────────────────

    async def create_semester(self, request: CreateSemesterDTO) -> SemesterResponseDTO:
        """
        Create a new semester.

        Raises:
            HTTPException: 400 if tahun_ajaran_id doesn't exist or unique constraint violation
            HTTPException: 500 if database error
        """
        try:
            # Validate tahun_ajaran_id exists
            result = await self.db.execute(
                select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == request.tahun_ajaran_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Academic year with ID '{request.tahun_ajaran_id}' does not exist"
                )

            # Check unique constraint (tahun_ajaran_id, tipe)
            semester_check = await self.db.execute(
                select(Semester).where(
                    Semester.tahun_ajaran_id == request.tahun_ajaran_id,
                    Semester.tipe == request.tipe
                )
            )
            if semester_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Semester {request.tipe.value} already exists for this academic year"
                )

            semester = Semester(
                tahun_ajaran_id=request.tahun_ajaran_id,
                tipe=request.tipe,
                tanggal_mulai=request.tanggal_mulai,
                tanggal_selesai=request.tanggal_selesai,
                is_active=request.is_active,
            )
            self.db.add(semester)
            await self.db.commit()
            await self.db.refresh(semester)

            return self._to_semester_dto(semester)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create semester: {str(e)}"
            )

    async def list_semesters(self) -> list[SemesterResponseDTO]:
        """
        List all semesters.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(Semester))
        semesters = result.scalars().all()
        return [self._to_semester_dto(s) for s in semesters]

    async def get_semester(self, semester_id: UUID) -> SemesterResponseDTO:
        """
        Get a single semester by ID.

        Raises:
            HTTPException: 404 if semester not found
        """
        result = await self.db.execute(
            select(Semester).where(Semester.semester_id == semester_id)
        )
        semester = result.scalar_one_or_none()
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semester not found"
            )
        return self._to_semester_dto(semester)

    async def list_semesters_by_tahun_ajaran(self, tahun_ajaran_id: UUID) -> list[SemesterResponseDTO]:
        """
        List all semesters for a specific academic year.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(Semester).where(Semester.tahun_ajaran_id == tahun_ajaran_id)
        )
        semesters = result.scalars().all()
        return [self._to_semester_dto(s) for s in semesters]

    async def update_semester(
        self, semester_id: UUID, request: UpdateSemesterDTO
    ) -> SemesterResponseDTO:
        """
        Partial update a semester.

        Raises:
            HTTPException: 404 if semester not found
            HTTPException: 400 if no fields to update
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(Semester).where(Semester.semester_id == semester_id)
        )
        semester = result.scalar_one_or_none()
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semester not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        for field, value in update_data.items():
            setattr(semester, field, value)

        await self.db.commit()
        await self.db.refresh(semester)
        return self._to_semester_dto(semester)

    async def delete_semester(self, semester_id: UUID) -> MessageResponseDTO:
        """
        Delete a semester.

        Raises:
            HTTPException: 404 if semester not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(Semester).where(Semester.semester_id == semester_id)
        )
        semester = result.scalar_one_or_none()
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semester not found"
            )

        await self.db.delete(semester)
        await self.db.commit()
        return MessageResponseDTO(message="Semester deleted successfully")

    # ── KalenderAkademik CRUD ────────────────────────────────────────────────

    async def create_kalender(self, request: CreateKalenderDTO) -> KalenderResponseDTO:
        """
        Create a new academic calendar entry.

        Raises:
            HTTPException: 400 if tahun_ajaran_id doesn't exist
            HTTPException: 500 if database error
        """
        try:
            # Validate tahun_ajaran_id exists
            result = await self.db.execute(
                select(TahunAjaran).where(TahunAjaran.tahun_ajaran_id == request.tahun_ajaran_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Academic year with ID '{request.tahun_ajaran_id}' does not exist"
                )

            kalender = KalenderAkademik(
                tahun_ajaran_id=request.tahun_ajaran_id,
                tanggal=request.tanggal,
                jenis=request.jenis,
                keterangan=request.keterangan,
            )
            self.db.add(kalender)
            await self.db.commit()
            await self.db.refresh(kalender)

            return self._to_kalender_dto(kalender)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create calendar entry: {str(e)}"
            )

    async def list_kalender(self) -> list[KalenderResponseDTO]:
        """
        List all academic calendar entries.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(KalenderAkademik))
        kalender_list = result.scalars().all()
        return [self._to_kalender_dto(k) for k in kalender_list]

    async def list_kalender_by_tahun_ajaran(self, tahun_ajaran_id: UUID) -> list[KalenderResponseDTO]:
        """
        List all calendar entries for a specific academic year.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(KalenderAkademik).where(KalenderAkademik.tahun_ajaran_id == tahun_ajaran_id)
        )
        kalender_list = result.scalars().all()
        return [self._to_kalender_dto(k) for k in kalender_list]

    async def update_kalender(
        self, kalender_id: UUID, request: UpdateKalenderDTO
    ) -> KalenderResponseDTO:
        """
        Partial update a calendar entry.

        Raises:
            HTTPException: 404 if calendar entry not found
            HTTPException: 400 if no fields to update
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(KalenderAkademik).where(KalenderAkademik.kalender_id == kalender_id)
        )
        kalender = result.scalar_one_or_none()
        if not kalender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar entry not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        for field, value in update_data.items():
            setattr(kalender, field, value)

        await self.db.commit()
        await self.db.refresh(kalender)
        return self._to_kalender_dto(kalender)

    async def delete_kalender(self, kalender_id: UUID) -> MessageResponseDTO:
        """
        Delete a calendar entry.

        Raises:
            HTTPException: 404 if calendar entry not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(KalenderAkademik).where(KalenderAkademik.kalender_id == kalender_id)
        )
        kalender = result.scalar_one_or_none()
        if not kalender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar entry not found"
            )

        await self.db.delete(kalender)
        await self.db.commit()
        return MessageResponseDTO(message="Calendar entry deleted successfully")

    # ── MataPelajaran CRUD ───────────────────────────────────────────────────

    async def create_mapel(self, request: CreateMapelDTO) -> MapelResponseDTO:
        """
        Create a new subject (mata pelajaran).

        Raises:
            HTTPException: 400 if kode_mapel already exists
            HTTPException: 500 if database error
        """
        try:
            # Check if kode_mapel already exists
            result = await self.db.execute(
                select(MataPelajaran).where(MataPelajaran.kode_mapel == request.kode_mapel)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject code '{request.kode_mapel}' already exists"
                )

            mapel = MataPelajaran(
                kode_mapel=request.kode_mapel,
                nama_mapel=request.nama_mapel,
                kelompok=request.kelompok,
                jam_per_minggu=request.jam_per_minggu,
                is_active=request.is_active,
            )
            self.db.add(mapel)
            await self.db.commit()
            await self.db.refresh(mapel)

            return self._to_mapel_dto(mapel)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create subject: {str(e)}"
            )

    async def list_mapel(self) -> list[MapelResponseDTO]:
        """
        List all subjects.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(MataPelajaran))
        mapel_list = result.scalars().all()
        return [self._to_mapel_dto(m) for m in mapel_list]

    async def get_mapel(self, mapel_id: UUID) -> MapelResponseDTO:
        """
        Get a single subject by ID.

        Raises:
            HTTPException: 404 if subject not found
        """
        result = await self.db.execute(
            select(MataPelajaran).where(MataPelajaran.mapel_id == mapel_id)
        )
        mapel = result.scalar_one_or_none()
        if not mapel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        return self._to_mapel_dto(mapel)

    async def update_mapel(
        self, mapel_id: UUID, request: UpdateMapelDTO
    ) -> MapelResponseDTO:
        """
        Partial update a subject.

        Raises:
            HTTPException: 404 if subject not found
            HTTPException: 400 if kode_mapel conflict or no fields to update
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(MataPelajaran).where(MataPelajaran.mapel_id == mapel_id)
        )
        mapel = result.scalar_one_or_none()
        if not mapel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Check kode_mapel uniqueness if being changed
        if "kode_mapel" in update_data and update_data["kode_mapel"] != mapel.kode_mapel:
            kode_check = await self.db.execute(
                select(MataPelajaran).where(MataPelajaran.kode_mapel == update_data["kode_mapel"])
            )
            if kode_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject code '{update_data['kode_mapel']}' already exists"
                )

        for field, value in update_data.items():
            setattr(mapel, field, value)

        await self.db.commit()
        await self.db.refresh(mapel)
        return self._to_mapel_dto(mapel)

    async def delete_mapel(self, mapel_id: UUID) -> MessageResponseDTO:
        """
        Delete a subject.

        Raises:
            HTTPException: 404 if subject not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(MataPelajaran).where(MataPelajaran.mapel_id == mapel_id)
        )
        mapel = result.scalar_one_or_none()
        if not mapel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        await self.db.delete(mapel)
        await self.db.commit()
        return MessageResponseDTO(message="Subject deleted successfully")

    # ── SlotWaktu CRUD ───────────────────────────────────────────────────────

    async def create_slot_waktu(self, request: CreateSlotWaktuDTO) -> SlotWaktuResponseDTO:
        """
        Create a new time slot.

        Raises:
            HTTPException: 500 if database error
        """
        try:
            slot = SlotWaktu(
                nama=request.nama,
                jam_mulai=request.jam_mulai,
                jam_selesai=request.jam_selesai,
                urutan=request.urutan,
                is_piket=request.is_piket,
            )
            self.db.add(slot)
            await self.db.commit()
            await self.db.refresh(slot)

            return self._to_slot_waktu_dto(slot)

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create time slot: {str(e)}"
            )

    async def list_slot_waktu(self) -> list[SlotWaktuResponseDTO]:
        """
        List all time slots, ordered by urutan.

        Raises:
            HTTPException: 500 if database error
        """
        result = await self.db.execute(select(SlotWaktu).order_by(SlotWaktu.urutan))
        slots = result.scalars().all()
        return [self._to_slot_waktu_dto(s) for s in slots]

    async def update_slot_waktu(
        self, slot_id: UUID, request: UpdateSlotWaktuDTO
    ) -> SlotWaktuResponseDTO:
        """
        Partial update a time slot.

        Raises:
            HTTPException: 404 if time slot not found
            HTTPException: 400 if no fields to update
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(SlotWaktu).where(SlotWaktu.slot_id == slot_id)
        )
        slot = result.scalar_one_or_none()
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time slot not found"
            )

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        for field, value in update_data.items():
            setattr(slot, field, value)

        await self.db.commit()
        await self.db.refresh(slot)
        return self._to_slot_waktu_dto(slot)

    async def delete_slot_waktu(self, slot_id: UUID) -> MessageResponseDTO:
        """
        Delete a time slot.

        Raises:
            HTTPException: 404 if time slot not found
            HTTPException: 500 if database error
        """
        result = await self.db.execute(
            select(SlotWaktu).where(SlotWaktu.slot_id == slot_id)
        )
        slot = result.scalar_one_or_none()
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time slot not found"
            )

        await self.db.delete(slot)
        await self.db.commit()
        return MessageResponseDTO(message="Time slot deleted successfully")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _to_tahun_ajaran_dto(self, tahun_ajaran: TahunAjaran) -> TahunAjaranResponseDTO:
        return TahunAjaranResponseDTO(
            tahun_ajaran_id=tahun_ajaran.tahun_ajaran_id,
            nama=tahun_ajaran.nama,
            tanggal_mulai=tahun_ajaran.tanggal_mulai,
            tanggal_selesai=tahun_ajaran.tanggal_selesai,
            is_active=tahun_ajaran.is_active,
        )

    def _to_semester_dto(self, semester: Semester) -> SemesterResponseDTO:
        return SemesterResponseDTO(
            semester_id=semester.semester_id,
            tahun_ajaran_id=semester.tahun_ajaran_id,
            tipe=semester.tipe,
            tanggal_mulai=semester.tanggal_mulai,
            tanggal_selesai=semester.tanggal_selesai,
            is_active=semester.is_active,
        )

    def _to_kalender_dto(self, kalender: KalenderAkademik) -> KalenderResponseDTO:
        return KalenderResponseDTO(
            kalender_id=kalender.kalender_id,
            tahun_ajaran_id=kalender.tahun_ajaran_id,
            tanggal=kalender.tanggal,
            jenis=kalender.jenis,
            keterangan=kalender.keterangan,
        )

    def _to_mapel_dto(self, mapel: MataPelajaran) -> MapelResponseDTO:
        return MapelResponseDTO(
            mapel_id=mapel.mapel_id,
            kode_mapel=mapel.kode_mapel,
            nama_mapel=mapel.nama_mapel,
            kelompok=mapel.kelompok,
            jam_per_minggu=mapel.jam_per_minggu,
            is_active=mapel.is_active,
        )

    def _to_slot_waktu_dto(self, slot: SlotWaktu) -> SlotWaktuResponseDTO:
        return SlotWaktuResponseDTO(
            slot_id=slot.slot_id,
            nama=slot.nama,
            jam_mulai=slot.jam_mulai,
            jam_selesai=slot.jam_selesai,
            urutan=slot.urutan,
            is_piket=slot.is_piket,
        )
