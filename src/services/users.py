from src.services.base import BaseService


class UsersService(BaseService):
    async def change_status_to_premium(self, user_id: int) -> bool:
        user_bookings = await self.db.bookings.get_filtered(user_id=user_id)

        if len(user_bookings) >= 5:
            await self.db.users.update(obj_id=user_id, status="premium")
            return True
        else:
            return False
