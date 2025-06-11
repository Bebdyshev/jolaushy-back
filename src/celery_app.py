from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "jolaushy-back",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)

if __name__ == "__main__":
    celery_app.start() 