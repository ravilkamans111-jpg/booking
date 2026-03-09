from src.services.base import BaseService


class FacilitiesService(BaseService):
    async def create_facility(self, facility):
        result = await self.db.facilities.add(facility)
        await self.db.commit()
        return result
