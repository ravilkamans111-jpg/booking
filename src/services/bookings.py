from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from src.schemas.bookings import BookingAdd
from src.services.price_service import PriceChanger
from src.exceptions import IsNotBookingOfThisClient, DateFromCantBeAfterDateTo
from src.exceptions import RoomAlreadyBooked
from src.services.base import BaseService
from src.tasks.tasks import send_booking_confirmation


class BookingsService(BaseService):
    async def create_booking(self, booking: BaseModel):
        await self.db.session.execute(
            text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        )

        if booking.date_from >= booking.date_to:
            raise DateFromCantBeAfterDateTo

        bookings = await self.db.bookings.get_bookings_days(
            date_in=booking.date_from, date_out=booking.date_to, room_id=booking.room_id
        )

        room = await self.db.rooms.get_one_or_none(id=booking.room_id)

        if room.quantity <= len(bookings):
            raise RoomAlreadyBooked(status_code=409)

        final_price = await PriceChanger(self.db).get_final_price(
            date_to=booking.date_to,
            date_from=booking.date_from,
            room_id=booking.room_id,
            hotel_id=room.hotel_id,
        )
        booking_add = BookingAdd(
            date_to=booking.date_to,
            date_from=booking.date_from,
            room_id=booking.room_id,
            rate=booking.rate,
            user_id=booking.user_id,
            price=int(final_price),
        )

        await self.db.bookings.add(booking_add)
        await self.db.commit()

        hotel = await self.db.hotels.get_one_or_none(id=room.hotel_id)
        user = await self.db.users.get_one_or_none(id=booking.user_id)

        send_booking_confirmation.delay(email=user.email, hotel_title=hotel.title)

        return {"status": 200}, {"total_price": final_price}

    async def delete_booking(self, booking_id: int, user_id: int):
        booking = await self.db.bookings.get_one_or_none(id=booking_id)
        client = await self.db.users.get_one_or_none(id=user_id)

        if not booking:
            raise IsNotBookingOfThisClient(
                status_code=404, detail="Бронирования не существует"
            )

        if client.status == "premium":
            await self.db.bookings.delete(booking_id)

        elif client.status != "premium":
            if booking.rate == "comfort" or "business":
                await self.db.bookings.delete(booking_id)

        else:
            raise HTTPException(
                status_code=409, detail="Вы не можете отменить бронирование"
            )

        await self.db.commit()
