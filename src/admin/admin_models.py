from sqladmin import ModelView

from src.models.bookings import BookingsOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UserOrm


class UserAdmin(ModelView, model=UserOrm):
    column_list = [UserOrm.id, UserOrm.email, UserOrm.role]
    name = "Пользователь"
    name_plural = "Пользователи"


class HotelAdmin(ModelView, model=HotelsOrm):
    column_list = [HotelsOrm.id, HotelsOrm.title, HotelsOrm.location]
    name = "Отель"
    name_plural = "Отели"


class RoomAdmin(ModelView, model=RoomsOrm):
    column_list = [
        RoomsOrm.id,
        RoomsOrm.title,
        RoomsOrm.price,
        RoomsOrm.hotel_id,
        RoomsOrm.description,
    ]
    name = "Комната"
    name_plural = "Комнаты"


class BookingAdmin(ModelView, model=BookingsOrm):
    column_list = [
        BookingsOrm.id,
        BookingsOrm.price,
        BookingsOrm.room_id,
        BookingsOrm.user_id,
    ]
    name = "Бронь"
    name_plural = "Брони"
