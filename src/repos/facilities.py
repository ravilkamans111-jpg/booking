from src.models.facilities import FacilitiesOrm
from src.repos.mappers.mappers import FacilitiesDataMapper
from src.repos.base import BaseRepository


class FacilityRepository(BaseRepository):
    mapper = FacilitiesDataMapper
    model = FacilitiesOrm
