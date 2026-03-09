from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.redis.REDIS_URL,
    include=["src.tasks.tasks"],
)

celery_instance.conf.beat_schedule = {
    "beats": {"task": "booking_today_check_in", "schedule": crontab(minute="*")}
}

# celery -A src.tasks.celery_app:celery_instance worker --loglevel=info
# celery -A src.tasks.celery_app:celery_instance beat --loglevel=info
