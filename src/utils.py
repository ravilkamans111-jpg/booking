from src.repos.facilities import FacilityRepository
from src.repos.favourites import FavouritesRepository
from src.repos.bookings import BookingsRepository
from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.repos.users import UserRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.favourites = FavouritesRepository(self.session)
        self.facilities = FacilityRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
