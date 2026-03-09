from fastapi import HTTPException


class BronException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectIsAlreadyExistsException(BronException):
    detail = "Похожий объект уже существует"


class ObjectHasNotInformation(BronException):
    detail = "Данного объекта не существует"


class RoomAlreadyBooked(HTTPException):
    detail = "Комната не может быть забронирована"


class IsNotBookingOfThisClient(BronException):
    detail = "Данного бронирования не существует"


class DateFromCantBeAfterDateTo(BronException):
    detail = "Дата заезда не может быть позднее даты выезда"
