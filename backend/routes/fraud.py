from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.fraud_service import detect_fraud

router = APIRouter(prefix="/api/fraud", tags=["Fraud"])

class FraudInput(BaseModel):
    face_match_score: float = 1.0
    liveness_passed: bool = True
    declared_age: int = 30
    estimated_age: int = 30
    declared_city: str = ""
    ip_city: str = ""
    voice_confidence: float = 1.0
    pan_used_before: bool = False
    session_duration_seconds: int = 60
    consent_captured: bool = True

@router.post("")
async def detect_fraud_route(data: FraudInput):
    result = detect_fraud(data.model_dump())
    return result
