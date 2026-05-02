# CredAI — Project Progress & Context Brain
> Last Updated: 2026-05-02T17:42:00+05:30
> Agent must read this entire file before making ANY changes to the project.

---

## 🧠 WHAT IS THIS PROJECT

**Project Name:** CredAI — AI-Powered Video-Based Loan Onboarding & Risk Assessment System
**Demo Name:** CredTech
**Hackathon:** Vibethon 2026 @ NMIT Bengaluru, India
**Team:** Ramya RS (3rd year AI/ML Engineering student, Bengaluru)
**Domain:** FinTech + Computer Vision + Machine Learning + NLP + Full-Stack Web

**One-line summary:**
A smart digital lending platform that uses a live video call to verify
identity (face recognition + liveness), capture customer data via voice (STT),
score credit risk (LightGBM), detect fraud (rule engine), and generate
instant personalized loan offers — with zero paperwork.

**Problem being solved:**
Indian banks and NBFCs lose billions to fake identity fraud and loan defaults
in digital lending. Manual KYC is slow, expensive, and error-prone. This
system automates the entire onboarding using AI in under 3 minutes.

---

## 📁 PROJECT FOLDER STRUCTURE
CredTech/ ← ROOT (Desktop)
├── backend/
│ ├── models/ ← ✅ TRAINED ML MODELS (DO NOT MODIFY)
│ │ ├── risk_model.pkl ← LightGBM trained on Home Credit Default dataset
│ │ ├── label_encoders.pkl ← sklearn LabelEncoders for categorical features
│ │ └── model_features.json ← ordered list of 25 feature names for prediction
│ ├── routes/
│ │ ├── __init__.py
│ │ ├── risk.py ← POST /api/risk
│ │ ├── fraud.py ← POST /api/fraud
│ │ ├── face.py ← POST /api/face-verify, /api/face-analyze
│ │ └── session.py ← POST /api/session/start, /api/session/complete
│ ├── services/
│ │ ├── __init__.py
│ │ ├── risk_service.py ← loads pkl, runs LightGBM prediction
│ │ ├── fraud_service.py ← rule-based fraud scoring engine
│ │ └── face_service.py ← DeepFace verify + analyze wrappers
│ ├── main.py ← FastAPI app entry point
│ └── config.py ← paths, constants
├── frontend/
│ ├── index.html ← Landing page
│ ├── onboarding.html ← Video KYC 4-step flow
│ ├── result.html ← Loan result page
│ ├── dashboard.html ← Admin dashboard
│ ├── css/
│ │ └── style.css ← Complete design system
│ └── js/
│ ├── app.js ← Core app logic + charts + animations
│ ├── video.js ← Webcam + step navigation + form handling
│ └── api.js ← All fetch() calls to backend
├── requirements.txt
├── .env
├── README.md
└── progress.md ← THIS FILE — project brain

---

## 🤖 ML MODELS — ALREADY TRAINED (DO NOT RETRAIN)

### Model 1: Risk Scoring — LightGBM ✅
- **File:** backend/models/risk_model.pkl
- **Trained on:** Home Credit Default Risk dataset (Kaggle) — 307,511 rows
- **Features used:** 25 features including income, credit amount, age, employment,
  bureau scores (EXT_SOURCE_1/2/3), education, employment type, engineered ratios
- **Performance:** ROC-AUC ~0.76, early stopping at ~400 iterations
- **Output:** risk_probability (0-1), risk_band (LOW/MEDIUM/HIGH/VERY_HIGH),
  decision (APPROVED/APPROVED_WITH_CONDITIONS/MANUAL_REVIEW/REJECTED),
  loan_offer (amount, interest_rate, tenure_months=36, emi)
- **Interest rate formula:** 10 + risk_prob * 20 (so 10% for safest, 30% for riskiest)
- **EMI formula:** P * r * (1+r)^n / ((1+r)^n - 1)

### Model 2: Face Recognition — DeepFace (pretrained, no training needed) ✅
- **Library:** deepface==0.0.93
- **Model used:** Facenet
- **Backend:** opencv (NOT retinaface — too slow)
- **enforce_detection:** False (critical — crashes without this on LFW crops)
- **Function verify:** returns verified(bool), distance(float), threshold(float)
- **Function analyze:** returns estimated_age, dominant_gender, dominant_emotion
- **Dataset tested on:** LFW (Labeled Faces in the Wild) via sklearn

