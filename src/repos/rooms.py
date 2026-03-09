from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.schemas.rooms import RoomWithFacilities
from src.repos.utils import rooms_ids_for_booking
from src.models.rooms import RoomsOrm
from src.repos.mappers.mappers import RoomDataMapper
from src.repos.base import BaseRepository


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_room_price_by_id(self, room_id):
        stmt = select(self.model.price).where(RoomsOrm.id == room_id)
        model = await self.session.execute(stmt)
        result = model.scalar_one_or_none()
        return result

    async def get_filtered_by_time(self, hotel_id, date_from, date_to):
        rooms_ids_to_get = rooms_ids_for_booking(
            hotel_id=hotel_id, date_to=date_to, date_from=date_from
        )

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(self.model.id.in_(rooms_ids_to_get))
        )

        result = await self.session.execute(query)

        return [
            RoomWithFacilities.model_validate(model, from_attributes=True)
            for model in result.unique().scalars().all()
        ]
