const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const session = document.getElementById("session");

uploadButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return setStatus("Selecciona un archivo .EXE o .APK.");

  const form = new FormData();
  form.append("file", file);
  uploadButton.disabled = true;
  progress.hidden = false;
  progress.value = 0;
  setStatus("Subiendo archivo...");

  try {
    const response = await fetch("/api/sessions", { method: "POST", body: form });
    const contentType = response.headers.get("content-type") || "";
    const body = await response.text();

    let data;
    if (contentType.includes("application/json")) {
      data = JSON.parse(body);
    } else {
      throw new Error("El servidor devolvió HTML en vez de JSON. Si estás usando GitHub Pages, FastAPI no está ejecutándose allí.");
    }

    if (!response.ok) throw new Error(data.detail || "Error al subir el archivo.");

    progress.value = 100;
    session.textContent = "Sesión: " + data.session_id;
    setStatus(data.message);
  } catch (error) {
    setStatus(error.message);
  } finally {
    uploadButton.disabled = false;
  }
});

function setStatus(message) {
  status.textContent = message;
}
