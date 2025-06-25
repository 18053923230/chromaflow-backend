# Start with an official Python base image
FROM python:3.9.23

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by Pillow or rembg's ONNX runtime
# libgomp1 is often needed for ONNX runtime with CPU
# Add other dependencies if rembg or Pillow complain (e.g., for specific image formats like WebP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    # libjpeg-dev zlib1g-dev libwebp-dev # Example for Pillow if needing more formats
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
RUN ls -R /app
RUN echo "Application code copied successfully."


# Expose the port the app runs on (FastAPI default is 8000 if not specified)
EXPOSE 8000

# The command to run the application (will be overridden by Render for the web service)
# For local testing, this can be the Uvicorn command.
# Render will use a different command for its web service and worker.
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# We will use a startup script for Render to be more flexible.