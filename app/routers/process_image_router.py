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

# app/routers/process_image_router.py
@router.post("/process", response_model=TaskSubmitResponse, status_code=202)
async def create_image_processing_task(
    image: UploadFile = File(...),
    operations_json: str = Form(...)
):
    print(">>>> /api/v1/process: create_image_processing_task ENTERED <<<<")
    try:
        print(f"DEBUG: image.filename = {image.filename}, image.content_type = {image.content_type}")

        if not image.content_type or not image.content_type.startswith("image/"):
            print("XXXX ERROR: Invalid image content_type XXXX")
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
        print("DEBUG: image content_type check PASSED.")

        operations_data = json.loads(operations_json)
        print(f"DEBUG: operations_data parsed: {operations_data}")

        validated_operations = [Operation(**op) for op in operations_data]
        print(f"DEBUG: operations validated by Pydantic: {validated_operations}")

        image_bytes = await image.read()
        if not image_bytes:
            print("XXXX ERROR: Image data is empty XXXX")
            raise HTTPException(status_code=400, detail="Image data is empty.")
        print(f"DEBUG: image_bytes read, length: {len(image_bytes)}")

        print("DEBUG: About to send task to Celery...")
        task = process_image_task.delay(image_data=image_bytes, operations=operations_data)
        print(f"DEBUG: Celery task sent, task_id: {task.id}")

        response = TaskSubmitResponse(
            task_id=task.id,
            status="PENDING",
            message="Image processing task submitted successfully."
        )
        print(f"DEBUG: Returning response: {response}")
        return response
    except HTTPException as http_exc: # Re-raise HTTPExceptions directly
        print(f"XXXX HTTPException in /process: {http_exc.status_code} - {http_exc.detail} XXXX")
        raise http_exc
    except json.JSONDecodeError as json_err:
        print(f"XXXX JSONDecodeError in /process: {json_err} XXXX")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format for operations: {str(json_err)}")
    except Exception as e: # Catch any other unexpected errors
        import traceback
        print("XXXX UNEXPECTED ERROR in /process endpoint: XXXX")
        print(traceback.format_exc()) # Print full traceback to logs
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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