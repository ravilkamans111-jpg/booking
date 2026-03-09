from datetime import date

from pydantic import BaseModel


class BookingAdd(BaseModel):
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int
    rate: str


class BookingSchema(BookingAdd):
    id: int
