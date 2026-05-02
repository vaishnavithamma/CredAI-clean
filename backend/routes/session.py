import uuid
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.services.risk_service import predict_risk
from backend.services.fraud_service import detect_fraud, check_and_register_pan
from backend.services.llm_service import classify_customer
from backend.routes.admin import log_application

router = APIRouter(prefix="/api/session", tags=["Session"])

class CompleteSessionRequest(BaseModel):
    session_id: str
    answers: Dict[str, Any]
    face_match_score: float = 0.95
    liveness_passed: bool = True
    session_duration_seconds: int = 120
    geo_city: str = ""
    voice_confidence: float = 0.95
    consent_captured: bool = False
    full_transcript: str = ""
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
async def complete_session(req: CompleteSessionRequest):
    answers = req.answers
    
    pan = answers.get("pan_number", "")
    pan_used_before = False
    if pan:
        pan_used_before = check_and_register_pan(pan)
    
    # 2. Map features and Run risk prediction
    model_features = map_answers_to_features(answers)
    risk_result = predict_risk(model_features)
    
    # 4. LLM Persona Classification
    llm_classification = classify_customer(req.full_transcript)
    
    # Update fraud checks with new parameters
    age = abs(calculate_days_birth(answers.get("dob", ""))) / 365.25
    estimated_age = req.metadata.get("estimated_age", 0)
    
    fraud_data = {
        "face_match_score": req.face_match_score,
        "liveness_passed": req.liveness_passed,
        "declared_age": age,
        "estimated_age": estimated_age,
        "declared_city": answers.get("city", ""),
        "ip_city": req.geo_city,
        "voice_confidence": req.voice_confidence,
        "pan_used_before": pan_used_before,
        "session_duration_seconds": req.session_duration_seconds,
        "consent_captured": req.consent_captured
    }
    fraud_result = detect_fraud(fraud_data)

    # Base risk score and rate
    base_risk_score = risk_result.get("risk_score", 100)
    base_rate = risk_result.get("loan_offer", {}).get("interest_rate", 15.0)
    
    # Financials from User
    monthly_income = float(answers.get("monthly_income") or 35000)
    requested_amount = float(answers.get("loan_amount") or 100000)
    requested_tenure = max(float(answers.get("loan_tenure_months") or 24), 12.0)
    
    # Standard FOIR (Fixed Obligation to Income Ratio) calculation
    # A user can afford a max EMI of 50% of their monthly income
    max_affordable_emi = monthly_income * 0.50
    
    # Calculate required EMI for the requested amount
    r_monthly = (base_rate / 100.0) / 12.0
    if r_monthly > 0:
        required_emi = requested_amount * r_monthly * ((1 + r_monthly)**requested_tenure) / (((1 + r_monthly)**requested_tenure) - 1)
    else:
        required_emi = requested_amount / requested_tenure

    # Calculate Max Affordable Loan Amount
    if r_monthly > 0:
        max_affordable_loan = (max_affordable_emi * (((1 + r_monthly)**requested_tenure) - 1)) / (r_monthly * ((1 + r_monthly)**requested_tenure))
    else:
        max_affordable_loan = max_affordable_emi * requested_tenure
        
    max_affordable_loan = round(max_affordable_loan, 2)

    # Decision Engine
    tiered_offers = []
    
    if fraud_result["block"] or base_risk_score >= 60:
        final_decision = "REJECTED"
        # No offers
    elif base_risk_score >= 40:
        final_decision = "MANUAL REVIEW"
        # No immediate offers
    else:
        # User is in acceptable risk band (<40)
        if required_emi <= max_affordable_emi:
            final_decision = "APPROVED"
            approved_amount = requested_amount
        else:
            final_decision = "PARTIALLY APPROVED"
            approved_amount = max_affordable_loan
            
        # Build 3-tier realistic offers based on the approved amount limit
        tiered_offers = [
            {"tier": "🏆 Best Offer", "amount": approved_amount, "interest_rate": round(max(base_rate - 1.0, 9.0), 1), "tenure_months": 36},
            {"tier": "⚡ Standard", "amount": approved_amount, "interest_rate": base_rate, "tenure_months": 24},
            {"tier": "🛡️ Safe Option", "amount": min(approved_amount, max_affordable_loan * 0.7), "interest_rate": round(base_rate + 1.5, 1), "tenure_months": 12}
        ]

    # Calculate EMI mathematically for each tier so UI shows real numbers
    for offer in tiered_offers:
        r = (offer["interest_rate"] / 100) / 12
        m = offer["tenure_months"]
        if r > 0 and m > 0:
            emi = offer["amount"] * r * (1 + r)**m / ((1 + r)**m - 1)
            offer["emi"] = round(emi, 2)
        else:
            offer["emi"] = 0

    log_application(
        session_id=req.session_id,
        applicant_data=answers,
        risk_result=risk_result,
        fraud_result=fraud_result,
        final_decision=final_decision
    )

    return {
        "success": True,
        "session_id": req.session_id,
        "timestamp": datetime.now().isoformat(),
        "final_decision": final_decision,
        "risk_assessment": risk_result,
        "fraud_assessment": fraud_result,
        "llm_classification": llm_classification,
        "tiered_offers": tiered_offers
    }
