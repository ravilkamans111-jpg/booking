from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.permisions import userrole_enum
from src.database import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(
        userrole_enum,
        nullable=False,
        server_default="user",
    )
    status: Mapped[str] = mapped_column(nullable=False, server_default="0")
