import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ✅ IMPORTANT: only import here
from backend.routes import download

from backend.config import APP_NAME, VERSION, CORS_ORIGINS, BASE_DIR
from backend.services.risk_service import load_models
from backend.routes import risk, fraud, face, session, admin, pdf_form, voice_assistant, analysis

from deepface import DeepFace
import numpy as np
import urllib.request
import urllib.parse
from fastapi.responses import StreamingResponse, RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{APP_NAME} Backend Starting")
    print("Loading ML models...")

    try:
        load_models()
        app.state.models_loaded = True
        print("Models loaded successfully!")
    except Exception as e:
        app.state.models_loaded = False
        print(f"Error loading models: {e}")

    print("Warming up DeepFace...")
    try:
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        DeepFace.analyze(dummy_img, actions=['age'], enforce_detection=False)
        print("DeepFace ready!")
    except Exception as e:
        print(f"DeepFace error: {e}")

    yield


# ✅ CREATE APP FIRST
app = FastAPI(title=APP_NAME, version=VERSION, lifespan=lifespan)


# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ ADD ROUTES (ORDER MATTERS)
app.include_router(download.router, prefix="/api")   # 👈 OUR FIX
app.include_router(risk.router)
app.include_router(fraud.router)
app.include_router(face.router)
app.include_router(session.router)
app.include_router(admin.router)
app.include_router(pdf_form.router)
app.include_router(voice_assistant.router)
app.include_router(analysis.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ✅ SERVE FRONTEND
frontend_dir = os.path.join(BASE_DIR, "frontend")
@app.get("/")
async def redirect_to_kyc():
    return RedirectResponse(url="/credai-voice-kyc.html")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# ✅ TTS
@app.get("/api/tts")
def tts(text: str, lang: str):
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={lang}&client=tw-ob&q={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)

    def stream():
        while True:
            chunk = response.read(4096)
            if not chunk:
                break
            yield chunk

    return StreamingResponse(stream(), media_type="audio/mpeg")