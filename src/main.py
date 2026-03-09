from pathlib import Path
from contextlib import asynccontextmanager
import logging

from prometheus_fastapi_instrumentator import Instrumentator

from redis.asyncio import Redis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Info
from src.rate_limiter import get_redis
from src.config import settings
from src.admin.admin_models import UserAdmin, HotelAdmin, RoomAdmin, BookingAdmin
from src.database import engine
from src.api.auth import router as auth_router
import uvicorn
from fastapi import FastAPI
from src.api.hotels import router as hotel_router
import sys
from src.api.rooms import router as rooms_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from sqladmin import Admin


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.redis.host, port=settings.redis.port, db=settings.redis.db.cache
    )

    try:
        rate_limit = get_redis()
        await rate_limit.ping()
        FastAPICache.init(RedisBackend(redis), prefix=settings.cache.prefix)
    except Exception as e:
        logging.error(f"Failed {e}")

    logging.info("Redis working")

    # startup
    # await bot(DeleteWebhook(drop_pending_updates=True))
    # asyncio.create_task(dp.start_polling(bot))
    yield
    # shutdown
    #     await bot.session.close()
    await redis.aclose()


sys.path.append(str(Path(__file__).parent.parent))


app = FastAPI(title="New Booking", lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

app_info = Info('fastapi_app', 'FastAPI application info')
app_info.info({'app_name': 'myapp'})

admin = Admin(app=app, engine=engine)
admin.add_view(UserAdmin)
admin.add_view(HotelAdmin)
admin.add_view(BookingAdmin)
admin.add_view(RoomAdmin)


app.include_router(router=auth_router)
app.include_router(router=hotel_router, tags=["Отели"])
app.include_router(router=rooms_router, tags=["Комнаты"])
app.include_router(router=bookings_router, tags=["Бронирования"])
app.include_router(router=facilities_router, tags=["Удобства"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost")

"Start uvicorn src.main:app --reload"
