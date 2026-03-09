from typing import Annotated

import jwt
from fastapi import Depends, Request, HTTPException, status, Response

from src.config import settings
from src.api_fetch_services.hotels import HotelsHTTPClient
from src.database import async_session_maker
from src.authorization_services import JWTToken
from src.utils import DBManager


def get_access_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не предоставили токен доступа чао какао",
        )
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не предоставили токен доступа чао какао",
        )
    return token


def get_current_user(access_token=Depends(get_access_token)) -> int:
    """Извлекает user_id из access token в cookie"""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = JWTToken().decode_token(access_token)
        user_id = JWTToken().validate_token_payload(payload, "user_id")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Время токена истекло"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Устанавливает access и refresh токены в cookies"""

    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
    )

    # Refresh token cookie
    response.set_cookie(key="refresh_token", value=refresh_token)


def clear_auth_cookies(response: Response):
    response.delete_cookie(
        key="access_token",
    )
    response.delete_cookie(
        key="refresh_token",
    )


def get_user_role_from_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет токена")
    return JWTToken().validate_user_role_payload(token)


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


async def get_hotels_session():
    async with HotelsHTTPClient(api_key=settings.HOTELS_API_KEY) as ss:
        yield ss


UserRoleCheck = Annotated[bool, Depends(get_user_role_from_token)]

UserIdDep = Annotated[int, Depends(get_current_user)]
UserRefreshToken = Annotated[str, Depends(get_refresh_token)]

DBDep = Annotated[DBManager, Depends(get_db)]

HotelsSessionDep = Annotated[HotelsHTTPClient, Depends(get_hotels_session)]
