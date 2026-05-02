import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import APP_NAME, VERSION, CORS_ORIGINS, BASE_DIR
from backend.services.risk_service import load_models
from backend.routes import risk, fraud, face, session, admin, pdf_form, voice_assistant, analysis
from deepface import DeepFace
import cv2
import numpy as np
import urllib.request
import urllib.parse
from fastapi.responses import StreamingResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"{APP_NAME} Backend Starting")
    print("Loading ML models...")
    try:
        load_models()
        app.state.models_loaded = True
        print("Models loaded successfully!")
    except Exception as e:
        app.state.models_loaded = False
        print(f"Error loading models: {e}")
        
    print("Warming up DeepFace models...")
    try:
        # Dummy image for warmup
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        DeepFace.analyze(dummy_img, actions=['age', 'gender', 'emotion'], enforce_detection=False, detector_backend="opencv")
        print("DeepFace models warmed up successfully!")
    except Exception as e:
        print(f"Error warming up DeepFace: {e}")
        
    yield
    # Shutdown (if needed)

app = FastAPI(title=APP_NAME, version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(risk.router)
app.include_router(fraud.router)
app.include_router(face.router)
app.include_router(session.router)
app.include_router(admin.router)
app.include_router(pdf_form.router)
app.include_router(voice_assistant.router)
app.include_router(analysis.router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": getattr(app.state, "models_loaded", False)
    }

@app.get("/api/status")
async def api_status():
    return {
        "app": APP_NAME,
        "version": VERSION,
        "status": "active"
    }

# Mount frontend directory
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/api/tts")
def proxy_tts(text: str, lang: str):
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={lang}&client=tw-ob&q={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        def iterfile():
            while True:
                chunk = response.read(4096)
                if not chunk: break
                yield chunk
        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Proxy Error: {e}")
        return {"error": str(e)}