from celery_app import celery_instance
from app.core.image_operations import remove_background_core, resize_image_core # Import your core functions
import time
import io

# Keep the add task for basic Celery testing if you like
@celery_instance.task(name="add_numbers_task")
def add(x, y):
    time.sleep(1) # Reduced sleep for faster testing
    return x + y

@celery_instance.task(name="process_image_task", bind=True) # bind=True gives access to `self` (the task instance)
def process_image_task(self, image_data: bytes, operations: list):
    """
    Celery task to process an image through a series of operations.
    For MVP, we'll start with just background removal.
    Args:
        image_data: The raw image bytes.
        operations: A list of operation dicts, e.g.,
                    [
                        {"type": "remove_background", "params": {}},
                        {"type": "resize", "params": {"width": 500}},
                        # ... more operations
                    ]
    Returns:
        The processed image bytes.
    """
    current_image_bytes = image_data
    total_steps = len(operations)

    for i, operation in enumerate(operations):
        op_type = operation.get("type")
        params = operation.get("params", {})
        print(f"Executing operation: {op_type} with params: {params}")

        # Update task state for progress (optional but good for UX)
        self.update_state(state='PROGRESS', meta={'current_step': i + 1, 'total_steps': total_steps, 'operation': op_type})

        if op_type == "remove_background":
            current_image_bytes = remove_background_core(current_image_bytes)
        elif op_type == "resize":
            current_image_bytes = resize_image_core(current_image_bytes, **params)
        # Add more elif blocks for other operations (convert_format, change_background_color, etc.)
        # e.g.,
        # elif op_type == "convert_format":
        #     current_image_bytes = convert_format_core(current_image_bytes, **params)
        else:
            print(f"Unknown operation type: {op_type}")
            # Optionally raise an error or skip
            raise ValueError(f"Unknown operation type: {op_type}")

    return current_image_bytes # Celery will serialize this (e.g., to Base64 if bytes)
                                # or you can store it and return a URL.
                                # For MVP, returning bytes is fine if they aren't too large.