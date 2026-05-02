import os
from dotenv import load_dotenv

load_dotenv()  # loads from CredTech/.env

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "models")
APP_NAME    = os.getenv("APP_NAME", "CredAI")
VERSION     = os.getenv("VERSION", "1.0.0")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000"
).split(",")
