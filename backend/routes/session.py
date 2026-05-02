import uuid
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.services.risk_service import predict_risk
from backend.services.fraud_service import detect_fraud, check_and_register_pan
from backend.routes.admin import log_application

router = APIRouter(prefix="/api/session", tags=["Session"])

class SessionCompleteInput(BaseModel):
    session_id: str
    language: str
    answers: Dict[str, Any]
    face_analysis: Dict[str, Any]
    face_match_score: Optional[float] = None
    metadata: Dict[str, Any]

def calculate_days_birth(dob_str):
    try:
        if not dob_str: return -10000
        from dateutil import parser
        dob = parser.parse(dob_str, fuzzy=True).date()
        today = datetime.now().date()
        return (dob - today).days
    except:
        return -10000

def map_answers_to_features(answers: dict) -> dict:
    # Safely get values
    income = float(answers.get("monthly_income") or 0)
    loan_amt = float(answers.get("loan_amount") or 100000)
    tenure = max(float(answers.get("loan_tenure_months") or 12), 1)
    
    # We must match EXACTLY this order from model_features.json:
    # ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_ID_PUBLISH", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "CODE_GENDER", "NAME_EDUCATION_TYPE", "NAME_INCOME_TYPE", "NAME_FAMILY_STATUS", "FLAG_OWN_CAR", "FLAG_OWN_REALTY", "CNT_CHILDREN", "REGION_RATING_CLIENT", "HOUR_APPR_PROCESS_START", "LIVE_CITY_NOT_WORK_CITY", "AGE_YEARS", "EMPLOYMENT_YEARS", "CREDIT_TO_INCOME", "ANNUITY_TO_INCOME", "EXT_SCORE_MEAN"]
    
    days_birth = calculate_days_birth(answers.get("dob", ""))
    age_years = abs(days_birth) / 365.25
    employment_years = float(answers.get("work_experience_years") or 1)
    
    features = {
        "AMT_INCOME_TOTAL": income * 12,
        "AMT_CREDIT": loan_amt,
        "AMT_ANNUITY": loan_amt / tenure,
        "AMT_GOODS_PRICE": loan_amt,
        "DAYS_BIRTH": days_birth,
        "DAYS_EMPLOYED": employment_years * -365,
        "DAYS_ID_PUBLISH": -3650,
        "EXT_SOURCE_1": 0.5,
        "EXT_SOURCE_2": 0.5,
        "EXT_SOURCE_3": 0.5,
        "CODE_GENDER": "F" if answers.get("gender", "Female") == "Female" else "M",
        "NAME_EDUCATION_TYPE": "Secondary / secondary special",
        "NAME_INCOME_TYPE": answers.get("employment_type", "Working"),
        "NAME_FAMILY_STATUS": answers.get("marital_status", "Single / not married"),
        "FLAG_OWN_CAR": "Y" if str(answers.get("own_vehicle", "N")).upper() == "Y" else "N",
        "FLAG_OWN_REALTY": "Y" if str(answers.get("own_property", "N")).upper() == "Y" else "N",
        "CNT_CHILDREN": int(answers.get("dependents", 0)),
        "REGION_RATING_CLIENT": 2,
        "HOUR_APPR_PROCESS_START": 12,
        "LIVE_CITY_NOT_WORK_CITY": 0,
        "AGE_YEARS": age_years,
        "EMPLOYMENT_YEARS": employment_years,
        "CREDIT_TO_INCOME": loan_amt / max(income * 12, 1),
        "ANNUITY_TO_INCOME": (loan_amt / tenure) / max(income * 12, 1),
        "EXT_SCORE_MEAN": 0.5
    }
    return features

@router.post("/start")
async def start_session():
    session_id = str(uuid.uuid4())
    return {
        "success": True,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }

@router.post("/complete")
async def complete_session(data: SessionCompleteInput):
    answers = data.answers
    
    pan = answers.get("pan_number", "")
    if pan:
        pan_duplicate = check_and_register_pan(pan)
        answers["pan_used_before"] = pan_duplicate
    
    # Check age mismatch
    face_age = data.face_analysis.get("estimated_age")
    dob_age = abs(calculate_days_birth(answers.get("dob", ""))) / 365.25
    age_mismatch = False
    if face_age and face_age > 0 and dob_age > 0:
        if abs(face_age - dob_age) > 10:
            age_mismatch = True
    
    # 1. Run fraud detection
    fraud_result = detect_fraud(answers)
    if age_mismatch:
        fraud_result["alerts"].append("Age mismatch between face and stated DOB (>10 years)")
        fraud_result["fraud_score"] = min(1.0, fraud_result.get("fraud_score", 0) + 0.3)
        if fraud_result["fraud_score"] > 0.7:
            fraud_result["block"] = True
    
    # 2. Map features and Run risk prediction
    model_features = map_answers_to_features(answers)
    risk_result = predict_risk(model_features)
    
    # Combine results
    final_decision = risk_result.get("decision", "APPROVED")
    if fraud_result.get("block", False):
        final_decision = "REJECTED_FRAUD"
        
    log_application(data.session_id, answers, risk_result, fraud_result, final_decision)
        
    return {
        "success": True,
        "session_id": data.session_id,
        "applicant_name": answers.get("full_name", "Unknown"),
        "risk_result": risk_result,
        "fraud_result": fraud_result,
        "face_analysis": data.face_analysis,
        "decision": final_decision,
        "application_summary": answers,
        "audit_timestamp": datetime.now(timezone.utc).isoformat()
    }
