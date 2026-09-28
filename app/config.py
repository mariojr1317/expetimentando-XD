import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 500 * 1024 * 1024))
ALLOWED_EXTENSIONS = {".apk", ".exe"}

# Android
ADB_PATH = os.getenv("ADB_PATH", "adb")
ADB_SERIAL = os.getenv("ADB_SERIAL", "").strip()
AAPT_PATH = os.getenv("AAPT_PATH", "aapt")

# Windows EXE
EXE_TIMEOUT = int(os.getenv("EXE_TIMEOUT", "15"))
MIN_CPU_CORES = int(os.getenv("MIN_CPU_CORES", "2"))
MIN_AVAILABLE_RAM_MB = int(os.getenv("MIN_AVAILABLE_RAM_MB", "1024"))
