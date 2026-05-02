import os
import json
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def classify_customer(transcript: str) -> dict:
    if not GROQ_API_KEY:
        print("WARNING: No GROQ_API_KEY found. Using mock LLM response.")
        return {
            "occupation_confidence": 0.85,
            "income_band": "medium",
            "loan_purpose_category": "personal",
            "customer_persona": "prime",
            "intent_signals": ["Clear communication", "Consistent answers provided"],
            "risk_flags": [],
            "recommended_offer_tier": "standard"
        }
    
    req_data = json.dumps({
        "model": "llama3-8b-8192",
        "response_format": {"type": "json_object"},
        "messages": [{
            "role": "system",
            "content": "You are a risk assessment AI. Respond ONLY with valid JSON."
        }, {
            "role": "user",
            "content": f"""
            Analyze this loan applicant's voice interview transcript and return JSON:
            {{
                "occupation_confidence": 0.9,
                "income_band": "medium",
                "loan_purpose_category": "education",
                "customer_persona": "prime",
                "intent_signals": ["positive signal 1"],
                "risk_flags": [],
                "recommended_offer_tier": "standard"
            }}
            
            Transcript: {transcript}
            """
        }]
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=req_data,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        print(f"LLM Classification Error: {e}")
        return {
            "occupation_confidence": 0.5,
            "income_band": "unknown",
            "loan_purpose_category": "other",
            "customer_persona": "unknown",
            "intent_signals": [],
            "risk_flags": ["LLM Analysis Failed or Unavailable"],
            "recommended_offer_tier": "standard"
        }
