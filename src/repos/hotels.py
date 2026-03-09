from sqlalchemy import select, func

from src.models.rooms import RoomsOrm
from src.repos.utils import rooms_ids_for_booking
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import HotelDataMapper


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self, date_from, date_to, title, location, limit, offset
    ):
        rooms_id_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)

        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_id_to_get))
            .distinct()
        )

        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        if location:
            query = query.filter(
                func.lower(HotelsOrm.location).contains(location.strip().lower())
            )

        if title:
            query = query.filter(
                func.lower(HotelsOrm.title).contains(title.strip().lower())
            )

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity_pyd(hotel)
            for hotel in result.scalars().all()
        ]
