from pydantic import BaseModel


class FavouritesSchema(BaseModel):
    id: int
    hotel_id: int
    user_id: int


class FavouritesAdd(BaseModel):
    hotel_id: int
    user_id: int


class FavouritesRead(BaseModel):
    hotel_id: int
