import os
import json
import pickle
import numpy as np
import pandas as pd
import threading
from backend.config import MODELS_DIR

# Global variables to hold models
risk_model = None
label_encoders = None
model_features = None
_model_lock = threading.Lock()

def load_models():
    global risk_model, label_encoders, model_features
    if risk_model is not None:
        return
    
    with _model_lock:
        if risk_model is not None:
            return
        
        with open(os.path.join(MODELS_DIR, "risk_model.pkl"), "rb") as f:
            risk_model = pickle.load(f)
            
        with open(os.path.join(MODELS_DIR, "label_encoders.pkl"), "rb") as f:
            label_encoders = pickle.load(f)
            
        with open(os.path.join(MODELS_DIR, "model_features.json"), "r") as f:
            model_features = json.load(f)

def predict_risk(data: dict) -> dict:
    load_models()
    
    # Base inputs with defaults
    income = float(data.get("income", 0))
    credit_amount = float(data.get("credit_amount", 0))
    annuity = float(data.get("annuity", 0))
    if annuity == 0 and credit_amount > 0:
        # rough estimate if missing
        annuity = credit_amount * 0.05
    goods_price = float(data.get("goods_price", credit_amount))
    age_years = float(data.get("age_years", 30))
    employment_years = float(data.get("employment_years", 5))
    gender = data.get("gender", "F")
    education = data.get("education", "Secondary / secondary special")
    income_type = data.get("income_type", "Working")
    family_status = data.get("family_status", "Married")
    own_car = data.get("own_car", "N")
    own_realty = data.get("own_realty", "Y")
    children = int(data.get("children", 0))
    ext_score_1 = float(data.get("ext_score_1", 0.5))
    ext_score_2 = float(data.get("ext_score_2", 0.5))
    ext_score_3 = float(data.get("ext_score_3", 0.5))

    # Reconstruct original standard features
    days_birth = -int(age_years * 365.25)
    days_employed = -int(employment_years * 365.25) if employment_years >= 0 else 365243
    days_id_publish = -2000 # default
    region_rating_client = 2
    hour_appr_process_start = 12
    live_city_not_work_city = 0

    # Engineered Features
    AGE_YEARS = age_years
    EMPLOYMENT_YEARS = employment_years if employment_years >= 0 else np.nan
    CREDIT_TO_INCOME = credit_amount / income if income > 0 else 0
    ANNUITY_TO_INCOME = annuity / income if income > 0 else 0
    EXT_SCORE_MEAN = np.nanmean([ext_score_1, ext_score_2, ext_score_3])
    
    # Categorical Encoding
    def safe_encode(col_name, val):
        if col_name in label_encoders:
            le = label_encoders[col_name]
            # Handle unseen labels with fallback 0
            if val in le.classes_:
                return le.transform([val])[0]
            else:
                return 0
        return val

    # Build the feature dict
    feature_dict = {
        "AMT_INCOME_TOTAL": income,
        "AMT_CREDIT": credit_amount,
        "AMT_ANNUITY": annuity,
        "AMT_GOODS_PRICE": goods_price,
        "DAYS_BIRTH": days_birth,
        "DAYS_EMPLOYED": days_employed,
        "DAYS_ID_PUBLISH": days_id_publish,
        "EXT_SOURCE_1": ext_score_1,
        "EXT_SOURCE_2": ext_score_2,
        "EXT_SOURCE_3": ext_score_3,
        "CODE_GENDER": safe_encode("CODE_GENDER", gender),
        "NAME_EDUCATION_TYPE": safe_encode("NAME_EDUCATION_TYPE", education),
        "NAME_INCOME_TYPE": safe_encode("NAME_INCOME_TYPE", income_type),
        "NAME_FAMILY_STATUS": safe_encode("NAME_FAMILY_STATUS", family_status),
        "FLAG_OWN_CAR": safe_encode("FLAG_OWN_CAR", own_car),
        "FLAG_OWN_REALTY": safe_encode("FLAG_OWN_REALTY", own_realty),
        "CNT_CHILDREN": children,
        "REGION_RATING_CLIENT": region_rating_client,
        "HOUR_APPR_PROCESS_START": hour_appr_process_start,
        "LIVE_CITY_NOT_WORK_CITY": live_city_not_work_city,
        "AGE_YEARS": AGE_YEARS,
        "EMPLOYMENT_YEARS": EMPLOYMENT_YEARS,
        "CREDIT_TO_INCOME": CREDIT_TO_INCOME,
        "ANNUITY_TO_INCOME": ANNUITY_TO_INCOME,
        "EXT_SCORE_MEAN": float(EXT_SCORE_MEAN)
    }

    # Reorder features using model_features
    ordered_features = {k: feature_dict.get(k, 0) for k in model_features}
    df = pd.DataFrame([ordered_features])
    
    # Prediction
    risk_prob = float(risk_model.predict_proba(df)[0][1]) # probability of default
    
    # Risk Bands
    if risk_prob < 0.20:
        risk_band = "LOW"
        decision = "APPROVED"
    elif risk_prob < 0.40:
        risk_band = "MEDIUM"
        decision = "APPROVED_WITH_CONDITIONS"
    elif risk_prob < 0.60:
        risk_band = "HIGH"
        decision = "MANUAL_REVIEW"
    else:
        risk_band = "VERY_HIGH"
        decision = "REJECTED"
        
    # Loan offer logic
    interest_rate = 10.0 + (risk_prob * 20.0) # 10 to 30 percent
    tenure_months = 36
    r = (interest_rate / 100.0) / 12.0
    n = tenure_months
    P = credit_amount
    if P > 0 and r > 0:
        emi = P * r * ((1+r)**n) / (((1+r)**n) - 1)
    else:
        emi = 0

    return {
        "success": True,
        "risk_score": round(risk_prob * 100, 2),
        "risk_band": risk_band,
        "decision": decision,
        "loan_offer": {
            "amount": round(credit_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "tenure_months": tenure_months,
            "emi": round(emi, 2)
        }
    }
