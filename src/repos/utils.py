from sqlalchemy import select, func
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def rooms_ids_for_booking(date_from, date_to, hotel_id=None):
    """Будем получать все номера в отеле в даты, заданные пользователем
    1. Считаем количество занятых комнат
    2.
    """
    rooms_count = (
        # берем номера комнат, фильтруем их по дате, создаем таблицу rooms_count
        # с двумя колонками room_id и rooms_booked (забронированные комнаты)
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .select_from(BookingsOrm)
        .filter(BookingsOrm.date_to >= date_from, BookingsOrm.date_from <= date_to)
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")
    )

    """Считаем количество свободных комнат"""
    rooms_left_table = (
        # Из числа комнат с определенным id вычитаем количество занятых
        # комнат. func.coalesce - выбирает наибольшее значение из двух
        # создается таблица с полями room_id и rooms_left (количество свободных комнат по id)
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.room_id, 0)).label(
                "rooms_left"
            ),
        )
        .select_from(RoomsOrm)
        # создаем таблицу rooms_left_table совмещенную из rooms_count и rooms
        # получается таблица с id комнат и количеством свободных комнат
        .outerjoin(rooms_count, rooms_count.c.room_id == RoomsOrm.id)
        .cte(name="rooms_left_table")
    )

    """Формируем запрос"""
    rooms_ids_for_hotel = select(RoomsOrm.id).select_from(RoomsOrm)
    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter(RoomsOrm.hotel_id == hotel_id)

    rooms_ids_for_hotel = rooms_ids_for_hotel.subquery("rooms_ids_for_hotel")

    """Оставляем только свободные комнаты и возвращаем их"""
    rooms_ids_to_get = (
        select(rooms_left_table.c.room_id)
        .select_from(rooms_left_table)
        .filter(
            rooms_left_table.c.rooms_left > 0,
            rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    return rooms_ids_to_get
