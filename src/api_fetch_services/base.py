import aiohttp


class BaseAPIService:
    def __init__(self, retries=3, api_key=None):
        self.__api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        self.retries = retries
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()
