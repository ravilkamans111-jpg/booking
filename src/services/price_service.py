import asyncio

from src.exceptions import DateFromCantBeAfterDateTo
from src.services.base import BaseService


from datetime import date, timedelta


SEASONS = {
    "high": {
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 12, 31),
        "price_multiplier": 1.4,
    },
    "medium": {
        "date_from": date(2026, 1, 1),
        "date_to": date(2026, 3, 31),
        "price_multiplier": 0.7,
    },
}


LONG_STAY_THRESHOLD_DAYS = 7
SHORT_STAY_MULTIPLIER = 1.2

WEEKEND_DAYS = {4, 5, 6}  # Friday, Saturday, Sunday
WEEKEND_MULTIPLIER = 1.11

HIGH_OCCUPANCY_THRESHOLD = 8
HIGH_OCCUPANCY_MULTIPLIER = 1.2


class PriceChanger(BaseService):

    def _get_mult_by_occupancy(self, days_of_booking: int, price: int) -> int:
        if days_of_booking >= LONG_STAY_THRESHOLD_DAYS:
            return price
        return round(price * SHORT_STAY_MULTIPLIER)

    def _get_mult_by_season(self, current_date: date, price: int) -> int:
        for season in SEASONS.values():
            if season["date_from"] <= current_date <= season["date_to"]:
                return round(price * season["price_multiplier"])
        return price

    def _get_mult_by_day_of_week(self, current_date: date, price: int) -> int:
        if current_date.weekday() in WEEKEND_DAYS:
            return round(price * WEEKEND_MULTIPLIER)
        return price

    def _apply_occupancy_multiplier(self, bookings_count: int, price: int) -> int:
        if bookings_count >= HIGH_OCCUPANCY_THRESHOLD:
            return round(price * HIGH_OCCUPANCY_MULTIPLIER)
        return price

    async def get_final_price(
        self,
        date_from: date,
        date_to: date,
        hotel_id: int,
        room_id: int,
    ):
        if date_from >= date_to:
            raise DateFromCantBeAfterDateTo

        base_room_price, bookings = await asyncio.gather(
            self.db.rooms.get_room_price_by_id(room_id=room_id),
            self.db.bookings.get_bookings(date_from, date_to, hotel_id),
        )

        if base_room_price is None:
            raise ValueError(f"Room {room_id} not found")

        bookings_count = len(bookings)
        days_of_booking = (date_to - date_from).days
        price_by_occupancy = self._get_mult_by_occupancy(days_of_booking, base_room_price)

        daily_prices: list[int] = []
        current_date = date_from

        while current_date < date_to:
            daily_price = self._get_mult_by_season(current_date, price_by_occupancy)
            daily_price = self._get_mult_by_day_of_week(current_date, daily_price)
            daily_price = self._apply_occupancy_multiplier(bookings_count, daily_price)
            daily_prices.append(daily_price)
            current_date += timedelta(days=1)

        return sum(daily_prices)






#
# SEASONS = {
#     "high": {
#         "date_from": date(2026, 6, 1),
#         "date_to": date(2026, 12, 31),
#         "price_multiplier": 1.4,
#     },
#     "medium": {
#         "date_from": date(2026, 1, 1),
#         "date_to": date(2026, 3, 31),
#         "price_multiplier": 0.7,
#     },
# }
#
# class PriceChanger(BaseService):
#     async def get_mult_by_occupancy(self, days_of_booking, price):
#         if days_of_booking >= 7:
#             return price * 1
#         return price * 1.2
#
#     async def get_mult_by_season(self, dates, base_price):
#         for s in SEASONS.values():
#             if s["date_from"] <= dates <= s["date_to"]:
#                 return base_price * s["price_multiplier"]
#
#         return base_price
#
#     async def get_mult_by_day_of_weeks(self, date_from: date, price: int):
#         if date_from.weekday() >= 4:
#             return price * 1.11
#         return price
#
#     async def get_mult_by_bookings_in_hotel(
#         self, date_from: date, date_to: date, hotel_id: int, price: int
#     ):
#         result = await self.db.bookings.get_bookings(date_from, date_to, hotel_id)
#         if len(result) >= 8:
#             return price * 1.2
#         return price
#
#     async def get_final_price(
#         self, date_to: date, date_from: date, hotel_id: int, room_id: int
#     ):
#         prices_of_all_days = []
#         base_room_price = await self.db.rooms.get_room_price_by_id(room_id=room_id)
#         days_of_booking = date_to.day - date_from.day
#         price_by_occupancy = await self.get_mult_by_occupancy(
#             days_of_booking, base_room_price
#         )
#
#         while date_from <= date_to:
#             price_by_season = await self.get_mult_by_season(
#                 date_from, price_by_occupancy
#             )
#             price_by_weekdays = await self.get_mult_by_day_of_weeks(
#                 date_from=date_from, price=price_by_season
#             )
#             price_by_bookings_in_hotel = await self.get_mult_by_bookings_in_hotel(
#                 date_from=date_from,
#                 date_to=date_to,
#                 price=price_by_weekdays,
#                 hotel_id=hotel_id,
#             )
#             prices_of_all_days.append(price_by_bookings_in_hotel)
#
#             date_from += timedelta(days=1)
#
#         return sum(prices_of_all_days)
