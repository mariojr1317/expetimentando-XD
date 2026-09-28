// El runner siempre es local.
// Esto evita que un GitHub Pages/Nginx reciba el APK antes de llegar a FastAPI.
window.API_BASE_URL = "http://127.0.0.1:8000";
