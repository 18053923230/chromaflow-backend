print(">>>> image_operations.py: SCRIPT EXECUTION STARTED <<<<") # 新增
print("-------------------------------------------------------")

print(">>>> image_operations.py: About to import Pillow (Image) and io...") # 新增
try:
    from PIL import Image
    import io
    print(">>>> image_operations.py: Pillow (Image) and io IMPORTED.") # 新增
except Exception as e:
    print(f"XXXX image_operations.py: ERROR importing Pillow or io: {e} XXXX")
    raise
print("-------------------------------------------------------")


print(">>>> image_operations.py: About to import rembg...") # 新增
# 这是最关键的导入
try:
    from rembg import remove as rembg_remove # Rename to avoid conflict if 'remove' is used elsewhere
    print(">>>> image_operations.py: rembg (and its 'remove' function) IMPORTED SUCCESSFULLY.") # 新增
    print(">>>> image_operations.py: If rembg loads models now, this might be slow or fail on Render.")
except ImportError as e_imp_rembg:
    print(f"XXXX image_operations.py: IMPORT ERROR importing rembg: {e_imp_rembg} XXXX")
    raise
except Exception as e_runtime_rembg:
    print(f"XXXX image_operations.py: RUNTIME ERROR during rembg import/init: {e_runtime_rembg} XXXX")
    print("XXXX This is highly indicative of rembg/ONNX failing on Render. XXXX")
    raise
print("-------------------------------------------------------")


print(">>>> image_operations.py: About to define remove_background_core...") # 新增
def remove_background_core(image_bytes: bytes) -> bytes:
    print(">>>> remove_background_core: Function CALLED.") # 新增
    try:
        input_image = Image.open(io.BytesIO(image_bytes))
        print(">>>> remove_background_core: Input image opened with Pillow.") # 新增
        
        print(">>>> remove_background_core: Calling rembg_remove()... THIS IS THE CPU/MEMORY INTENSIVE STEP.") # 新增
        output_image = rembg_remove(input_image) # Using the renamed import
        print(">>>> remove_background_core: rembg_remove() FINISHED.") # 新增

        byte_arr = io.BytesIO()
        output_image.save(byte_arr, format='PNG')
        print(">>>> remove_background_core: Output image saved to bytes (PNG).") # 新增
        return byte_arr.getvalue()
    except Exception as e:
        print(f"XXXX remove_background_core: ERROR during background removal: {e} XXXX")
        # Consider logging the full traceback here for more details
        import traceback
        print(traceback.format_exc())
        raise
print(">>>> image_operations.py: remove_background_core DEFINED.") # 新增
print("-------------------------------------------------------")

# ... (你的 resize_image_core 和其他函数也类似地加入 print) ...
def resize_image_core(image_bytes: bytes, width: int = None, height: int = None, keep_aspect_ratio: bool = True) -> bytes:
     print(">>>> resize_image_core: Function CALLED.")
     # ... (内部逻辑)
     print(">>>> resize_image_core: Function FINISHED.")
     return image_bytes # 假设返回，你需要填充逻辑
print(">>>> image_operations.py: resize_image_core DEFINED.")

print("-------------------------------------------------------")
print(">>>> image_operations.py: SCRIPT EXECUTION FINISHED <<<<") # 新增