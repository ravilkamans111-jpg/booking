from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class FavouritesOrm(Base):
    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
