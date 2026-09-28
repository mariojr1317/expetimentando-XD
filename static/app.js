const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const session = document.getElementById("session");

const API_BASE_URL = (window.API_BASE_URL || "").replace(/\/$/, "");

function setStatus(message) {
  status.textContent = message;
}

uploadButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return setStatus("Selecciona un archivo .EXE o .APK.");

  if (!API_BASE_URL && window.location.hostname.endsWith("github.io")) {
    return setStatus("Configura la URL pública del backend en static/config.js.");
  }

  const form = new FormData();
  form.append("file", file);
  uploadButton.disabled = true;
  progress.hidden = false;
  progress.value = 0;
  setStatus("Subiendo archivo...");

  try {
    const response = await fetch(API_BASE_URL + "/api/sessions", {
      method: "POST",
      body: form
    });
    const contentType = response.headers.get("content-type") || "";
    const body = await response.text();

    if (!contentType.includes("application/json")) {
      throw new Error("El backend respondió con HTML en vez de JSON. Comprueba la URL del backend.");
    }

    const data = JSON.parse(body);
    if (!response.ok) throw new Error(data.detail || "Error al subir el archivo.");

    progress.value = 100;
    session.textContent = "Sesión: " + data.session_id;
    setStatus(data.message);
  } catch (error) {
    setStatus("Error: " + error.message);
  } finally {
    uploadButton.disabled = false;
  }
});
