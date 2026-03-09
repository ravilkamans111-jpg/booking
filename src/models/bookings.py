from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from src.database import Base


class BookingsOrm(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[int]
    rate: Mapped[str] = mapped_column(nullable=False, server_default="0")
