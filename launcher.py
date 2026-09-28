import subprocess
import sys
import webbrowser


def main():
    print("Iniciando Universal App Runner...")
    print("Abre http://127.0.0.1:8000 cuando el servidor esté listo.")

    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
