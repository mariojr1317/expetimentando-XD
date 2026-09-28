const API_BASE_URL = (window.API_BASE_URL || "").replace(/\/$/, "");
const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const session = document.getElementById("session");
const screen = document.getElementById("screen");

function setStatus(message) {
  status.textContent = message;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadButton.disabled = false;
  setStatus(`APK listo: ${file.name}`);
});

uploadButton.addEventListener("click", async () => {
  const file = fileInput.files[0];

  if (!file) {
    setStatus("Selecciona un APK.");
    return;
  }

  if (!file.name.toLowerCase().endsWith(".apk")) {
    setStatus("Esta versión local acepta archivos .APK.");
    return;
  }

  const form = new FormData();
  form.append("file", file);

  uploadButton.disabled = true;
  progress.hidden = false;
  progress.value = 10;
  setStatus("Copiando APK al runner local...");

  try {
    const response = await fetch(API_BASE_URL + "/api/sessions", {
      method: "POST",
      body: form,
    });

    const contentType = response.headers.get("content-type") || "";
    const body = await response.text();

    if (!contentType.includes("application/json")) {
      throw new Error("El servidor local no respondió con JSON.");
    }

    const data = JSON.parse(body);

    if (!response.ok) {
      throw new Error(data.detail || "Error al ejecutar el APK.");
    }

    progress.value = 100;
    session.textContent = "Sesión: " + data.session_id;
    setStatus(data.message);

    if (data.status === "running") {
      screen.classList.add("active");
      const label = screen.querySelector(".screen-placeholder span:last-child");
      if (label) {
        label.textContent = "APK ejecutándose en el Android local.";
      }
    }
  } catch (error) {
    setStatus("Error: " + error.message);
  } finally {
    uploadButton.disabled = false;
  }
});
