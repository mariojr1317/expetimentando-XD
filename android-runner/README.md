# Android Runner

Usaremos el Android Emulator Container Scripts oficial de Google como base del runner. El proyecto oficial permite ejecutar Android en un contenedor Linux con KVM y expone ADB (5555) y el servicio gRPC/WebRTC (8554). También incluye un gateway WebRTC para ver y controlar el emulador desde el navegador.

## Arquitectura

Universal App Runner -> Android Runner -> Android Emulator -> WebRTC -> navegador

El APK no se ejecutará dentro del backend principal de Render.

## Requisitos

- Host Linux.
- Docker y Docker Compose.
- KVM disponible.
- Preferiblemente una VM con virtualización anidada o un host con KVM directo.

## Imagen oficial de prueba

`us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2`

Puertos del emulador:

- 5555: ADB
- 8554: gRPC/WebRTC

## Siguiente integración

El adaptador existente en `app/android_runner.py` enviará cada APK al servicio aislado. Después conectaremos el gateway WebRTC oficial al frontend para que la pantalla y los inputs no dependan de capturas periódicas.

Fuente oficial: https://github.com/google/android-emulator-container-scripts
