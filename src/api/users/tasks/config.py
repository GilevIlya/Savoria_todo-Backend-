from pathlib import Path

TASKS_FOLDER_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
TASK_UPLOAD_DIR = TASKS_FOLDER_BASE_DIR / "uploads" / "task_images"
TASK_IMG_URL = "http://localhost:8000/uploads/task_images/"