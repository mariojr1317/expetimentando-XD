# Universal App Runner — Local

Runner completamente local. El navegador habla con FastAPI en localhost y la aplicación se ejecuta en la misma máquina.

## Flujo

```
Navegador
   ↓
FastAPI (127.0.0.1:8000)
   ├── APK → ADB → Android local
   └── EXE → proceso Windows local
```

No se usa Render, no se envían los archivos a un servidor remoto y no se necesita una cuenta.

## APK

Requisitos:

- Python 3.11+
- Android SDK Platform-Tools (`adb`)
- Android Emulator local o Android con ADB
- `aapt` para apertura automática cuando sea necesario

Comprueba ADB:

```bash
adb devices
```

Después:

```bash
pip install -r requirements.txt
python run.py
```

Abre `http://127.0.0.1:8000`.

## EXE

Los `.exe` se ejecutan **directamente en el PC local con Windows** mediante `subprocess.Popen`. No se ejecutan en la nube.

El runner hace una comprobación antes de iniciar un EXE:

- mínimo configurable de 2 núcleos
- mínimo configurable de 1024 MB de RAM disponible

Por tanto, una máquina con **1 núcleo y 250 MB de RAM disponibles será rechazada** en vez de intentar ejecutar el programa y fingir que tiene recursos suficientes.

Si el sistema no es Windows, el runner devuelve un mensaje claro: un EXE de Windows no puede ejecutarse directamente en ChromeOS/Linux.

El runner tampoco puede garantizar que cualquier EXE funcione: un programa puede requerir DLL, drivers, arquitectura o componentes de Windows que no estén instalados. En esos casos el error se devuelve como estado del runner en lugar de romper FastAPI.

## Variables opcionales

```text
ADB_PATH=adb
ADB_SERIAL=
AAPT_PATH=aapt
MAX_UPLOAD_SIZE=524288000
MIN_CPU_CORES=2
MIN_AVAILABLE_RAM_MB=1024
EXE_TIMEOUT=15
```

## Estado

- Interfaz local: lista.
- Backend FastAPI local: listo.
- APK + ADB local: listo.
- EXE + Windows local: listo.
- Comprobación de recursos para EXE: lista.
- Streaming de la pantalla dentro del navegador: pendiente.

**Importante:** ejecutar un EXE no significa que su ventana aparezca automáticamente dentro del navegador. La primera versión lo inicia en el escritorio local; el visor remoto/embebido es una fase separada.
