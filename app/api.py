from pathlib import Path
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from pydantic import BaseModel
from .auth import check_password, create_token, valid_token
from .config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .models import create_session, get_session

router = APIRouter(prefix="/api")

class LoginRequest(BaseModel):
    password: str

def require_auth(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Autenticación requerida.")
    if not valid_token(authorization[7:]):
        raise HTTPException(401, "Sesión inválida o expirada.")

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/auth/status")
def auth_status():
    from .auth import configured
    return {"configured": configured()}

@router.post("/auth/login")
def login(data: LoginRequest):
    from .auth import configured
    if not configured():
        raise HTTPException(503, "La contraseña del runner no está configurada en el servidor.")
    if not check_password(data.password):
        raise HTTPException(401, "Contraseña incorrecta.")
    return {"token": create_token()}

@router.get("/capabilities")
def capabilities(authorization: str | None = Header(default=None)):
    require_auth(authorization)
    return {
        "upload": True,
        "exe": {"available": False, "reason": "Windows isolated runner is not implemented"},
        "apk": {"available": False, "reason": "Android isolated runner is not implemented"},
        "webrtc": {"available": False, "reason": "WebRTC streaming is not implemented"},
    }

@router.post("/sessions")
async def upload_app(file: UploadFile = File(...), authorization: str | None = Header(default=None)):
    require_auth(authorization)
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

    return {
        "session_id": session.id,
        "filename": filename,
        "extension": extension,
        "size": size,
        "status": session.status,
        "message": "Archivo recibido. El runner aislado todavía no está implementado.",
    }

@router.get("/sessions/{session_id}")
def session_info(session_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Sesión no encontrada.")
    return session.__dict__
