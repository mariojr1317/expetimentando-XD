from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from .config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .local_runner import LocalRunnerError, install_and_launch_apk
from .models import create_session, get_session

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok", "mode": "local"}


@router.get("/capabilities")
def capabilities():
    return {
        "mode": "local",
        "upload": True,
        "apk": {"available": True},
        "exe": {
            "available": False,
            "reason": "El runner EXE local todavía no está implementado.",
        },
        "webrtc": {
            "available": False,
            "reason": "La primera versión usa el emulador local; streaming embebido queda para después.",
        },
    }


@router.post("/sessions")
async def upload_app(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Esta versión local acepta archivos .APK.")

    session = create_session(filename, extension)
    destination = UPLOAD_DIR / f"{session.id}{extension}"
    size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    destination.unlink(missing_ok=True)
                    raise HTTPException(413, "El archivo supera el límite configurado.")
                output.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(500, f"No se pudo guardar el APK: {exc}") from exc

    try:
        result = install_and_launch_apk(destination)
    except LocalRunnerError as exc:
        session.status = "runner_error"
        return {
            "session_id": session.id,
            "filename": filename,
            "extension": extension,
            "size": size,
            "status": session.status,
            "message": str(exc),
        }

    session.status = result["status"]

    return {
        "session_id": session.id,
        "filename": filename,
        "extension": extension,
        "size": size,
        "status": session.status,
        "message": result["message"],
        "package": result.get("package"),
    }


@router.post("/sessions/{session_id}/start")
def start_session(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    apk_path = UPLOAD_DIR / f"{session.id}.apk"
    if not apk_path.exists():
        raise HTTPException(404, "El APK de la sesión ya no está disponible.")

    try:
        result = install_and_launch_apk(apk_path)
    except LocalRunnerError as exc:
        session.status = "runner_error"
        raise HTTPException(503, str(exc)) from exc

    session.status = result["status"]

    return {
        "session_id": session.id,
        "status": session.status,
        "message": result["message"],
        "package": result.get("package"),
    }


@router.get("/sessions/{session_id}")
def session_info(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    return session.__dict__
