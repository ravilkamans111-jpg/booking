import logging

from src.api.utils.send_welcome_email import EmailSender
from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils import DBManager
import asyncio


async def get_bookings_with_today_check_in_helper():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        result = await db.bookings.get_bookings_with_today_check_in()
        logging.info(f"{result=}")


async def get_bookings_confirmation_helper(email, hotel_title):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        result = await EmailSender().send_confirmation_email(
            email=email, db=db, hotel_title=hotel_title
        )
        logging.info(f"Email sent to {email}")


@celery_instance.task(name="booking_today_check_in")
def send_mail_to_users_with_today_check_in():
    asyncio.run(get_bookings_with_today_check_in_helper())


@celery_instance.task
def send_booking_confirmation(email, hotel_title):
    asyncio.run(get_bookings_confirmation_helper(email=email, hotel_title=hotel_title))
