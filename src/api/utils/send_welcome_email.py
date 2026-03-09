from email.message import EmailMessage
import aiosmtplib
from src.utils import DBManager
import random


class EmailSender:
    async def send_mail(
        self,
        recipient: str,
        body: str,
        subject: str,
    ):
        admin_email = "admin@site.com"

        message = EmailMessage()
        message["From"] = admin_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            recipients=[recipient],
            sender=admin_email,
            hostname="localhost",
            port=1025,
        )

    async def send_welcome_email(self, user_email, db: DBManager):
        user = await db.users.get_one_or_none(email=user_email)

        await self.send_mail(
            body=f"Dear {user.email},\n\nWelcome to Booking",
            subject="Welcome to Booking",
            recipient=user.email,
        )

    async def send_confirmation_email(
        self, email: str, db: DBManager, hotel_title: str
    ):
        await self.send_mail(
            body=f"Dear {email},\n\n Your booking in {hotel_title} is confirm!",
            subject="Booking confirmation",
            recipient=email,
        )

    async def send_verify_code(self, code, user_email):
        await self.send_mail(
            body=f"Dear {user_email},\n\nWelcome to Booking, your code: {code}",
            subject="Verify code",
            recipient=user_email,
        )


async def get_random_code_for_verify_email():
    return random.choice(range(1000, 9999))
