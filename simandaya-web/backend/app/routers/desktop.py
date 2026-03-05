from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.config.settings import settings
from app.dependencies import verify_desktop_api_key, require_role
from app.enums import UserType
from app.models.user import User
from app.services.desktop_service import DesktopService
from app.dto.desktop.desktop_request import AttendanceEventDTO, UpdateDesktopSettingsDTO
from app.dto.desktop.desktop_response import StudentSyncDTO, AttendanceAckDTO, DesktopSettingsDTO
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/desktop",
    tags=["Desktop"],
)


@router.get(
    "/students",
    response_model=list[StudentSyncDTO],
    summary="Sync Student List",
    description="Get all active students for desktop app RFID mapping.",
    dependencies=[Depends(verify_desktop_api_key)],
)
async def list_students(
    db: AsyncSession = Depends(get_db),
) -> list[StudentSyncDTO]:
    service = DesktopService(db)
    return await service.list_students()


@router.get(
    "/settings",
    response_model=DesktopSettingsDTO,
    summary="Get Desktop Settings",
    description="Get current desktop app settings (late cutoff time).",
    dependencies=[Depends(verify_desktop_api_key)],
)
async def get_settings(
    db: AsyncSession = Depends(get_db),
) -> DesktopSettingsDTO:
    service = DesktopService(db)
    return await service.get_settings()


@router.put(
    "/settings",
    response_model=DesktopSettingsDTO,
    summary="Update Desktop Settings",
    description="Update desktop app settings (admin only).",
)
async def update_settings(
    request: UpdateDesktopSettingsDTO,
    current_user: User = Depends(require_role(UserType.admin)),
    db: AsyncSession = Depends(get_db),
) -> DesktopSettingsDTO:
    service = DesktopService(db)
    return await service.update_settings(request.late_cutoff_time, current_user.user_id)


@router.websocket("/ws")
async def desktop_websocket(
    websocket: WebSocket,
    api_key: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for desktop attendance events.

    Connect: ws://host/api/desktop/ws?api_key=<key>
    Send: AttendanceEventDTO JSON
    Receive: AttendanceAckDTO JSON
    """
    # Validate API key before accepting
    if api_key != settings.DESKTOP_API_KEY:
        await websocket.close(code=4001, reason="Invalid API key")
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            try:
                event = AttendanceEventDTO(**data)
                service = DesktopService(db)
                ack = await service.process_attendance_event(event)
                await db.commit()
            except Exception as e:
                await db.rollback()
                record_id = data.get("record_id", "unknown")
                ack = AttendanceAckDTO(
                    record_id=record_id,
                    status="error",
                    published_at=datetime.now(timezone.utc),
                    detail=str(e.detail) if hasattr(e, "detail") else str(e),
                )

            await websocket.send_json(ack.model_dump(mode="json"))

    except WebSocketDisconnect:
        pass
