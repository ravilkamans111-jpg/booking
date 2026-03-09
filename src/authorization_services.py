from datetime import datetime, timezone, timedelta
from src.config import settings
from pwdlib import PasswordHash
import jwt
from fastapi import HTTPException, status


class AuthorizationServices:
    password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.password_hash.hash(password)


class JWTToken:
    def create_token(self, data: dict, ttl: int):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ttl)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def decode_token(self, token: str):
        return jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

    def validate_token_payload(self, payload: dict, info: str):
        user_info = payload.get(info)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
            )
        return user_info

    def validate_user_role_payload(self, token):
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        role = payload.get("user_role")
        if role not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа"
            )
        return True
