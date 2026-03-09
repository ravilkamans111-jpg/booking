from datetime import date

from sqlalchemy import select

from src.models.rooms import RoomsOrm
from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings(self, date_in: date, date_out: date, hotel_id: int):
        stmt = (
            select(BookingsOrm)
            .join(RoomsOrm, BookingsOrm.room_id == RoomsOrm.id)
            .where(RoomsOrm.hotel_id == hotel_id)
            .where(
                BookingsOrm.date_from < date_out,
                BookingsOrm.date_to > date_in,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_bookings_days(self, date_in: date, date_out: date, room_id: int):
        stmt = select(BookingsOrm).where(
            BookingsOrm.room_id == room_id,
            BookingsOrm.date_from <= date_out,
            BookingsOrm.date_to >= date_in,
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_bookings_with_today_check_in(self):
        stmt = select(self.model).filter_by(date_from=date.today())
        bookings = await self.session.execute(stmt)
        return [
            self.mapper.map_to_domain_entity_pyd(booking)
            for booking in bookings.scalars().all()
        ]
