from pydantic import BaseModel, EmailStr, ConfigDict

from src.permisions import UserRole


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = "user"
    status: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str
    role: UserRole
    status: str


class User(UserAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    status: str

    model_config = ConfigDict(from_attributes=True)
