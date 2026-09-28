from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .api import router

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "INDEX.HTML"

app = FastAPI(title="Universal App Runner Local", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def root():
    return FileResponse(INDEX_FILE)


app.include_router(router)
