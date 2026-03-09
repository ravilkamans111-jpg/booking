from src.repos.mappers.mappers import FavouritesDataMapper
from src.models.favourites import FavouritesOrm
from src.repos.base import BaseRepository


class FavouritesRepository(BaseRepository):
    model = FavouritesOrm
    mapper = FavouritesDataMapper
