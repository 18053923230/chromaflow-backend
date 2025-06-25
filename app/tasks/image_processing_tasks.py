
try:
    from celery_app import celery_instance
    
except Exception as e:
    print(f"XXXX image_processing_tasks.py: ERROR importing celery_instance: {e} XXXX")
    raise



try:
    from app.core.image_operations import remove_background_core, resize_image_core
    
except ImportError as e_imp:
    print(f"XXXX image_processing_tasks.py: IMPORT ERROR importing from app.core.image_operations: {e_imp} XXXX")
    print("XXXX Check app.core.image_operations.py and its imports (especially rembg). XXXX")
    raise
except Exception as e_runtime_ops:
    print(f"XXXX image_processing_tasks.py: RUNTIME ERROR importing from app.core.image_operations: {e_runtime_ops} XXXX")
    print("XXXX This could be rembg/ONNX initialization failure within image_operations.py. XXXX")
    raise



@celery_instance.task(name="process_image_task", bind=True)
def process_image_task(self, image_data: bytes, operations: list):
    
    current_image_bytes = image_data
    total_steps = len(operations)

    for i, operation in enumerate(operations):
        op_type = operation.get("type")
        params = operation.get("params", {})
        

        self.update_state(state='PROGRESS', meta={'current_step': i + 1, 'total_steps': total_steps, 'operation': op_type})

        if op_type == "remove_background":
            
            current_image_bytes = remove_background_core(current_image_bytes)
            
        elif op_type == "resize":
            
            current_image_bytes = resize_image_core(current_image_bytes, **params)
        else:
            
            raise ValueError(f"Unknown operation type: {op_type}")
    
    print(f">>>> process_image_task: Task {self.request.id} FINISHED successfully.") # 新增
    return current_image_bytes
