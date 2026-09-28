import json
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from .config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, UPLOAD_DIR
from .local_runner import LocalRunnerError, install_and_launch_apk, launch_exe
from .models import create_session, get_latest_session_by_filename, get_session

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok", "mode": "local"}


@router.get("/capabilities")
def capabilities():
    return {
        "mode": "local",
        "upload": True,
        "apk": {"available": True, "runner": "ADB local", "json_config": True},
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


def _safe_json_config(data: object) -> dict:
    if not isinstance(data, dict):
        raise LocalRunnerError("El JSON debe contener un objeto.")

    app_type = data.get("type")
    if app_type != "apk":
        raise LocalRunnerError('Por ahora el JSON solo admite "type": "apk".')

    filename = data.get("file")
    if not isinstance(filename, str) or not filename.strip():
        raise LocalRunnerError('El JSON necesita un campo "file" con el nombre del APK.')

    filename_path = Path(filename)
    if (
        filename_path.name != filename
        or filename_path.is_absolute()
        or ".." in filename_path.parts
        or filename_path.suffix.lower() != ".apk"
    ):
        raise LocalRunnerError("El campo "file" debe ser solamente el nombre de un .apk.")

    package = data.get("package")
    if package is not None and (
        not isinstance(package, str)
        or not package.strip()
        or any(char.isspace() for char in package)
    ):
        raise LocalRunnerError('El campo "package" debe ser un identificador válido.')

    name = data.get("name", Path(filename).stem)
    if not isinstance(name, str) or not name.strip():
        raise LocalRunnerError('El campo "name" debe ser texto.')

    return {
        "name": name.strip(),
        "type": "apk",
        "file": filename,
        "package": package.strip() if isinstance(package, str) else None,
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


@router.post("/configs")
async def upload_config(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if Path(filename).suffix.lower() != ".json":
        raise HTTPException(400, "La configuración debe ser un archivo .json.")

    try:
        raw = await file.read(256 * 1024 + 1)
        if len(raw) > 256 * 1024:
            raise LocalRunnerError("El JSON supera el límite de 256 KB.")
        data = json.loads(raw.decode("utf-8"))
        config = _safe_json_config(data)
    except UnicodeDecodeError as exc:
        raise HTTPException(400, "El JSON debe estar codificado en UTF-8.") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(400, f"JSON inválido: {exc.msg}.") from exc
    except LocalRunnerError as exc:
        raise HTTPException(400, str(exc)) from exc

    session = get_latest_session_by_filename(config["file"])
    if not session or session.extension != ".apk":
        raise HTTPException(
            404,
            f"No se encontró un APK cargado con el nombre {config['file']}. "
            "Primero selecciona y sube ese APK.",
        )

    apk_path = UPLOAD_DIR / f"{session.id}.apk"
    if not apk_path.exists():
        raise HTTPException(404, "El APK de la sesión ya no está disponible.")

    try:
        result = install_and_launch_apk(apk_path, config["package"])
    except LocalRunnerError as exc:
        session.status = "runner_error"
        return {
            "session_id": session.id,
            "filename": session.filename,
            "extension": ".apk",
            "status": session.status,
            "config": config,
            "message": str(exc),
        }

    session.status = result["status"]

    return {
        "session_id": session.id,
        "filename": session.filename,
        "extension": ".apk",
        "status": session.status,
        "config": config,
        "message": result["message"],
        "package": result.get("package"),
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
