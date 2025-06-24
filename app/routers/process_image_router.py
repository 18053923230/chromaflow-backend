from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse # Or FileResponse if saving to disk
from app.tasks.image_processing_tasks import process_image_task
from app.schemas.image_schemas import ProcessImageRequest, TaskStatusResponse, TaskSubmitResponse, Operation
from celery.result import AsyncResult
from celery_app import celery_instance # Import your Celery app instance
import json
import io

router = APIRouter()

@router.post("/process", response_model=TaskSubmitResponse, status_code=202)
async def create_image_processing_task(
    image: UploadFile = File(...),
    # Operations sent as a JSON string in a form field.
    # This is a common way to send structured data alongside a file upload.
    operations_json: str = Form(...)
):
    """
    Accepts an image and a list of operations, then queues a processing task.
    The `operations_json` should be a JSON string representation of `List[Operation]`.
    Example for `operations_json` form field:
    '[{"type": "remove_background", "params": {}}, {"type": "resize", "params": {"width": 300}}]'
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    try:
        # Parse the JSON string for operations
        operations_data = json.loads(operations_json)
        # Validate with Pydantic (optional but good)
        # This step ensures the structure of operations_data is correct.
        # We are creating ProcessImageRequest just for validation here.
        _ = ProcessImageRequest(operations=[Operation(**op) for op in operations_data])
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for operations.")
    except Exception as e: # Catch Pydantic validation errors etc.
         raise HTTPException(status_code=400, detail=f"Invalid operations structure: {e}")


    image_bytes = await image.read()

    # Send task to Celery
    # Note: Celery tasks usually prefer primitive types as arguments.
    # Sending complex Pydantic models directly might require custom serializers.
    # Here, operations_data is a list of dicts, which is fine.
    task = process_image_task.delay(image_data=image_bytes, operations=operations_data)

    return TaskSubmitResponse(
        task_id=task.id,
        status="PENDING", # Or use task.status if it's immediately available
        message="Image processing task submitted successfully."
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the status and result of a Celery task.
    """
    # Use your Celery app instance to get the AsyncResult
    task_result = AsyncResult(task_id, app=celery_instance)

    response_data = {
        "task_id": task_id,
        "status": task_result.status,
    }

    if task_result.successful():
        processed_image_bytes = task_result.result # This is the raw bytes from the task
        # For MVP, we can consider returning the image directly if small enough,
        # or indicate where to download it.
        # Returning raw bytes in JSON is not ideal.
        # Option 1: Store and return URL (better for prod)
        # Option 2: Have a separate download endpoint
        # Option 3: For now, we'll just indicate success and let the client fetch via a download endpoint
        response_data["result"] = "Processing successful. Use download endpoint."
        # If you want to include progress metadata from update_state:
        if isinstance(task_result.info, dict):
            response_data.update(task_result.info)
        return TaskStatusResponse(**response_data)
    elif task_result.failed():
        response_data["result"] = str(task_result.info) # Error message
        return TaskStatusResponse(**response_data)
    else: # PENDING, STARTED, RETRY, PROGRESS
         # If you want to include progress metadata from update_state:
        if isinstance(task_result.info, dict):
            response_data.update(task_result.info)
        response_data["result"] = "Processing in progress or pending."
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
        raise HTTPException(status_code=500, detail="Task result is not image bytes.")

    # Determine media type - rembg output is PNG
    # If other operations can change format, this needs to be dynamic
    media_type = "image/png"
    return StreamingResponse(io.BytesIO(processed_image_bytes), media_type=media_type)