import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram import types
from aiogram.types import Message
from aiogram.filters import Command

from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.repos.bookings import BookingsRepository
from src.repos.users import UserRepository
from src.database import async_session_maker
from src.config import settings


logging.basicConfig(level=logging.INFO)

bot = Bot(settings.TG_TOKEN)
dp = Dispatcher()


async def get_booking_info(session, user_email: str):
    user = await UserRepository(session).get_one_or_none(email=user_email)
    booking = await BookingsRepository(session).get_one_or_none(user_id=user.id)
    room = await RoomsRepository(session).get_one_or_none(id=booking.room_id)
    hotel = await HotelsRepository(session).get_one_or_none(id=room.hotel_id)

    return {
        "date": booking.date_to,
        "hotel": hotel.title,
        "room": room.title,
    }


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пришли свой email", parse_mode="HTML")


@dp.message()
async def message_handler(msg: Message):
    async with async_session_maker() as session:
        booking_info = await get_booking_info(session, msg.text.strip())

    if not booking_info:
        await bot.send_message(
            msg.chat.id,
            "Бронирование не найдено. Проверь email.",
        )
        return

    response = (
        f"📅 Дата Заезда: {booking_info['date']}\n"
        f"🏨 Отель: {booking_info['hotel']}\n"
        f"🏨 Комната: {booking_info['room']}"
    )

    await bot.send_message(msg.chat.id, response, parse_mode="Markdown")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
