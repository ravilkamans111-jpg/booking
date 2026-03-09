import jwt
from fastapi import APIRouter, HTTPException, status, Request, Response, BackgroundTasks

from src.services.users import UsersService
from src.api.utils.send_welcome_email import EmailSender
from src.config import settings
from src.exceptions import ObjectIsAlreadyExistsException
from src.api.dependencies import (
    UserRefreshToken,
    UserIdDep,
    set_auth_cookies,
    clear_auth_cookies,
    DBDep,
)

from src.authorization_services import AuthorizationServices, JWTToken
from src.schemas.auth import UserRequestAdd, UserAdd

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", summary="Регистрация пользователя")
async def register_user(
    user: UserRequestAdd, db: DBDep, background_tasks: BackgroundTasks
):
    hashed_password = AuthorizationServices().get_password_hash(password=user.password)
    new_user_data = UserAdd(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        status=user.status,
    )
    try:
        await db.users.add(new_user_data)
        await db.commit()
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с такой почтой уже существует",
        )

    background_tasks.add_task(
        EmailSender().send_welcome_email, user_email=user.email, db=db
    )

    return {"status": 200}


@router.get("/login", summary="Авторизация пользователя")
async def login(user_email, password, db: DBDep, response: Response):
    user = await db.users.get_user_with_hashed_password(email=user_email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователя с email: {user_email} не существует",
        )

    if not AuthorizationServices().verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный пароль"
        )

    access_token = JWTToken().create_token(
        {"user_id": user.id, "user_role": user.role},
        ttl=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = JWTToken().create_token(
        {"user_id": user.id, "user_role": user.role},
        ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/only_auth", summary="Только для авторизованных пользователей")
async def get_only_auth(request: Request, access_token: UserIdDep):
    data = JWTToken().decode_token(request.cookies.get("access_token"))
    return data


@router.get("/me", summary="Получить информацию о пользователе")
async def get_me(user_id: UserIdDep, db: DBDep, access_token: UserIdDep):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post("/logout", summary="Выход")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"status": "ok"}


@router.post("/refresh", summary="Выпустить новую пару токенов")
async def refresh(response: Response, refresh_token: UserRefreshToken):
    """Обновление access token через refresh token из cookie"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Отсутствует рефреш токен"
        )

    try:
        payload = JWTToken().decode_token(refresh_token)
        user_id = JWTToken().validate_token_payload(payload, "user_id")
        user_role = JWTToken().validate_token_payload(payload, "user_role")

        response.delete_cookie(
            key="refresh_token",
        )

        new_access_token = JWTToken().create_token(
            {"user_id": user_id, "user_role": user_role},
            ttl=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        new_refresh_token = JWTToken().create_token(
            {"user_id": user_id, "user_role": user_role},
            ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )

        """Обновляем access и refresh token cookie"""
        set_auth_cookies(
            response, access_token=new_access_token, refresh_token=new_refresh_token
        )

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    except jwt.ExpiredSignatureError:
        response.delete_cookie("refresh_token")
        clear_auth_cookies(response)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Рефреш токен истек. Зайдите заново",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.put("/{user_id}/premium", summary="Обновить статус пользователя")
async def change_status_to_premium(
    db: DBDep, user_id: UserIdDep, access_token: UserIdDep
):
    if await UsersService(db).change_status_to_premium(user_id):
        return {"success": 200}

    else:
        raise HTTPException(
            status_code=409, detail="Вы не можете стать Private пользователем"
        )


@router.put("/verify/email/{user_email}")
async def verify_email(access_token: UserIdDep, user_code: int):
    payload = JWTToken().decode_token(access_token)

    user_email = JWTToken().validate_token_payload(payload, "user_email")

    verify_code = EmailSender().get_random_code_for_verify_email()

    await EmailSender().send_verify_code(code=verify_code, user_email=user_email)

    if user_code == verify_code:
        return {"success": 200}
    else:
        raise HTTPException(status_code=404, detail="Код неверный")
