from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from .config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .models import create_session, get_session

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/capabilities")
def capabilities():
    return {
        "upload": True,
        "exe": {"available": False, "reason": "isolated Windows runner not implemented"},
        "apk": {"available": False, "reason": "isolated Android runner not implemented"},
        "webrtc": {"available": False, "reason": "streaming not implemented"},
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
                    raise HTTPException(413, "El archivo supera el limite de 500 MB.")
                output.write(chunk)
    except HTTPException:
        raise
    except Exception:
        destination.unlink(missing_ok=True)
        raise HTTPException(500, "No se pudo guardar el archivo.")

    return {
        "session_id": session.id,
        "filename": filename,
        "extension": extension,
        "size": size,
        "status": session.status,
        "message": "Archivo recibido. El runner aislado todavía no está implementado.",
    }

@router.get("/sessions/{session_id}")
def session_info(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Sesión no encontrada.")
    return session.__dict__
