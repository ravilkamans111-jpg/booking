from pydantic import BaseModel, ConfigDict

from src.schemas.facilities import Facility


class RoomADD(BaseModel):
    hotel_id: int
    title: str
    description: str
    price: int
    quantity: int


class RoomSchema(RoomADD):
    id: int

    # question
    model_config = ConfigDict(from_attributes=True)


class RoomWithFacilities(RoomADD):
    facilities: list[Facility]
