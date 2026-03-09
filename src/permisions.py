from enum import Enum
from fastapi import HTTPException, status
from fastapi import Request
from jwt import ExpiredSignatureError

from src.authorization_services import JWTToken

from sqlalchemy.dialects import postgresql

userrole_enum = postgresql.ENUM(
    "guest",
    "user",
    "moderator",
    "admin",
    name="userrole",
    create_type=False,
)


class Permission(str, Enum):
    # Users
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"

    # Hotels
    READ_HOTELS = "read:hotels"
    WRITE_HOTELS = "write:hotels"
    DELETE_HOTELS = "delete:hotels"

    # Bookings
    READ_BOOKINGS = "read:bookings"
    WRITE_BOOKINGS = "write:bookings"
    DELETE_BOOKINGS = "delete:bookings"

    READ_ROOMS = "read:rooms"
    WRITE_ROOMS = "write:rooms"
    DELETE_ROOMS = "delete:rooms"

    # Admin
    ADMIN_PANEL = "admin:panel"
    MANAGE_ROLES = "admin:roles"


# Роли
class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


# Permissions для каждой роли
ROLE_PERMISSIONS = {
    UserRole.GUEST: {
        Permission.READ_HOTELS,
    },
    UserRole.USER: {
        Permission.READ_HOTELS,
        Permission.READ_USERS,
        Permission.READ_BOOKINGS,
        Permission.WRITE_BOOKINGS,
        Permission.READ_ROOMS,
    },
    UserRole.MODERATOR: {
        Permission.READ_HOTELS,
        Permission.WRITE_HOTELS,
        Permission.DELETE_HOTELS,
        Permission.READ_USERS,
        Permission.READ_BOOKINGS,
        Permission.WRITE_BOOKINGS,
        Permission.DELETE_BOOKINGS,
        Permission.READ_ROOMS,
        Permission.WRITE_ROOMS,
        Permission.DELETE_ROOMS,
    },
    UserRole.ADMIN: {
        # Админ имеет ВСЕ права
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_HOTELS,
        Permission.WRITE_HOTELS,
        Permission.DELETE_HOTELS,
        Permission.READ_BOOKINGS,
        Permission.WRITE_BOOKINGS,
        Permission.DELETE_BOOKINGS,
        Permission.ADMIN_PANEL,
        Permission.MANAGE_ROLES,
        Permission.READ_ROOMS,
        Permission.WRITE_ROOMS,
        Permission.DELETE_ROOMS,
    },
}


def require_permission(permission: Permission):
    def dependency(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
            )
        try:
            payload = JWTToken().decode_token(token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Нужно авторизоваться заново",
            )

        user_role = payload.get("user_role")
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Роль не указана"
            )

        role_permissions = ROLE_PERMISSIONS.get(UserRole(user_role), set())
        if permission not in role_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
            )

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Авторизуйтесь"
            )

        return payload

    return dependency
