from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery_tasks import add_numbers, long_running_task, process_data, send_notification
from celery_app import celery_app
from typing import Any

router = APIRouter()

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class ProcessDataRequest(BaseModel):
    data: dict

class NotificationRequest(BaseModel):
    user_id: str
    message: str

@router.post("/add", response_model=TaskResponse)
async def add_task(x: int, y: int):
    """Trigger an add numbers task."""
    task = add_numbers.delay(x, y)
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message=f"Task started to add {x} + {y}"
    )

@router.post("/long-task", response_model=TaskResponse)
async def start_long_task(duration: int = 10):
    """Start a long-running task."""
    task = long_running_task.delay(duration)
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message=f"Long running task started for {duration} seconds"
    )

@router.post("/process-data", response_model=TaskResponse)
async def process_data_task(request: ProcessDataRequest):
    """Process data asynchronously."""
    task = process_data.delay(request.data)
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message="Data processing task started"
    )

@router.post("/send-notification", response_model=TaskResponse)
async def send_notification_task(request: NotificationRequest):
    """Send notification asynchronously."""
    task = send_notification.delay(request.user_id, request.message)
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message=f"Notification task started for user {request.user_id}"
    )

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a task."""
    try:
        task = celery_app.AsyncResult(task_id)
        if task.state == "PENDING":
            return {
                "task_id": task_id,
                "status": "PENDING",
                "message": "Task is waiting to be processed"
            }
        elif task.state == "PROGRESS":
            return {
                "task_id": task_id,
                "status": "PROGRESS",
                "message": "Task is being processed",
                "progress": task.info
            }
        elif task.state == "SUCCESS":
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "message": "Task completed successfully",
                "result": task.result
            }
        else:  # FAILURE
            return {
                "task_id": task_id,
                "status": "FAILURE",
                "message": "Task failed",
                "error": str(task.info)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")

@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": "Task has been cancelled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}") 