from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.risk_service import predict_risk

router = APIRouter(prefix="/api/risk", tags=["Risk"])

class RiskInput(BaseModel):
    income: float
    credit_amount: float
    annuity: float = 0.0
    goods_price: Optional[float] = None
    age_years: float
    employment_years: float
    gender: str = "F"
    education: str = "Secondary / secondary special"
    income_type: str = "Working"
    family_status: str = "Married"
    own_car: str = "N"
    own_realty: str = "Y"
    children: int = 0
    ext_score_1: float = 0.5
    ext_score_2: float = 0.5
    ext_score_3: float = 0.5

@router.post("")
async def assess_risk(data: RiskInput):
    # Convert Pydantic model to dict
    data_dict = data.model_dump(exclude_none=True)
    if "goods_price" not in data_dict:
        data_dict["goods_price"] = data_dict["credit_amount"]
        
    result = predict_risk(data_dict)
    return result
