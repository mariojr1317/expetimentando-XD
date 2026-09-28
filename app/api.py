from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from .config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .local_runner import LocalRunnerError, install_and_launch_apk, launch_exe
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
        "apk": {"available": True, "runner": "ADB local"},
        "exe": {
            "available": True,
            "runner": "Windows local",
            "note": "Los EXE se ejecutan en el mismo PC; no se suben a Internet.",
        },
        "webrtc": {
            "available": False,
            "reason": "El visor embebido queda para una fase posterior.",
        },
    }


@router.post("/sessions")
async def upload_app(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Solo se aceptan archivos .APK y .EXE.")

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
        raise HTTPException(500, f"No se pudo guardar el archivo: {exc}") from exc

    try:
        if extension == ".apk":
            result = install_and_launch_apk(destination)
        else:
            result = launch_exe(destination)
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
        "pid": result.get("pid"),
    }


@router.post("/sessions/{session_id}/start")
def start_session(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    app_path = UPLOAD_DIR / f"{session.id}{session.extension}"
    if not app_path.exists():
        raise HTTPException(404, "El archivo de la sesión ya no está disponible.")

    try:
        if session.extension == ".apk":
            result = install_and_launch_apk(app_path)
        elif session.extension == ".exe":
            result = launch_exe(app_path)
        else:
            raise LocalRunnerError("Tipo de archivo no soportado.")
    except LocalRunnerError as exc:
        session.status = "runner_error"
        raise HTTPException(503, str(exc)) from exc

    session.status = result["status"]

    return {
        "session_id": session.id,
        "status": session.status,
        "message": result["message"],
        "package": result.get("package"),
        "pid": result.get("pid"),
    }


@router.get("/sessions/{session_id}")
def session_info(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    return session.__dict__
