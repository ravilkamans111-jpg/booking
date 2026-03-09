from fastapi import APIRouter, Body

from src.services.facilities import FacilitiesService
from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep

router = APIRouter(prefix="/facilities")


@router.post("", summary="Создать удобство")
async def create_facility(db: DBDep, facility: FacilityAdd = Body()):
    return await FacilitiesService(db).create_facility(facility)
