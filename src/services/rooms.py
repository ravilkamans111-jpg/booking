from datetime import date


from src.exceptions import DateFromCantBeAfterDateTo
from src.services.base import BaseService


class RoomsService(BaseService):
    async def create_rooms(self, room):
        await self.db.rooms.add(room)
        await self.db.commit()
        return room

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        if date_from >= date_to:
            raise DateFromCantBeAfterDateTo

        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_to=date_to, date_from=date_from
        )
