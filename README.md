``

# ChromaFlow Studio Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Add other badges if you like: build status, version, etc. -->

ChromaFlow Studio Backend is a Python-based API designed for orchestrating image processing workflows. It allows users to upload an image and apply a series of operations like background removal, resizing, and format conversion through a flexible, task-based architecture using FastAPI and Celery.

**Live Demo (Backend API - Replace with your Render URL if you want to share it, or remove if backend is not meant for direct public access without a frontend):**
`https://your-chromaflow-api.onrender.com` (Example: Health check at `/`)

**Project Repository:** `git@github.com:18053923230/chromaflow-backend.git` (or use HTTPS link for easier cloning: `https://github.com/18053923230/chromaflow-backend.git`)

## Features

* **Image Upload:** Accepts image files for processing.
* **Workflow-driven Processing:** Define a sequence of operations to apply to an image.
* **Core Image Operations (MVP):**
  * **Background Removal:** Utilizes the `rembg` library for AI-powered background removal.
  * **Resizing:** Adjust image dimensions while optionally maintaining aspect ratio.
  * *(Future: Format Conversion, Background Change, Filters, etc.)*
* **Asynchronous Task Processing:** Leverages Celery and Redis to handle potentially long-running image operations without blocking API requests.
* **Modern Python Stack:** Built with FastAPI for high-performance API development and Pydantic for data validation.
* **Dockerized:** Ready for containerized deployment.
* **Cloud-Native Deployment:** Designed and tested for deployment on platforms like Render.

## Tech Stack

* **Backend Framework:** FastAPI
* **Task Queue:** Celery
* **Message Broker & Result Backend:** Redis
* **Image Processing:** Pillow, `rembg`
* **ASGI Server:** Uvicorn
* **Containerization:** Docker
* **Deployment Platform (Example):** Render

## Project Structure

**chromaflow\_backend/**
├── app/ # Main application code
│ ├── core/ # Core image processing logic
│ ├── routers/ # API endpoint definitions
│ ├── schemas/ # Pydantic data models
│ ├── tasks/ # Celery task definitions
│ └── main.py # FastAPI application entry point
├── celery\_app.py # Celery application instance setup
├── celery\_worker\_launcher.sh # Script to launch Celery worker
├── Dockerfile # Docker configuration for building the image
├── docker-compose.yml # For local multi-container development (optional)
├── requirements.txt # Python dependencies
└── .env.example # Example environment variables



## Getting Started Locally

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.9+
* A running Redis instance (e.g., local install, Memurai on Windows, or Docker)
* Git

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/18053923230/chromaflow-backend.git
   cd chromaflow-backend
   ```
2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # On Windows:
   # .\venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   ```
3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**

   * Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   * Modify `.env` to point to your local Redis instance (if not already `redis://localhost:6379/0`):
     ```env
     CELERY_BROKER_URL=redis://localhost:6379/0
     CELERY_RESULT_BACKEND=redis://localhost:6379/0
     ```
5. **Run the FastAPI application:**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at `http://localhost:8000`. Swagger UI docs at `http://localhost:8000/docs`.
6. **Run the Celery worker (in a separate terminal):**

   ```bash
   celery -A celery_app.celery_instance worker -l info -P solo
   ```

### Testing the API

You can use tools like Postman, Insomnia, or `curl` to test the API endpoints.

**Example: Process Image**

* **Endpoint:** `POST /api/v1/process`
* **Body Type:** `form-data`
* **Fields:**
  * `image` (File): Your image file.
  * `operations_json` (Text): A JSON string defining the operations.
    ```json
    [
        {"type": "remove_background", "params": {}},
        {"type": "resize", "params": {"width": 500}}
    ]
    ```
* This will return a `task_id`.

**Example: Get Task Status**

* **Endpoint:** `GET /api/v1/tasks/{task_id}`

**Example: Download Processed Image**

* **Endpoint:** `GET /api/v1/tasks/{task_id}/download` (when task is successful)

## Deployment

This project is designed to be deployed using Docker. An example deployment setup for Render.com is as follows:

1. **Render Redis ("Key Value" instance):** Create a Redis instance on Render.
2. **Render Web Service (FastAPI):**
   * Runtime: Docker
   * Repository: Your GitHub repo
   * Environment Variables:
     * `CELERY_BROKER_URL`: Internal URL of your Render Redis.
     * `CELERY_RESULT_BACKEND`: Internal URL of your Render Redis.
     * `PYTHONUNBUFFERED=1`
   * Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
3. **Render Background Worker (Celery):**
   * Runtime: Docker
   * Repository: Your GitHub repo
   * Environment Variables: (Same as Web Service for Celery/Redis URLs)
   * Start Command: `bash ./celery_worker_launcher.sh`

Refer to the `Dockerfile` and Render's documentation for more details.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Open a Pull Request.

Please make sure to update tests as appropriate.

## Future Enhancements / To-Do

* [ ]  Add more image operations (format conversion, color adjustments, filters).
* [ ]  Implement user authentication and authorization.
* [ ]  Allow users to save and manage workflow templates.
* [ ]  More robust error handling and reporting.
* [ ]  Unit and integration tests.
* [ ]  Optimize `rembg` model loading/caching.
* [ ]  Frontend application to consume this API.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (You'll need to create this file with the MIT license text).

## Acknowledgements

* FastAPI community
* Celery project
* Daniel Gatis for `rembg`
* Pillow maintainers
* Render.com for their PaaS

---

Let me know if you have any questions or feedback.
Contact: [qq260316514@gmail.com] or GitHub Issues.
