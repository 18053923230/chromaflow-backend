
try:
    from PIL import Image
    import io
    
except Exception as e:
    print(f"XXXX image_operations.py: ERROR importing Pillow or io: {e} XXXX")
    raise


# 不要在这里直接 from rembg import remove

_rembg_remove_func = None # 全局缓存加载后的函数

def get_rembg_remove_func():
    global _rembg_remove_func
    if _rembg_remove_func is None:
        
        try:
            from rembg import remove as actual_rembg_remove
            _rembg_remove_func = actual_rembg_remove
            
        except Exception as e:
            print(f"XXXX image_operations.py: ERROR during LAZY LOADING of rembg: {e} XXXX")
            raise
    return _rembg_remove_func



def remove_background_core(image_bytes: bytes) -> bytes:
    
    rembg_remove = get_rembg_remove_func() # 在函数调用时才获取/加载
    if not rembg_remove:
        raise RuntimeError("rembg function could not be loaded.")
    try:
        input_image = Image.open(io.BytesIO(image_bytes))
        
        output_image = rembg_remove(input_image) # Using the renamed import
        

        byte_arr = io.BytesIO()
        output_image.save(byte_arr, format='PNG')
        
        return byte_arr.getvalue()
    except Exception as e:
        print(f"XXXX remove_background_core: ERROR during background removal: {e} XXXX")
        # Consider logging the full traceback here for more details
        import traceback
        print(traceback.format_exc())
        raise


def resize_image_core(image_bytes: bytes, width: int = None, height: int = None, keep_aspect_ratio: bool = True) -> bytes:
     
     return image_bytes # 假设返回，你需要填充逻辑
