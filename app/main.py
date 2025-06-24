from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="ChromaFlow Studio API",
    description="API for image processing workflows.",
    version="0.1.0"
)

# Import and include your new router
from .routers import process_image_router # Make sure this path is correct

app.include_router(process_image_router.router, prefix="/api/v1", tags=["Image Processing"])


@app.get("/")
async def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Welcome to ChromaFlow Studio API!"}

# Remove or comment out the uvicorn.run for production/docker
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)