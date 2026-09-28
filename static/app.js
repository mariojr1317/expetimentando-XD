const API_BASE_URL=(window.API_BASE_URL||"").replace(/\/$/,"");
const loginView=document.getElementById("login-view");
const appView=document.getElementById("app-view");
const loginForm=document.getElementById("login-form");
const passwordInput=document.getElementById("password");
const loginStatus=document.getElementById("login-status");
const logoutButton=document.getElementById("logout");
const fileInput=document.getElementById("file");
const uploadButton=document.getElementById("upload");
const status=document.getElementById("status");
const progress=document.getElementById("progress");
const session=document.getElementById("session");
const TOKEN_KEY="uar_token";

function setStatus(message){status.textContent=message}
function token(){return sessionStorage.getItem(TOKEN_KEY)}
function showApp(){loginView.hidden=true;appView.hidden=false}
function showLogin(){loginView.hidden=false;appView.hidden=true}

async function login(password){
  const response=await fetch(API_BASE_URL+"/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({password})});
  const data=await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(data.detail||"No se pudo iniciar sesión.");
  sessionStorage.setItem(TOKEN_KEY,data.token);
  showApp();
}

loginForm.addEventListener("submit",async e=>{
  e.preventDefault();
  loginStatus.textContent="Comprobando...";
  try{await login(passwordInput.value);passwordInput.value="";loginStatus.textContent=""}
  catch(error){loginStatus.textContent=error.message}
});

logoutButton.addEventListener("click",()=>{sessionStorage.removeItem(TOKEN_KEY);showLogin()});

uploadButton.addEventListener("click",async()=>{
  const file=fileInput.files[0];
  if(!file)return setStatus("Selecciona un archivo .EXE o .APK.");
  if(!API_BASE_URL&&window.location.hostname.endsWith("github.io"))return setStatus("Configura la URL pública del backend en static/config.js.");
  const form=new FormData();form.append("file",file);
  uploadButton.disabled=true;progress.hidden=false;progress.value=0;setStatus("Subiendo archivo...");
  try{
    const response=await fetch(API_BASE_URL+"/api/sessions",{method:"POST",headers:{Authorization:"Bearer "+token()},body:form});
    const contentType=response.headers.get("content-type")||"";
    const body=await response.text();
    if(!contentType.includes("application/json"))throw new Error("El backend respondió con HTML en vez de JSON.");
    const data=JSON.parse(body);
    if(response.status===401){sessionStorage.removeItem(TOKEN_KEY);showLogin();throw new Error("La sesión expiró.")}
    if(!response.ok)throw new Error(data.detail||"Error al subir el archivo.");
    progress.value=100;session.textContent="Sesión: "+data.session_id;setStatus(data.message);
  }catch(error){setStatus("Error: "+error.message)}
  finally{uploadButton.disabled=false}
});
