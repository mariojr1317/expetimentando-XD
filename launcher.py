import subprocess
import sys
import time
import urllib.request
import webbrowser


HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def main():
    print("🚀 Iniciando Universal App Runner...")
    print(f"🌐 Servidor: {URL}")

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ]
    )

    print("⏳ Esperando a que FastAPI esté listo...")

    for _ in range(30):
        if process.poll() is not None:
            print()
            print("❌ FastAPI se cerró antes de iniciar.")
            print(f"   Código de salida: {process.returncode}")
            print()
            print("El error de Uvicorn debería aparecer arriba.")
            input("Presiona Enter para cerrar...")
            return

        try:
            with urllib.request.urlopen(f"{URL}/api/health", timeout=1) as response:
                if response.status == 200:
                    print("✅ FastAPI está funcionando.")
                    print("🌐 Abriendo el navegador...")
                    webbrowser.open(URL)
                    print()
                    print("El servidor seguirá funcionando mientras esta ventana esté abierta.")
                    input("Presiona Enter para detenerlo...")
                    process.terminate()
                    return
        except Exception:
            time.sleep(0.5)

    print()
    print("❌ FastAPI no respondió después de 15 segundos.")
    print("Revisa el error que apareció arriba.")
    input("Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
