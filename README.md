# Universal App Runner

Proyecto experimental para investigar cómo ejecutar aplicaciones en entornos aislados y transmitir su interfaz con baja latencia.

## Objetivo
Permitir que un cliente remoto interactúe con una aplicación que se ejecuta en un entorno aislado, sin instalar la aplicación directamente en el dispositivo cliente.

## Arquitectura prevista
Cliente (browser) -> WebRTC/DataChannel -> Backend -> Runner aislado -> EXE/Android VM

## Estado actual
Fase 0: estructura inicial. La ejecución de archivos arbitrarios todavía NO está habilitada.

Antes de ejecutar archivos desconocidos se necesita aislamiento real (VM/sandbox), límites de CPU/RAM/disco, control de red y eliminación automática de sesiones.

## Próximos pasos
1. Backend Python.
2. API de sesiones.
3. Frontend web.
4. Canal de entrada de baja latencia.
5. Streaming mediante WebRTC.
6. Runner aislado para EXE.
7. Runner Android para APK.
8. Medición de latencia end-to-end.

## Desarrollo
Python 3.11+ recomendado.
Instalar dependencias: pip install -r requirements.txt
Iniciar servidor: python -m app.main

Proyecto educativo/experimental. No ejecutes archivos desconocidos directamente en el sistema host.