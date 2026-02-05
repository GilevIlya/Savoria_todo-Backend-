from pathlib import Path

PROFILE_PHOTO_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROFILE_PHOTO_UPLOAD_DIR = PROFILE_PHOTO_DIR / "uploads" / "avatars"

PROFILE_PHOTO_URL = "http://localhost:8000/uploads/avatars/"
