# chromaflow_backend/app/main.py

import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file for local development.
# On Render, environment variables are set via the dashboard.
# This call is generally safe; if .env is not found, it does nothing.
load_dotenv()

app = FastAPI(
    title="ChromaFlow Studio API",
    description="API for image processing workflows.",
    version="0.1.0",
    # You might want to add other FastAPI configurations here,
    # e.g., docs_url, redoc_url, openapi_url, root_path (if behind a proxy)
)

# Import and include your API router(s)
try:
    from .routers import process_image_router
    app.include_router(
        process_image_router.router,
        prefix="/api/v1",
        tags=["Image Processing"]
    )
except ImportError as e:
    # Log this error more formally in a real application
    # For now, a print to stderr might be visible in Render logs if startup fails here
    import sys
    print(f"FATAL ERROR: Could not import or include process_image_router: {e}", file=sys.stderr)
    # Depending on the severity, you might want the application to exit
    # raise RuntimeError(f"Failed to setup API routers: {e}") from e

@app.get("/", tags=["Health Check"])
async def read_root_health_check():
    """
    Root endpoint for health check.
    Render uses this (by default) to determine if the service is live.
    """
    return {"status": "healthy", "message": "Welcome to ChromaFlow Studio API!"}

# The following block is for local development only using `python app/main.py`.
# It should be commented out or removed for production when Uvicorn is run directly
# by a process manager or a PaaS like Render.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app", # Or just "main:app" if main.py is in the root of where uvicorn runs
#         host="0.0.0.0",
#         port=int(os.getenv("PORT", 8000)), # Use PORT from env if available, else default
#         reload=os.getenv("DEV_MODE", "false").lower() == "true" # Enable reload only in dev
#     )