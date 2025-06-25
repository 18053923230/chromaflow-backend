print(">>>> image_processing_tasks.py: SCRIPT EXECUTION STARTED <<<<") # 新增
print("---------------------------------------------------------------")

print(">>>> image_processing_tasks.py: About to import celery_app...") # 新增
try:
    from celery_app import celery_instance
    print(">>>> image_processing_tasks.py: celery_instance IMPORTED.") # 新增
except Exception as e:
    print(f"XXXX image_processing_tasks.py: ERROR importing celery_instance: {e} XXXX")
    raise
print("---------------------------------------------------------------")

print(">>>> image_processing_tasks.py: About to import image_operations core functions...") # 新增
# 这是关键的导入，它会间接导入 rembg
try:
    from app.core.image_operations import remove_background_core, resize_image_core
    print(">>>> image_processing_tasks.py: core image_operations (remove_background_core, etc.) IMPORTED.") # 新增
    print(">>>> image_processing_tasks.py: This implies rembg was successfully imported by image_operations.py.")
except ImportError as e_imp:
    print(f"XXXX image_processing_tasks.py: IMPORT ERROR importing from app.core.image_operations: {e_imp} XXXX")
    print("XXXX Check app.core.image_operations.py and its imports (especially rembg). XXXX")
    raise
except Exception as e_runtime_ops:
    print(f"XXXX image_processing_tasks.py: RUNTIME ERROR importing from app.core.image_operations: {e_runtime_ops} XXXX")
    print("XXXX This could be rembg/ONNX initialization failure within image_operations.py. XXXX")
    raise
print("---------------------------------------------------------------")

# ... (你原来的 add 任务可以保留或注释掉) ...
# @celery_instance.task(name="add_numbers_task")
# def add(x, y): ...

print(">>>> image_processing_tasks.py: About to define process_image_task...") # 新增
@celery_instance.task(name="process_image_task", bind=True)
def process_image_task(self, image_data: bytes, operations: list):
    print(f">>>> process_image_task: Task {self.request.id} STARTED with {len(operations)} operations.") # 新增
    current_image_bytes = image_data
    total_steps = len(operations)

    for i, operation in enumerate(operations):
        op_type = operation.get("type")
        params = operation.get("params", {})
        print(f">>>> process_image_task {self.request.id}: Executing op {i+1}/{total_steps} - {op_type} with params: {params}") # 新增

        self.update_state(state='PROGRESS', meta={'current_step': i + 1, 'total_steps': total_steps, 'operation': op_type})

        if op_type == "remove_background":
            print(f">>>> process_image_task {self.request.id}: Calling remove_background_core...") # 新增
            current_image_bytes = remove_background_core(current_image_bytes)
            print(f">>>> process_image_task {self.request.id}: remove_background_core FINISHED.") # 新增
        elif op_type == "resize":
            # ... (类似的 print 语句)
            current_image_bytes = resize_image_core(current_image_bytes, **params)
        else:
            print(f"XXXX process_image_task {self.request.id}: Unknown operation type: {op_type} XXXX")
            raise ValueError(f"Unknown operation type: {op_type}")
    
    print(f">>>> process_image_task: Task {self.request.id} FINISHED successfully.") # 新增
    return current_image_bytes
print(">>>> image_processing_tasks.py: process_image_task DEFINED.") # 新增
print("---------------------------------------------------------------")
print(">>>> image_processing_tasks.py: SCRIPT EXECUTION FINISHED <<<<") # 新增