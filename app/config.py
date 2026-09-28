import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 500 * 1024 * 1024))
ALLOWED_EXTENSIONS = {".apk"}

# Comando ADB local. Puedes cambiarlo con ADB_PATH si adb no está en PATH.
ADB_PATH = os.getenv("ADB_PATH", "adb")
ADB_SERIAL = os.getenv("ADB_SERIAL", "").strip()
AAPT_PATH = os.getenv("AAPT_PATH", "aapt")
