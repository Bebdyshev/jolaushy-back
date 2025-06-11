from celery_app import celery_app
from config import redis_client
import time
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def add_numbers(x: int, y: int) -> int:
    """Simple example task that adds two numbers."""
    logger.info(f"Adding {x} + {y}")
    return x + y

@celery_app.task
def long_running_task(duration: int = 10) -> str:
    """Example of a long-running task."""
    logger.info(f"Starting long running task for {duration} seconds")
    time.sleep(duration)
    logger.info("Long running task completed")
    return f"Task completed after {duration} seconds"

@celery_app.task
def process_data(data: dict) -> dict:
    """Example task for processing data."""
    logger.info(f"Processing data: {data}")
    
    # Example processing logic
    processed_data = {
        "original": data,
        "processed": True,
        "timestamp": time.time()
    }
    
    # Store in Redis cache if needed
    redis_client.setex(f"processed_data_{data.get('id', 'unknown')}", 3600, str(processed_data))
    
    logger.info("Data processing completed")
    return processed_data

@celery_app.task
def send_notification(user_id: str, message: str) -> bool:
    """Example task for sending notifications."""
    logger.info(f"Sending notification to user {user_id}: {message}")
    
    # Here you would integrate with your notification service
    # For now, we'll just log it and store in Redis
    notification_key = f"notification_{user_id}_{time.time()}"
    redis_client.setex(notification_key, 86400, message)  # Store for 24 hours
    
    logger.info(f"Notification sent to user {user_id}")
    return True 