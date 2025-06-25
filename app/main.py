from fastapi import FastAPI
from dotenv import load_dotenv
import os
print("==============================================")
print("STARTING app/main.py execution...")
print(f"Current Python version (from os.sys.version): {os.sys.version}") # 打印 Python 版本
print(f"Current Working Directory: {os.getcwd()}")
try:
    print(f"Listing files in CWD: {os.listdir('.')}")
except Exception as e:
    print(f"Error listing CWD files: {e}")
print("==============================================")

import os # os 已在上面导入，但确保它在 load_dotenv 前
from fastapi import FastAPI
from dotenv import load_dotenv

print("Core modules (os, FastAPI, dotenv) imported.")
print("----------------------------------------------")

print("Attempting to load dotenv (will be ignored on Render if .env not present)...")
try:
    load_dotenv()
    print("dotenv loaded (or skipped if .env not found).")
except Exception as e:
    print(f"Error during load_dotenv: {e}")
print("----------------------------------------------")


print("Initializing FastAPI app instance...")
try:
    app = FastAPI(
        title="ChromaFlow Studio API",
        description="API for image processing workflows.",
        version="0.1.0"
    )
    print("FastAPI app instance INITIALIZED successfully.")
except Exception as e:
    print(f"CRITICAL ERROR during FastAPI app initialization: {e}")
    # 如果 FastAPI 初始化失败，后续代码可能无法执行或意义不大
    # 可以在这里 raise e 来中断，或者让它继续尝试加载路由看是否还有其他错误
print("----------------------------------------------")

# Import and include your new router
print("Attempting to import process_image_router from .routers...")
try:
    from .routers import process_image_router # Make sure this path is correct
    print("process_image_router IMPORTED successfully.")

    print("Attempting to include process_image_router into app...")
    app.include_router(process_image_router.router, prefix="/api/v1", tags=["Image Processing"])
    print("process_image_router INCLUDED successfully.")
except ImportError as e_import:
    print(f"ERROR importing or including process_image_router: {e_import}")
    print("Check if '.routers.process_image_router' exists and has no import errors itself.")
except Exception as e_include:
    print(f"UNEXPECTED ERROR during router import/include: {e_include}")
print("----------------------------------------------")


print("Defining root health check endpoint ('/') ...")
@app.get("/")
async def read_root():
    """
    Root endpoint for health check.
    """
    print(">>>> HEALTH CHECK ENDPOINT ('/') WAS HIT! <<<<") # 非常明显的标记
    return {"message": "Welcome to ChromaFlow Studio API! Health check successful."}
print("Root health check endpoint DEFINED.")
print("----------------------------------------------")

# The uvicorn.run block for local development should remain commented out for Render.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

print("==============================================")
print("END OF app/main.py initial setup script.")
print("Uvicorn should now take over and start serving the application.")
print("Waiting for Uvicorn to log its 'Application startup complete' message...")
print("==============================================")