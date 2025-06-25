print(">>>> process_image_router.py: SCRIPT EXECUTION STARTED (RESTORING STEP-BY-STEP) <<<<")
print("-----------------------------------------------------------------------------------")

# Step 1: Basic FastAPI imports
try:
    from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
    print(">>>> process_image_router.py: Successfully imported: APIRouter, File, UploadFile, Form, HTTPException, Depends from fastapi")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing basic FastAPI components: {e} XXXX")
    raise # Re-raise to see the error clearly if this fails

print("-----------------------------------------------------------------------------------")

# Step 2: StreamingResponse import
try:
    from fastapi.responses import StreamingResponse # Or FileResponse if saving to disk
    print(">>>> process_image_router.py: Successfully imported: StreamingResponse from fastapi.responses")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing StreamingResponse: {e} XXXX")
    raise

print("-----------------------------------------------------------------------------------")

# Step 3: Standard library imports
try:
    import json
    import io
    print(">>>> process_image_router.py: Successfully imported: json, io")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing json or io: {e} XXXX")
    raise

print("-----------------------------------------------------------------------------------")

# Step 4: Schemas import (Pydantic models)
# IMPORTANT: Ensure app/schemas/image_schemas.py itself has no problematic imports or top-level code
try:
    from app.schemas.image_schemas import ProcessImageRequest, TaskStatusResponse, TaskSubmitResponse, Operation
    print(">>>> process_image_router.py: Successfully imported: Schemas (ProcessImageRequest, etc.) from app.schemas.image_schemas")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing Schemas from app.schemas.image_schemas: {e} XXXX")
    print("XXXX Check app/schemas/image_schemas.py for issues! XXXX")
    raise

print("-----------------------------------------------------------------------------------")

# Step 5: Celery specific imports (AsyncResult and your app instance)
# IMPORTANT: Ensure celery_app.py itself has no problematic imports or top-level code
try:
    from celery.result import AsyncResult
    print(">>>> process_image_router.py: Successfully imported: AsyncResult from celery.result")
    from celery_app import celery_instance # Import your Celery app instance
    print(">>>> process_image_router.py: Successfully imported: celery_instance from celery_app")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing Celery components (AsyncResult or celery_instance): {e} XXXX")
    print("XXXX Check celery_app.py for issues! XXXX")
    raise

print("-----------------------------------------------------------------------------------")

# Step 6: THE MOST SUSPICIOUS IMPORT - Your Celery task
# IMPORTANT: This will trigger loading of app.tasks.image_processing_tasks,
# which in turn loads app.core.image_operations, which loads rembg.
# This is the most likely point of failure if rembg/ONNX causes issues on import/init.
try:
    from app.tasks.image_processing_tasks import process_image_task
    print(">>>> process_image_router.py: Successfully imported: process_image_task from app.tasks.image_processing_tasks")
    print(">>>> process_image_router.py: If rembg/ONNX loads models on import, this might take time or fail silently here on Render.")
except ImportError as e:
    print(f"XXXX process_image_router.py: ERROR importing process_image_task: {e} XXXX")
    print("XXXX This is a CRITICAL import. Check app/tasks/image_processing_tasks.py and its dependencies (app.core.image_operations, rembg). XXXX")
    raise
except Exception as e_runtime: # Catch other potential errors during import, like model loading issues
    print(f"XXXX process_image_router.py: UNEXPECTED RUNTIME ERROR during import of process_image_task: {e_runtime} XXXX")
    print("XXXX This might be rembg/ONNX model loading or initialization failing. XXXX")
    raise

print("-----------------------------------------------------------------------------------")

print(">>>> process_image_router.py: All planned imports attempted. Initializing APIRouter instance... <<<<")
router = APIRouter()
print(">>>> process_image_router.py: APIRouter instance CREATED. <<<<")
print("-----------------------------------------------------------------------------------")


# Temporarily keep all route definitions commented out until all imports are confirmed working on Render
# If all the above prints appear in Render logs AND the app starts successfully,
# then you can start uncommenting the route definitions one by one.

# @router.post("/process", response_model=TaskSubmitResponse, status_code=202)
# async def create_image_processing_task(
#     image: UploadFile = File(...),
#     operations_json: str = Form(...)
# ):
#     print(">>>> /process endpoint HIT <<<<") # Add print for when endpoint is called
#     if not image.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
#     try:
#         operations_data = json.loads(operations_json)
#         _ = ProcessImageRequest(operations=[Operation(**op) for op in operations_data])
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format for operations.")
#     except Exception as e:
#          raise HTTPException(status_code=400, detail=f"Invalid operations structure: {e}")
#     image_bytes = await image.read()
#     task = process_image_task.delay(image_data=image_bytes, operations=operations_data)
#     return TaskSubmitResponse(
#         task_id=task.id,
#         status="PENDING",
#         message="Image processing task submitted successfully."
#     )
# print(">>>> /process endpoint DEFINED. <<<<")

# @router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
# async def get_task_status(task_id: str):
#     print(f">>>> /tasks/{task_id} endpoint HIT <<<<")
#     task_result = AsyncResult(task_id, app=celery_instance)
#     response_data = {"task_id": task_id, "status": task_result.status}
#     if task_result.successful():
#         response_data["result"] = "Processing successful. Use download endpoint."
#         if isinstance(task_result.info, dict): response_data.update(task_result.info)
#     elif task_result.failed():
#         response_data["result"] = str(task_result.info)
#     else:
#         if isinstance(task_result.info, dict): response_data.update(task_result.info)
#         response_data["result"] = "Processing in progress or pending."
#     return TaskStatusResponse(**response_data)
# print(">>>> /tasks/{task_id} endpoint DEFINED. <<<<")


# @router.get("/tasks/{task_id}/download")
# async def download_processed_image(task_id: str):
#     print(f">>>> /tasks/{task_id}/download endpoint HIT <<<<")
#     task_result = AsyncResult(task_id, app=celery_instance)
#     if not task_result.successful():
#         raise HTTPException(status_code=404, detail=f"Task {task_id} not successful or not found. Status: {task_result.status}")
#     processed_image_bytes = task_result.result
#     if not isinstance(processed_image_bytes, bytes):
#         raise HTTPException(status_code=500, detail="Task result is not image bytes.")
#     media_type = "image/png"
#     return StreamingResponse(io.BytesIO(processed_image_bytes), media_type=media_type)
# print(">>>> /tasks/{task_id}/download endpoint DEFINED. <<<<")

print("===================================================================================")
print(">>>> process_image_router.py: SCRIPT EXECUTION FINISHED (ALL IMPORTS ATTEMPTED, ROUTES COMMENTED) <<<<")
print("===================================================================================")