import os
import shutil
import subprocess
from pathlib import Path

from .config import (
    AAPT_PATH,
    ADB_PATH,
    ADB_SERIAL,
    EXE_TIMEOUT,
    MIN_AVAILABLE_RAM_MB,
    MIN_CPU_CORES,
)


class LocalRunnerError(RuntimeError):
    pass


def _adb_command(*args: str) -> list[str]:
    command = [ADB_PATH]
    if ADB_SERIAL:
        command += ["-s", ADB_SERIAL]
    command += list(args)
    return command


def _run(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise LocalRunnerError(
            "No se encontró la herramienta necesaria. Comprueba la instalación y el PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise LocalRunnerError("El proceso tardó demasiado en responder.") from exc


def _ensure_device() -> None:
    result = _run(_adb_command("devices"), timeout=15)

    if result.returncode != 0:
        raise LocalRunnerError(
            "ADB no pudo iniciarse: " + (result.stderr.strip() or result.stdout.strip())
        )

    devices = [
        line.split("\t", 1)[0]
        for line in result.stdout.splitlines()
        if "\tdevice" in line
    ]

    if not devices:
        raise LocalRunnerError(
            "No hay ningún dispositivo Android conectado. Inicia un emulador local "
            "o conecta un Android con ADB."
        )


def _package_from_apk(apk_path: Path) -> str | None:
    if not shutil.which(AAPT_PATH) and not Path(AAPT_PATH).exists():
        return None

    try:
        result = subprocess.run(
            [AAPT_PATH, "dump", "badging", str(apk_path)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    for line in result.stdout.splitlines():
        if line.startswith("package:"):
            for part in line.split():
                if part.startswith("name="):
                    return part.split("=", 1)[1].strip("'")
    return None


def install_and_launch_apk(apk_path: Path, package_override: str | None = None) -> dict:
    apk_path = apk_path.resolve()

    if not apk_path.exists() or apk_path.suffix.lower() != ".apk":
        raise LocalRunnerError("El archivo APK no existe o no es un .apk.")

    _ensure_device()

    install = _run(_adb_command("install", "-r", str(apk_path)), timeout=120)

    if install.returncode != 0:
        detail = install.stderr.strip() or install.stdout.strip()
        raise LocalRunnerError("ADB no pudo instalar el APK: " + detail)

    package = package_override or _package_from_apk(apk_path)

    if not package:
        return {
            "status": "installed",
            "message": (
                "APK instalado correctamente. Añade el campo \"package\" al JSON "
                "para que el runner pueda abrirlo automáticamente."
            ),
        }

    launch = _run(
        _adb_command("shell", "monkey", "-p", package, "1"),
        timeout=20,
    )

    if launch.returncode != 0:
        detail = launch.stderr.strip() or launch.stdout.strip()
        raise LocalRunnerError(
            f"APK instalado, pero no se pudo abrir {package}: {detail}"
        )

    return {
        "status": "running",
        "message": f"APK instalado y abierto en el Android local ({package}).",
        "package": package,
    }


def _check_exe_resources() -> None:
    try:
        import psutil
    except ImportError as exc:
        raise LocalRunnerError(
            "Falta psutil. Ejecuta: pip install -r requirements.txt"
        ) from exc

    cores = os.cpu_count() or 1
    available_ram_mb = psutil.virtual_memory().available // (1024 * 1024)

    if cores < MIN_CPU_CORES or available_ram_mb < MIN_AVAILABLE_RAM_MB:
        raise LocalRunnerError(
            f"Recursos insuficientes para ejecutar EXE de forma segura: "
            f"{cores} núcleo(s), {available_ram_mb} MB RAM disponibles. "
            f"Se requieren al menos {MIN_CPU_CORES} núcleos y "
            f"{MIN_AVAILABLE_RAM_MB} MB RAM disponibles."
        )


def launch_exe(exe_path: Path) -> dict:
    exe_path = exe_path.resolve()

    if exe_path.suffix.lower() != ".exe":
        raise LocalRunnerError("El archivo no es un .exe.")

    if not exe_path.exists():
        raise LocalRunnerError("El archivo EXE no existe.")

    if os.name != "nt":
        raise LocalRunnerError(
            "El runner EXE local funciona en Windows. ChromeOS/Linux no puede "
            "ejecutar un .exe de Windows directamente."
        )

    _check_exe_resources()

    try:
        process = subprocess.Popen(
            [str(exe_path)],
            cwd=str(exe_path.parent),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except OSError as exc:
        raise LocalRunnerError(
            f"Windows no pudo iniciar el EXE: {exc}"
        ) from exc

    return {
        "status": "running",
        "message": f"EXE iniciado localmente (PID {process.pid}).",
        "pid": process.pid,
    }
