from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.facilities import FacilitiesOrm
from src.database import Base


class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        secondary="rooms_facilities", back_populates="rooms"
    )
