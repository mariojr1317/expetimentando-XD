import os
import shutil
import subprocess
from pathlib import Path

from .config import AAPT_PATH, ADB_PATH, ADB_SERIAL


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
            "No se encontró ADB. Instala Android SDK Platform-Tools y asegúrate de que 'adb' esté en PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise LocalRunnerError("ADB tardó demasiado en responder.") from exc


def _ensure_device() -> None:
    result = _run(_adb_command("devices"), timeout=15)

    if result.returncode != 0:
        raise LocalRunnerError(
            "ADB no pudo iniciarse: " + (result.stderr.strip() or result.stdout.strip())
        )

    devices = []
    for line in result.stdout.splitlines():
        if "\tdevice" in line:
            devices.append(line.split("\t", 1)[0])

    if not devices:
        raise LocalRunnerError(
            "No hay ningún dispositivo Android conectado. Inicia un emulador local y comprueba 'adb devices'."
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


def install_and_launch_apk(apk_path: Path) -> dict:
    apk_path = apk_path.resolve()

    if not apk_path.exists() or apk_path.suffix.lower() != ".apk":
        raise LocalRunnerError("El archivo APK no existe o no es un .apk.")

    _ensure_device()

    install = _run(_adb_command("install", "-r", str(apk_path)), timeout=120)

    if install.returncode != 0:
        detail = install.stderr.strip() or install.stdout.strip()
        raise LocalRunnerError("ADB no pudo instalar el APK: " + detail)

    package = _package_from_apk(apk_path)

    if not package:
        return {
            "status": "installed",
            "message": "APK instalado correctamente. No se pudo detectar automáticamente el paquete para abrirlo.",
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
