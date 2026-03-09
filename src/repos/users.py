from sqlalchemy import select
from src.schemas.auth import User
from src.models.users import UserOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import UserDataMapper


class UserRepository(BaseRepository):
    model = UserOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, **filters):
        stmt = select(self.model).filter_by(**filters)
        model = await self.session.execute(stmt)
        result = model.scalar_one_or_none()
        return User.model_validate(result)
