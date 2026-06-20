from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import Query
from fastapi_cache.decorator import cache

from src.rate_limiter import rate_limit_get_user_info
from src.exceptions import ObjectIsAlreadyExistsException
from src.schemas.favourites import FavouritesAdd
from src.config import settings
from src.services.hotels import HotelService
from src.api.dependencies import DBDep, HotelsSessionDep, UserIdDep
from src.paginations import PaginationDep
from src.schemas.hotels import HotelADD

# router = APIRouter(prefix="/hotels", dependencies=[Depends(rate_limit_get_user_info)])
router = APIRouter(prefix="/hotels")


@router.post(
    " ",
    summary="Создать отель",
)
async def create_hotel(hotel: HotelADD, db: DBDep):
    await HotelService(db).create_hotel(hotel=hotel)
    return {"success": 200}


@router.get(
    "/hotels",
    summary="Получить все отели",
    dependencies=[Depends(rate_limit_get_user_info)],
)
async def get_all_hotels(
    db: DBDep,
    pagination: PaginationDep,
    response: Response,
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(examples=["2026-08-02"]),
    date_to: date = Query(examples=["2026-08-10"]),
    location: str | None = Query(None, description="Город"),
):
    response.headers["Cache-Control"] = "public, max-age=10"
    return await HotelService(db).get_filtered_by_time(
        pagination=pagination,
        title=title,
        date_from=date_from,
        date_to=date_to,
        location=location,
    )


@router.get(
    "/hotel/{hotel_name}",
    summary="Получить отель по имени",
)
async def get_hotel_by_name(user_id: UserIdDep, db: DBDep, title: str):
    return await db.hotels.get_filtered(title=title)


@router.get(
    "/sorted",
    summary="Получить отели по сортировке",
)
async def get_sorted_hotels(
    user_id: UserIdDep, db: DBDep, field: str = "title", direction: str = "desc"
):
    return await db.hotels.get_sorted(field=field, direction=direction)


@router.get(
    "/hotels/search/{city}",
    summary="Получение отелей по API",
)
@cache(expire=60)
async def get_hotels_by_api(
    # user_id: UserIdDep,
    session: HotelsSessionDep,
    db: DBDep,
    city: str,
    limit: int = 20,
    page: int = 1,
):
    return await session.search_by_city(
        db=db, city=city, limit=limit, page=page, base_url=settings.API_URL
    )


@router.post("/hotels/favourites", summary="Добавить отель в избранное")
async def add_hotel_to_favourites(db: DBDep, user_id: UserIdDep, hotel_id: int):
    add_data = FavouritesAdd(user_id=user_id, hotel_id=hotel_id)
    try:
        await db.favourites.add(add_data)
        await db.commit()
    except ObjectIsAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Отель уже добавлен в избранное")

    return {"status": 200}


@router.get("/favourites/{user_id}", summary="Получить избранные отели")
async def get_favourites_hotels(db: DBDep, user_id: UserIdDep):
    return await HotelService(db).get_favourites_hotels_by_id(user_id=user_id)
