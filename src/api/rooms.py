from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from src.exceptions import DateFromCantBeAfterDateTo
from src.permisions import require_permission, Permission
from src.services.rooms import RoomsService
from src.api.dependencies import DBDep
from src.schemas.rooms import RoomADD

router = APIRouter(prefix="/rooms")


@router.post(
    "/room",
    summary="Создать комнату",
    # dependencies=[Depends((require_permission(Permission.WRITE_ROOMS)))],
)
async def create_rooms(room: RoomADD, db: DBDep):
    await db.rooms.add(room)
    await db.commit()
    return {"success": 200}


@router.get(
    "/",
    summary="Получить все комнаты",
    dependencies=[Depends((require_permission(Permission.READ_ROOMS)))],
)
async def get_all_rooms(db: DBDep):
    return await db.rooms.get_all()


@router.get(
    "/{hotel_id}/rooms",
    summary="Получить комнате в отеле по ID",
)
async def get_rooms_by_hotel_id(
    db: DBDep, hotel_id: int, date_from: date, date_to: date
):
    try:
        return await RoomsService(db).get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    except DateFromCantBeAfterDateTo:
        raise HTTPException(
            status_code=409, detail="Дата выезда не может быть раньше даты заезда"
        )
