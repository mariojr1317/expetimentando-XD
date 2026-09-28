# Universal App Runner — Local

Versión local del proyecto. El navegador habla con FastAPI en `localhost` y el APK se instala en un dispositivo o emulador Android conectado por ADB.

## Flujo

```
Navegador
   ↓
FastAPI (127.0.0.1:8000)
   ↓
ADB local
   ↓
Android Emulator / dispositivo
   ↓
APK
```

No se usa Render ni se sube el APK a Internet.

## Requisitos para APK

- Python 3.11+
- Android SDK Platform-Tools (`adb`)
- Un Android Emulator local o un dispositivo Android con ADB.
- Para apertura automática: `aapt` debe estar disponible.

Comprueba ADB:

```bash
adb devices
```

Debe aparecer al menos un dispositivo con estado `device`.

## Ejecutar

```bash
pip install -r requirements.txt
python run.py
```

Después abre `http://127.0.0.1:8000`.

Selecciona un APK y pulsa **Subir archivo**. El backend lo guarda temporalmente, lo instala con `adb install -r` y, cuando puede detectar el package name, lo abre con ADB.

## Variables opcionales

```text
ADB_PATH=adb
ADB_SERIAL=
AAPT_PATH=aapt
MAX_UPLOAD_SIZE=524288000
```

`ADB_SERIAL` sirve para elegir un emulador concreto si hay varios dispositivos conectados.

## Estado

- Interfaz local: lista.
- Backend FastAPI local: listo.
- Instalación de APK mediante ADB: lista.
- Apertura automática: lista cuando `aapt` detecta el package.
- Streaming del Android dentro de la página: pendiente.
- Runner EXE: pendiente.

El runner local usa comandos ADB fijos y no ejecuta comandos proporcionados por el APK.