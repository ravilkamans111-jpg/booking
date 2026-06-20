from pathlib import Path
from contextlib import asynccontextmanager
import logging.config

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
from fastapi import FastAPI, Request
from src.api.hotels import router as hotel_router
import sys
import time
from src.api.rooms import router as rooms_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from sqladmin import Admin


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Application startup — initialising resources")

    redis = Redis(
        host=settings.redis.host, port=settings.redis.port, db=settings.redis.db.cache
    )
    logger.debug(
        "Redis connection params: host=%s port=%s db=%s",
        settings.redis.host,
        settings.redis.port,
        settings.redis.db.cache,
    )

    try:
        rate_limit = get_redis()
        await rate_limit.ping()
        logger.info("Redis rate-limit connection: OK")
        FastAPICache.init(RedisBackend(redis), prefix=settings.cache.prefix)
        logger.info("FastAPI cache initialised (prefix=%s)", settings.cache.prefix)
    except Exception as e:
        logger.error("Failed to initialise Redis / cache: %s", e, exc_info=True)

    # startup
    # await bot(DeleteWebhook(drop_pending_updates=True))
    # asyncio.create_task(dp.start_polling(bot))
    logger.info("Application startup complete")
    yield
    # shutdown
    #     await bot.session.close()
    logger.info("Application shutdown — closing Redis connection")
    await redis.aclose()
    logger.info("Redis connection closed")


sys.path.append(str(Path(__file__).parent.parent))


app = FastAPI(title="New Booking", lifespan=lifespan)

Instrumentator().instrument(app).expose(app)
logger.debug("Prometheus Instrumentator attached")

app_info = Info("fastapi_app", "FastAPI application info")
app_info.info({"app_name": "myapp"})

admin = Admin(app=app, engine=engine)
admin.add_view(UserAdmin)
admin.add_view(HotelAdmin)
admin.add_view(BookingAdmin)
admin.add_view(RoomAdmin)
logger.debug("Admin panel views registered")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("→ %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled exception during %s %s", request.method, request.url.path)
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "← %s %s  status=%d  %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(router=auth_router)
app.include_router(router=hotel_router, tags=["Отели"])
app.include_router(router=rooms_router, tags=["Комнаты"])
app.include_router(router=bookings_router, tags=["Бронирования"])
app.include_router(router=facilities_router, tags=["Удобства"])
logger.debug("All routers registered")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("CORS middleware added")


if __name__ == "__main__":
    logger.info("Starting uvicorn on localhost")
    uvicorn.run(app, host="localhost")

"Start uvicorn src.main:app --reload"
