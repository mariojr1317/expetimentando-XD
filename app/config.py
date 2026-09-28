import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 500 * 1024 * 1024))
ALLOWED_EXTENSIONS = {".exe", ".apk"}

ANDROID_RUNNER_URL = os.getenv("ANDROID_RUNNER_URL", "").rstrip("/")
ANDROID_RUNNER_TOKEN = os.getenv("ANDROID_RUNNER_TOKEN", "")