### Model 3: Fraud Detection — Rule Engine ✅
- **Type:** Weighted rule-based scoring (no training needed)
- **Rules and weights:**
  - face_match_score < 0.40 → +40 (CRITICAL)
  - face_match_score < 0.65 → +20 (WARNING)
  - liveness_passed == False → +45 (CRITICAL)
  - age_gap > 10 years → +30
  - age_gap > 6 years → +15
  - city mismatch → +20
  - voice_confidence < 0.35 → +15
  - PAN reuse → +50 (CRITICAL)
  - session < 30 seconds → +20
  - no consent → +25
- **Output:** fraud_score(0-100), fraud_level(CLEAN/LOW/MEDIUM/HIGH), block(bool)

---

## 🎨 DESIGN SYSTEM

### Color Palette
- Background primary: #0a0f1e (deep navy)
- Background secondary: #0d1526
- Card background: rgba(255,255,255,0.05) — glassmorphism
- Accent blue: #00d4ff (primary CTA, highlights)
- Accent violet: #7c3aed (secondary, gradients)
- Accent teal: #00d4aa (success states)
- Alert red: #ff4757 (errors, fraud alerts)
- Text primary: #f0f4ff
- Text secondary: #8892a4
- Border: rgba(255,255,255,0.1)

### Typography
- Font: Inter (Google Fonts CDN)
- NO external CSS frameworks (no Bootstrap, no Tailwind)
- All CSS written from scratch in frontend/css/style.css

### UI Patterns
- Glassmorphism cards: backdrop-filter blur(20px), rgba(255,255,255,0.05) bg
- Animated gradient blob background on every page
- Smooth transitions: 0.3s ease everywhere
- Hover lift effect on cards: translateY(-4px) + glow shadow
- Circular gauge components for risk/fraud scores
- Mobile-responsive at 768px and 375px

---

## ⚙️ TECH STACK

### Backend
- Python 3.10
- FastAPI 0.111.0
- Uvicorn 0.29.0
- DeepFace 0.0.93
- LightGBM 4.3.0
- scikit-learn 1.4.2
- OpenCV (opencv-python-headless)
- Pandas + NumPy + Pillow

### Frontend
- Pure HTML5 + CSS3 + Vanilla JavaScript
- Chart.js (CDN) for dashboard charts
- Google Fonts (Inter) via CDN
- WebRTC getUserMedia for webcam
- NO React, NO Vue, NO framework — pure HTML files

### ML / AI
- LightGBM for risk scoring
- DeepFace (Facenet) for face recognition
- Rule engine for fraud detection
- (Future) Whisper for speech-to-text
- (Future) Wav2Vec2 for voice sentiment

---

## 🔌 API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check — returns {"status":"healthy","models_loaded":true} |
| POST | /api/risk | Risk score prediction — accepts applicant financial data |
| POST | /api/fraud | Fraud detection — accepts session signals |
| POST | /api/face-verify | Face match — accepts 2 image files |
| POST | /api/face-analyze | Face analysis — accepts 1 image file, returns age/gender/emotion |
| POST | /api/session/start | Start new onboarding session — returns session_id |
| POST | /api/session/complete | Complete session — runs risk + fraud, returns full decision |

All endpoints return JSON with "success": true/false field.
Backend runs on: http://127.0.0.1:8000
API docs auto-available at: http://127.0.0.1:8000/docs

---

## 📄 FRONTEND PAGES

| File | Purpose | Key Features |
|------|---------|--------------|
| index.html | Landing page | Hero, How It Works, Features, Tech Stack |
| onboarding.html | Video KYC | 4-step flow, webcam, face analysis, forms |
| result.html | Loan result | Risk gauge, fraud alerts, loan offer card |
| dashboard.html | Admin panel | KPIs, charts, applications table, fraud alerts |

---

## 🚀 HOW TO RUN THE PROJECT

### Start Backend:
```bash
cd Desktop/CredTech/backend
conda activate credai
uvicorn main:app --reload --port 8000
```

### Open Frontend:
Open frontend/index.html directly in Chrome browser.
OR serve with: python -m http.server 3000 (from frontend/ folder)

### Install Dependencies (first time only):
```bash
conda activate credai
pip install -r requirements.txt
```

---

## ✅ COMPLETED TASKS

