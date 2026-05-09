_pan_registry: set = set()  # In-memory — resets on restart
# For production: replace with database lookup

def check_and_register_pan(pan_number: str) -> bool:
    """Returns True if PAN was already seen (duplicate). Registers it."""
    pan_clean = pan_number.strip().upper()
    if not pan_clean or len(pan_clean) != 10:
        return False  # Invalid PAN format — don't block
    if pan_clean in _pan_registry:
        return True  # Duplicate
    _pan_registry.add(pan_clean)
    return False

def detect_fraud(data: dict) -> dict:
    fraud_score = 0
    alerts = []
    
    face_match_score = float(data.get("face_match_score", 1.0))
    liveness_passed = data.get("liveness_passed", True)
    declared_age = int(data.get("declared_age", 30))
    estimated_age = int(data.get("estimated_age", 30))
    declared_city = str(data.get("declared_city", "")).lower().strip()
    ip_city = str(data.get("ip_city", "")).lower().strip()
    voice_confidence = float(data.get("voice_confidence", 1.0))
    pan_used_before = data.get("pan_used_before", False)
    session_duration_seconds = int(data.get("session_duration_seconds", 60))
    consent_captured = data.get("consent_captured", True)

    # Face match rules (mutually exclusive ranges based on lowest threshold)
    if face_match_score < 0.40:
        fraud_score += 40
        alerts.append({"rule": "Face Match Critical", "severity": "CRITICAL", "desc": f"Face match confidence is critically low ({int(face_match_score*100)}%). Identity verification failed."})
    elif face_match_score < 0.65:
        fraud_score += 20
        alerts.append({"rule": "Face Match Warning", "severity": "WARNING", "desc": f"Face match confidence is borderline ({int(face_match_score*100)}%)."})

    if not liveness_passed:
        fraud_score += 45
        alerts.append({"rule": "Liveness Failed", "severity": "CRITICAL", "desc": "Motion/Blink liveness check failed. Possible photo spoofing detected."})

    # Age mismatch rules
    age_gap = abs(declared_age - estimated_age)
    if age_gap > 10:
        fraud_score += 30
        alerts.append({"rule": "Age Mismatch > 10", "severity": "HIGH", "desc": f"Declared age ({declared_age}) differs significantly from face analysis ({estimated_age})."})
    elif age_gap > 6:
        fraud_score += 15
        alerts.append({"rule": "Age Mismatch > 6", "severity": "MEDIUM", "desc": f"Declared age ({declared_age}) slightly mismatches face analysis ({estimated_age})."})

    if declared_city and ip_city and declared_city != ip_city:
        fraud_score += 20
        alerts.append({"rule": "Location Mismatch", "severity": "HIGH", "desc": f"GPS City ({ip_city}) does not match declared city ({declared_city})."})

    if voice_confidence < 0.35:
        fraud_score += 15
        alerts.append({"rule": "Low Voice Confidence", "severity": "MEDIUM", "desc": "Speech variance was unnaturally flat or robotic."})

    if pan_used_before:
        fraud_score += 50
        alerts.append({"rule": "Duplicate PAN", "severity": "CRITICAL", "desc": "The uploaded PAN card has been used in previous suspicious applications."})

    if session_duration_seconds < 30:
        fraud_score += 20
        alerts.append({"rule": "Speed Run detected (< 30s)", "severity": "HIGH", "desc": "Application completed unnaturally fast. Possible automated script."})

    if not consent_captured:
        fraud_score += 25
        alerts.append({"rule": "Missing Consent", "severity": "HIGH", "desc": "Explicit verbal consent was not recorded."})

    fraud_score = min(fraud_score, 100)

    # Fraud Levels
    if fraud_score == 0:
        fraud_level = "CLEAN"
    elif fraud_score <= 20:
        fraud_level = "LOW"
    elif fraud_score <= 55:
        fraud_level = "MEDIUM"
    else:
        fraud_level = "HIGH"

    block = fraud_score >= 60

    # Generate Explainable AI Decisions
    explanation = {
        "positives": [],
        "warnings": []
    }
    
    if face_match_score >= 0.8:
        explanation["positives"].append(f"Face match confidence is excellent ({int(face_match_score*100)}%) — identity securely verified.")
    if liveness_passed:
        explanation["positives"].append("Liveness verification passed successfully.")
    if age_gap <= 6:
        explanation["positives"].append(f"Declared age ({declared_age}) is consistent with visual analysis.")
    if declared_city and ip_city and declared_city == ip_city:
        explanation["positives"].append(f"Geo-location securely confirmed: {ip_city.title()}.")
    if consent_captured:
        explanation["positives"].append("Explicit verbal consent captured and timestamped.")
        
    for alert in alerts:
        explanation["warnings"].append(alert.get("desc", alert["rule"]))

    return {
        "success": True,
        "fraud_score": fraud_score,
        "fraud_level": fraud_level,
        "block": block,
        "alerts": alerts,
        "explanation": explanation,
        "face_match_score": face_match_score,
        "voice_confidence": voice_confidence,
        "consent_captured": consent_captured,
        "ip_city": ip_city,
        "estimated_age": estimated_age
    }
