import json
from pathlib import Path
from urllib import error, request

from .config import ANDROID_RUNNER_TOKEN, ANDROID_RUNNER_URL


class AndroidRunnerError(RuntimeError):
    pass


def configured() -> bool:
    return bool(ANDROID_RUNNER_URL and ANDROID_RUNNER_TOKEN)


def create_android_session(session_id: str, apk_path: Path, filename: str) -> dict:
    if not configured():
        raise AndroidRunnerError(
            "El Android Runner no está configurado. Define ANDROID_RUNNER_URL y ANDROID_RUNNER_TOKEN."
        )

    data = apk_path.read_bytes()
    boundary = "----UniversalAppRunnerBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="session_id"\r\n\r\n'
        f"{session_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/vnd.android.package-archive\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()

    req = request.Request(
        f"{ANDROID_RUNNER_URL}/sessions",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {ANDROID_RUNNER_TOKEN}",
        },
    )

    try:
        with request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AndroidRunnerError(f"Android Runner respondió HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise AndroidRunnerError(f"No se pudo contactar al Android Runner: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AndroidRunnerError("El Android Runner no devolvió JSON válido.") from exc