- [x] Problem statement analyzed (Vibethon PDF + Agentic AI PDF)
- [x] Project architecture designed (8 modules)
- [x] conda environment setup on Windows (Anaconda Prompt method)
- [x] Google Colab notebook created for training
- [x] Risk scoring model trained on Home Credit dataset (LightGBM)
- [x] Face recognition tested (DeepFace + LFW dataset)
- [x] Fraud detection engine coded and tested
- [x] All 3 model files saved and placed in backend/models/
- [x] CredTech project folder created on Desktop
- [x] VS Code opened with Antigravity agent
- [x] Backend file structure defined
- [x] Frontend design system defined
- [x] Create backend/main.py
- [x] Create backend/config.py
- [x] Create backend/services/risk_service.py
- [x] Create backend/services/fraud_service.py
- [x] Create backend/services/face_service.py
- [x] Create backend/routes/risk.py
- [x] Create backend/routes/fraud.py
- [x] Create backend/routes/face.py
- [x] Create backend/routes/session.py
- [x] Create requirements.txt
- [x] Create frontend/css/style.css
- [x] Create frontend/js/app.js
- [x] Create frontend/js/video.js
- [x] Create frontend/js/api.js
- [x] Create frontend/index.html
- [x] Create frontend/onboarding.html
- [x] Create frontend/result.html
- [x] Create frontend/dashboard.html
- [x] README.md
- [x] Test backend startup (uvicorn)
- [x] Test all API endpoints via /docs
- [x] Test frontend pages in browser
- [x] Build standalone Voice eKYC Assistant (credai-voice-kyc.html) connected to backend

---

## 🔲 REMAINING TASKS

- [ ] Final demo walkthrough

---

## ⚠️ KNOWN ISSUES & DECISIONS

1. conda init powershell fails on this machine due to OneDrive profile path.
   SOLUTION: Always use Anaconda Prompt (not PowerShell) for all commands.

2. DeepFace crashes with retinaface backend in some environments.
   SOLUTION: Always use detector_backend="opencv" and enforce_detection=False.

3. Wikipedia and thispersondoesnotexist.com return 403 in Colab.
   SOLUTION: Use sklearn.datasets.fetch_lfw_people() for face test images.

4. risk_model.pkl is a binary file — VS Code shows "unsupported text encoding".
   This is NORMAL — do not try to open or edit .pkl files. Load them with pickle.

5. model_features.json contains exactly 25 feature names in specific order.
   SOLUTION: Always load this JSON and use it to order DataFrame columns before
   passing to the model. Never hardcode the feature list anywhere.

6. risk_model.pkl was found at backend/risk_model.pkl instead of backend/models/.
   SOLUTION: Moved risk_model.pkl to backend/models/ during initialization.

---

## 📝 AGENT INSTRUCTIONS

If you are a new AI agent reading this file, here is what you must do:

1. READ this entire file before doing anything
2. UNDERSTAND the project is a FinTech AI loan platform for a hackathon
3. CHECK which tasks in "REMAINING TASKS" are not yet marked complete
4. DO NOT retrain or modify any .pkl files in backend/models/
5. DO NOT change the model feature list — read from model_features.json
6. FOLLOW the design system exactly (colors, fonts, glassmorphism cards)
7. USE the exact API endpoint paths listed above
8. AFTER every file you create or modify, UPDATE this progress.md:
   - Move the task from REMAINING TASKS to COMPLETED TASKS
   - Add a note under KNOWN ISSUES if you discovered a problem
   - Update the Last Updated timestamp at the top
9. IF you fix a bug, document it under KNOWN ISSUES with the solution
10. ALWAYS use Anaconda Prompt (not PowerShell) in any terminal instructions

---

## 🔄 CHANGE LOG

| Date | Change | Agent |
|------|--------|-------|
| 2026-04-29 | progress.md created, initial state documented | Antigravity |
| 2026-04-29 | Built complete backend, frontend, and config files | Antigravity |
| 2026-05-01 | Setup conda environment, installed dependencies, tested backend and frontend running locally | Antigravity |
| 2026-05-01 | Implemented AI Voice Loan Assistant with UI overlay, TTS/STT Q&A flow, and OCR extraction | Antigravity |
| 2026-05-02 | Created credai-voice-kyc.html standalone web app with real-time Speech API, Face-API and connected to backend LightGBM | Antigravity |
| 2026-05-02 | Fixed webcam crop issue, language fallback for Hindi/Kannada TTS, increased STT silence timeout, and linked from index.html | Antigravity |
| 2026-05-02 | Further optimized webcam size (450px contain) and made Hindi/Kannada TTS matching more robust | Antigravity |

---

*This file is the single source of truth for the CredAI project.
Every agent session must start by reading it and end by updating it.*
