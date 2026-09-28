# Universal App Runner — Local

Runner completamente local. El navegador habla con FastAPI en localhost y la aplicación se ejecuta en la misma máquina.

## Flujo

```
Navegador
   ↓
FastAPI (localhost:8000)
   ↓
APK → ADB → Android local
   ↑
JSON → configuración
```

No se usa Render, no se envían los archivos a un servidor remoto y no se necesita una cuenta.

## APK + JSON

La configuración JSON se usa para indicarle al runner qué APK debe ejecutar y, opcionalmente, cuál es su paquete Android.

Primero selecciona y sube el APK. Después selecciona y sube su JSON.

Ejemplo:

```json
{
  "name": "Mi APK",
  "type": "apk",
  "file": "mi_app.apk",
  "package": "com.ejemplo.app"
}
```

- `name`: nombre descriptivo.
- `type`: debe ser `apk`.
- `file`: nombre exacto del APK que subiste.
- `package`: paquete Android. Es opcional si `aapt` puede detectarlo automáticamente.

El JSON no puede usar rutas absolutas ni `..`; el runner solo busca el APK que ya fue cargado en la sesión local.

## Requisitos para APK

- Python 3.11+
- Android SDK Platform-Tools (`adb`)
- Android Emulator local o Android con ADB
- `aapt` es opcional si el JSON incluye `package`.

Comprueba ADB:

```bash
adb devices
```

Después:

```bash
pip install -r requirements.txt
python run.py
```

Abre `http://localhost:8000`.

## EXE

Los `.exe` se ejecutan **directamente en el PC local con Windows** mediante `subprocess.Popen`. No se ejecutan en la nube. Esta parte queda para después.

## Estado

- Interfaz local: lista.
- Backend FastAPI local: listo.
- APK + ADB local: listo.
- APK + JSON: listo.
- Streaming de la pantalla dentro del navegador: pendiente.
- EXE: reservado para una fase posterior.

**Importante:** el APK se ejecuta en el Android local. La pantalla del Android todavía no se transmite dentro del navegador; esa será la siguiente fase.
