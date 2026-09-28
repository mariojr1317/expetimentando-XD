# Universal App Runner

Proyecto experimental para ejecutar aplicaciones en entornos aislados y, más adelante, transmitir su interfaz con baja latencia al navegador.

## APK: Android Runner

El backend ahora acepta APK y puede crear una sesión Android mediante un **Android Runner separado**.

Arquitectura:

```
Chromebook
   ↓ navegador
GitHub Pages
   ↓ HTTPS + token
FastAPI / Render
   ↓ HTTPS + ANDROID_RUNNER_TOKEN
Android Runner dedicado
   ↓ ADB
Android Emulator / dispositivo de prueba
   ↓
APK
```

El Android Runner **no se ejecuta dentro del proceso FastAPI ni en el host de Render**. Debe ser una máquina/VM dedicada que tenga Android Emulator y ADB. Esto evita instalar APK arbitrarios en el servidor web principal.

### Variables del backend

Configura como secretos:

- `RUNNER_PASSWORD`: contraseña para entrar a la web.
- `TOKEN_SECRET`: secreto largo y aleatorio para firmar las sesiones web.
- `ANDROID_RUNNER_URL`: URL HTTPS del servicio Android Runner.
- `ANDROID_RUNNER_TOKEN`: token compartido entre FastAPI y el Android Runner.

### Contrato del Android Runner

El backend envía:

- `POST /sessions`
- Header: `Authorization: Bearer <ANDROID_RUNNER_TOKEN>`
- Multipart:
  - `session_id`
  - `file` = APK

El runner debe devolver JSON parecido a:

```json
{
  "session_id": "runner-session-id",
  "status": "running",
  "message": "APK instalado y lanzado."
}
```

Cuando el runner está configurado, subir un APK crea automáticamente la sesión Android. También existe:

```
POST /api/sessions/{session_id}/start
```

para volver a iniciar la sesión.

## Estado actual

- Login por contraseña: listo.
- Subida de APK: lista.
- Creación de sesión Android mediante runner: lista.
- Android Emulator real: requiere desplegar el Android Runner en una máquina/VM dedicada.
- Streaming WebRTC: todavía pendiente.
- Control táctil/teclado/mouse: todavía pendiente.
- Runner Windows para EXE: todavía pendiente.

## Seguridad

No ejecutes APK desconocidos directamente en el host del backend. El Android Runner debe usar un emulador dedicado y aislado. No pongas contraseñas ni tokens en GitHub.

## Desarrollo

Python 3.11+ recomendado.

```bash
pip install -r requirements.txt
python run.py
```
