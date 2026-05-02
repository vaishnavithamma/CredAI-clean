import os
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi import APIRouter
from datetime import datetime, timezone
from collections import deque
import threading

def require_admin_key(x_admin_key: str = Header(...)):
    expected = os.getenv("ADMIN_API_KEY")
    if not expected or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_key)]
)

# In-memory application log (thread-safe, max 500 entries)
_app_lock = threading.Lock()
_applications = deque(maxlen=500)

def log_application(session_id: str, applicant_data: dict,
                     risk_result: dict, fraud_result: dict,
                     final_decision: str):
    """Called from session.py after every /session/complete."""
    with _app_lock:
        _applications.appendleft({
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": applicant_data.get("fullname", "Unknown"),
            "risk_score": risk_result.get("risk_score", 0),
            "risk_band": risk_result.get("risk_band", ""),
            "fraud_score": fraud_result.get("fraud_score", 0),
            "fraud_level": fraud_result.get("fraud_level", ""),
            "decision": final_decision,
            "blocked": fraud_result.get("block", False),
            "alerts": fraud_result.get("alerts", [])
        })

@router.get("/stats")
async def get_stats():
    with _app_lock:
        apps = list(_applications)
    total = len(apps)
    if total == 0:
        return {"total": 0, "approved": 0, "rejected": 0, "review": 0,
                "blocked": 0, "approval_rate": 0, "block_rate": 0}
    approved = sum(1 for a in apps if "APPROVED" in a["decision"]
                   and "FRAUD" not in a["decision"])
    blocked  = sum(1 for a in apps if a["blocked"])
    review   = sum(1 for a in apps if "REVIEW" in a["decision"])
    rejected = total - approved - review
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "review": review,
        "blocked": blocked,
        "approval_rate": round(approved / total * 100, 1),
        "block_rate": round(blocked / total * 100, 1)
    }

@router.get("/applications")
async def get_applications(limit: int = 50):
    with _app_lock:
        return {"applications": list(_applications)[:limit]}

@router.get("/fraud-alerts")
async def get_fraud_alerts():
    with _app_lock:
        alerts = [a for a in _applications
                  if a["blocked"] or a["fraud_level"] == "HIGH"]
    return {"alerts": alerts[:50]}
