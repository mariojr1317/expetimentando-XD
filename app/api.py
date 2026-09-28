from pathlib import Path
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from .android_runner import AndroidRunnerError, configured as android_runner_configured, create_android_session
from .config import ALLOWED_EXTENSIONS, ANDROID_RUNNER_URL, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .models import create_session, get_session

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/auth/status")
def auth_status():
    return {"configured": False, "disabled": True}


@router.get("/capabilities")
def capabilities():
    return {
        "upload": True,
        "exe": {"available": False, "reason": "Windows isolated runner is not implemented"},
        "apk": {
            "available": android_runner_configured(),
            "reason": (
                "Android Runner configurado"
                if android_runner_configured()
                else "Configura un Android Runner aislado"
            ),
        },
        "webrtc": {"available": False, "reason": "WebRTC streaming is not implemented"},
    }


@router.post("/sessions")
async def upload_app(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Solo se permiten archivos .exe y .apk.")

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
    except Exception:
        destination.unlink(missing_ok=True)
        raise HTTPException(500, "No se pudo guardar el archivo.")

    if extension == ".apk":
        if not android_runner_configured():
            session.status = "uploaded"
            return {
                "session_id": session.id,
                "filename": filename,
                "extension": extension,
                "size": size,
                "status": session.status,
                "android_ready": False,
                "message": "APK recibido. Falta conectar el Android Runner aislado.",
            }

        try:
            runner = create_android_session(session.id, destination, filename)
        except AndroidRunnerError as exc:
            session.status = "runner_error"
            raise HTTPException(502, str(exc)) from exc

        session.status = runner.get("status", "running")
        session.runner_session_id = runner.get("session_id")
        session.runner_url = ANDROID_RUNNER_URL

        return {
            "session_id": session.id,
            "filename": filename,
            "extension": extension,
            "size": size,
            "status": session.status,
            "android_ready": True,
            "runner_session_id": session.runner_session_id,
            "message": runner.get(
                "message",
                "Sesión Android creada. El streaming todavía no está conectado.",
            ),
        }

    return {
        "session_id": session.id,
        "filename": filename,
        "extension": extension,
        "size": size,
        "status": session.status,
        "android_ready": False,
        "message": "EXE recibido. El runner Windows aislado todavía no está implementado.",
    }


@router.post("/sessions/{session_id}/start")
def start_session(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    if session.extension != ".apk":
        raise HTTPException(400, "Solo las sesiones APK pueden iniciarse con este endpoint.")

    if not android_runner_configured():
        raise HTTPException(503, "El Android Runner no está configurado.")

    apk_path = UPLOAD_DIR / f"{session.id}.apk"
    if not apk_path.exists():
        raise HTTPException(404, "El APK de la sesión ya no está disponible.")

    try:
        runner = create_android_session(session.id, apk_path, session.filename)
    except AndroidRunnerError as exc:
        session.status = "runner_error"
        raise HTTPException(502, str(exc)) from exc

    session.status = runner.get("status", "running")
    session.runner_session_id = runner.get("session_id")
    session.runner_url = ANDROID_RUNNER_URL

    return {
        "session_id": session.id,
        "status": session.status,
        "runner_session_id": session.runner_session_id,
        "message": runner.get("message", "Sesión Android iniciada."),
    }


@router.get("/sessions/{session_id}")
def session_info(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(404, "Sesión no encontrada.")

    return session.__dict__
