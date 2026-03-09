from pydantic import BaseModel
from sqlalchemy import select, insert, desc, asc, update
from sqlalchemy.exc import IntegrityError
import logging

from src.exceptions import ObjectIsAlreadyExistsException
from src.repos.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, limit: int = 100, offset: int = 0):
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity_pyd(model)
            for model in result.scalars().all()
        ]

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, data: BaseModel):
        try:
            add_data_stmt = (
                insert(self.model).values(**data.model_dump()).returning(self.model)
            )
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()

        except IntegrityError:
            raise ObjectIsAlreadyExistsException

        except Exception as ex:
            logging.error(f"Пользователь: {data}. Ошибка: {ex}")
            raise
        return self.mapper.map_to_domain_entity_pyd(model)

    async def get_one_or_none(self, **filters):
        stmt = select(self.model).filter_by(**filters)
        model = await self.session.execute(stmt)
        return self.mapper.map_to_domain_entity_pyd(model.scalar_one_or_none())

    async def get_sorted(self, field: str, direction: str = "desc"):
        column = getattr(self.model, field)

        stmt = select(self.model)

        if direction == "desc":
            stmt = stmt.order_by(desc(column))
        else:
            stmt = stmt.order_by(asc(column))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, obj_id: int, **data):
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()

    async def delete(self, obj_id: int):
        obj = await self.session.get(self.model, obj_id)
        if not obj:
            return False

        await self.session.delete(obj)
        return True
