# chromaflow_backend/app/routers/process_image_router.py

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.schemas.image_schemas import ProcessImageRequest, TaskStatusResponse, TaskSubmitResponse, Operation
from celery.result import AsyncResult
from celery_app import celery_instance # Assuming celery_app.py is correctly configured
from app.tasks.image_processing_tasks import process_image_task # Assuming this now uses delayed loading for rembg

import json
import io

router = APIRouter()

@router.post("/process", response_model=TaskSubmitResponse, status_code=202)
async def create_image_processing_task(
    image: UploadFile = File(...),
    operations_json: str = Form(...)
):
    """
    Accepts an image and a list of operations, then queues a processing task.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

    try:
        operations_data = json.loads(operations_json)
        # Validate operations structure using Pydantic (implicitly via ProcessImageRequest)
        # Create a list of Operation Pydantic models for validation and use
        validated_operations = [Operation(**op) for op in operations_data]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for operations.")
    except Exception as e: # Catches Pydantic validation errors and other unexpected errors
         raise HTTPException(status_code=400, detail=f"Invalid operations structure: {str(e)}")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image data is empty.")

    # Send task to Celery. operations_data is a list of dicts, which is fine.
    # If validated_operations is preferred, ensure it's converted back to list of dicts if Celery task expects that.
    # For now, using operations_data as it was before validation logic was made more explicit.
    task = process_image_task.delay(image_data=image_bytes, operations=operations_data)

    return TaskSubmitResponse(
        task_id=task.id,
        status="PENDING", # Celery task status is PENDING immediately after .delay()
        message="Image processing task submitted successfully."
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the status and result of a Celery task.
    """
    task_result = AsyncResult(task_id, app=celery_instance)

    response_data = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None, # Default result to None
        "current_step": None,
        "total_steps": None,
        "operation": None,
    }

    if isinstance(task_result.info, dict): # For progress updates or custom metadata
        response_data.update(task_result.info)

    if task_result.successful():
        # Result from successful task. For image bytes, we don't put them here directly.
        response_data["result"] = "Processing successful. Use download endpoint."
    elif task_result.failed():
        response_data["result"] = f"Task failed: {str(task_result.info)}" # Error message/traceback
    elif task_result.status == 'PENDING':
        response_data["result"] = "Task is pending."
    elif task_result.status == 'STARTED':
        response_data["result"] = "Task has started."
    elif task_result.status == 'RETRY':
        response_data["result"] = f"Task is being retried: {str(task_result.info)}"
    # PROGRESS status is usually handled by the task_result.info dict update above

    return TaskStatusResponse(**response_data)


@router.get("/tasks/{task_id}/download")
async def download_processed_image(task_id: str):
    """
    Downloads the processed image if the task was successful.
    """
    task_result = AsyncResult(task_id, app=celery_instance)

    if not task_result.successful():
        raise HTTPException(status_code=404, detail=f"Task {task_id} not successful or not found. Status: {task_result.status}")

    processed_image_bytes = task_result.result
    if not isinstance(processed_image_bytes, bytes):
        # This could happen if the task returned something else, or if the result backend misbehaved
        raise HTTPException(status_code=500, detail="Task result is not valid image bytes.")

    # Assuming rembg output is PNG by default due to transparency.
    # If format can change via operations, this media_type needs to be dynamic.
    media_type = "image/png"
    return StreamingResponse(io.BytesIO(processed_image_bytes), media_type=media_type)