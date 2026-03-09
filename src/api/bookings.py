from fastapi import APIRouter, Depends, HTTPException

from src.exceptions import RoomAlreadyBooked, DateFromCantBeAfterDateTo
from src.exceptions import IsNotBookingOfThisClient
from src.services.bookings import BookingsService
from src.permisions import require_permission, Permission
from src.schemas.bookings import BookingAdd
from src.api.dependencies import DBDep, UserIdDep

router = APIRouter(prefix="/bookings")


@router.get(
    "/",
    summary="Получить все бронирования",
    dependencies=[Depends(require_permission(Permission.READ_BOOKINGS))],
)
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.post(
    "/booking",
    summary="Создать бронирование",
)
async def create_booking(db: DBDep, booking: BookingAdd, user_id: UserIdDep):
    try:
        return await BookingsService(db).create_booking(
            booking=booking
        )

    except RoomAlreadyBooked:
        raise HTTPException(status_code=409, detail="Нельзя забронировать эти даты")

    except DateFromCantBeAfterDateTo:
        raise HTTPException(
            status_code=409, detail="Дата выезда не может быть раньше даты заезда"
        )


@router.get(
    "/user/{user_id}",
    summary="Получить бронирования пользователя",
)
async def get_user_bookings(db: DBDep, user_id: UserIdDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.delete("/unbooking", summary="Отменить бронирование")
async def delete_booking(db: DBDep, booking_id: int, user_id: UserIdDep):
    try:
        await BookingsService(db).delete_booking(booking_id=booking_id, user_id=user_id)

    except IsNotBookingOfThisClient:
        raise HTTPException(status_code=404, detail="Такой брони не существует")

    return {"status": 200}
