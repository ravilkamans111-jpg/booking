from fastapi import HTTPException

from src.services.base import BaseService


class HotelService(BaseService):
    async def create_hotel(self, hotel):
        await self.db.hotels.add(hotel)
        await self.db.commit()
        return hotel

    async def get_filtered_by_time(
        self, pagination, title, location, date_from, date_to
    ):
        if date_from >= date_to:
            raise HTTPException(
                status_code=422, detail="Дата заезда не может быть позже даты выезда"
            )

        return await self.db.hotels.get_filtered_by_time(
            date_to=date_to,
            date_from=date_from,
            title=title,
            location=location,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def get_favourites_hotels_by_id(self, user_id: int):
        return await self.db.favourites.get_filtered(user_id=user_id)

