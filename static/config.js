// Backend local de Universal App Runner.
// Si la interfaz viene de FastAPI, usa el mismo origen.
// Si INDEX.HTML se abre directamente con doble clic, usa localhost.
window.API_BASE_URL =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : window.location.origin;
