const API_BASE_URL = (window.API_BASE_URL || "").replace(/\/$/, "");
const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const session = document.getElementById("session");
const screen = document.getElementById("screen");
const selectedFile = document.getElementById("selected-file");

function setStatus(message) {
  status.textContent = message;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadButton.disabled = false;
  selectedFile.textContent = `Archivo seleccionado: ${file.name}`;
  const extension = file.name.toLowerCase().endsWith(".apk") ? "APK" : "EXE";
  setStatus(`${extension} listo para ejecutar localmente.`);
});

uploadButton.addEventListener("click", async () => {
  const file = fileInput.files[0];

  if (!file) {
    setStatus("Selecciona un APK o EXE.");
    return;
  }

  const lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith(".apk") && !lowerName.endsWith(".exe")) {
    setStatus("Solo se aceptan archivos .APK y .EXE.");
    return;
  }

  const form = new FormData();
  form.append("file", file);

  uploadButton.disabled = true;
  progress.hidden = false;
  progress.value = 10;
  setStatus("Copiando archivo al runner local...");

  try {
    const response = await fetch(API_BASE_URL + "/api/sessions", {
      method: "POST",
      body: form,
    });

    const contentType = response.headers.get("content-type") || "";
    const body = await response.text();

    if (!contentType.includes("application/json")) {
      throw new Error(
        `El backend respondió ${response.status} con HTML. Comprueba que FastAPI sea el servidor de localhost:8000.`
      );
    }

    const data = JSON.parse(body);

    if (!response.ok) {
      throw new Error(data.detail || "Error al ejecutar la aplicación.");
    }

    progress.value = 100;
    session.textContent = "Sesión: " + data.session_id;
    setStatus(data.message);

    if (data.status === "running") {
      screen.classList.add("active");
      const label = screen.querySelector(".screen-placeholder span:last-child");
      if (label) {
        label.textContent =
          data.extension === ".exe"
            ? "EXE ejecutándose localmente en Windows."
            : "APK ejecutándose en el Android local.";
      }
    }
  } catch (error) {
    progress.value = 0;
    setStatus("Error: " + error.message);
  } finally {
    uploadButton.disabled = false;
  }
});
