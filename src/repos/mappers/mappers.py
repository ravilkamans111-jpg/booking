from src.models.facilities import FacilitiesOrm
from src.schemas.facilities import FacilityAdd
from src.schemas.favourites import FavouritesRead
from src.models.favourites import FavouritesOrm
from src.models.bookings import BookingsOrm
from src.schemas.bookings import BookingSchema
from src.models.rooms import RoomsOrm
from src.schemas.rooms import RoomSchema
from src.models.hotels import HotelsOrm
from src.models.users import UserOrm
from src.repos.mappers.base import DataMapper
from src.schemas.auth import UserRead
from src.schemas.hotels import Hotel


class HotelDataMapper(DataMapper):
    schema = Hotel
    db_model = HotelsOrm


class RoomDataMapper(DataMapper):
    schema = RoomSchema
    db_model = RoomsOrm


class UserDataMapper(DataMapper):
    schema = UserRead
    db_model = UserOrm


class BookingDataMapper(DataMapper):
    schema = BookingSchema
    db_model = BookingsOrm


class FavouritesDataMapper(DataMapper):
    schema = FavouritesRead
    db_model = FavouritesOrm


class FacilitiesDataMapper(DataMapper):
    schema = FacilityAdd
    db_model = FacilitiesOrm
