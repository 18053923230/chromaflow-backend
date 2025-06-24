from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OperationParams(BaseModel):
    # Define specific parameters for each operation type for better validation
    # For now, allow any additional params
    width: Optional[int] = Field(None, description="Target width for resize")
    height: Optional[int] = Field(None, description="Target height for resize")
    keep_aspect_ratio: Optional[bool] = Field(True, description="Keep aspect ratio for resize")
    # format: Optional[str] = Field(None, description="Target format for conversion (e.g., 'PNG', 'JPEG')")
    # background_color: Optional[str] = Field(None, description="Hex color for background change (e.g., '#FFFFFF')")
    # background_image_url: Optional[str] = Field(None, description="URL of image to use as background")

    # Allow other parameters for flexibility initially, refine later
    class Config:
        extra = "allow"


class Operation(BaseModel):
    type: str = Field(..., description="Type of operation (e.g., 'remove_background', 'resize')")
    params: Optional[OperationParams] = Field(default_factory=OperationParams, description="Parameters for the operation")


class ProcessImageRequest(BaseModel):
    operations: List[Operation] = Field(..., description="List of operations to perform in sequence")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None # Could be URL to image, or base64 encoded for MVP
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    operation: Optional[str] = None


class TaskSubmitResponse(BaseModel):
    task_id: str
    status: str
    message: str