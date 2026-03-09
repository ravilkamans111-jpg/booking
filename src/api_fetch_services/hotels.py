import asyncio
import logging
import aiohttp

from src.api_fetch_services.base import BaseAPIService


class HotelsHTTPClient(BaseAPIService):
    async def search_by_city(
        self, db, city: str, limit: int = 20, page: int = 1, base_url=None
    ):
        params = {"city": city, "limit": limit, "page": page}

        try:
            resp = await self.session.get(
                url=f"{base_url}/hotels/search", params=params, headers=self.headers
            )
            return await resp.json()

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as exc:
            logging.warning(exc)
            return await db.hotels.get_all()
