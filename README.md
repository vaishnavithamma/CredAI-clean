# CredAI 🚀

![CredAI Logo](frontend/assets/logo.svg) <!-- (Placeholder path) -->

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.3.0-blue.svg)](https://lightgbm.readthedocs.io/en/latest/)
[![DeepFace](https://img.shields.io/badge/DeepFace-0.0.93-orange.svg)](https://github.com/serengil/deepface)

**CredAI** is an AI-Powered Video-Based Loan Onboarding & Risk Assessment System.

## Problem Statement

Indian banks and NBFCs lose billions to fake identity fraud and loan defaults in digital lending. Manual KYC is slow, expensive, and error-prone. 

## Solution Overview

This system automates the entire onboarding using AI in under 3 minutes. It replaces manual loan KYC with an AI video onboarding flow that verifies identity, captures customer data, scores risk, detects fraud, and generates instant loan offers.

## Architecture

```text
+-------------------+       +-------------------+       +-------------------+
|   Web Frontend    | <---> |   FastAPI Backend | <---> | ML Models & Logic |
| (HTML, CSS, JS)   |       |                   |       | (DeepFace, LightGBM)|
+-------------------+       +-------------------+       +-------------------+
        ^                           ^                           ^
        |                           |                           |
  Video KYC UI              Route Controllers             Risk, Fraud, Face
  Admin Dashboard                                         Detection Services
```

## Setup Instructions

1. **Clone / open project**
   Navigate to the project root directory.

2. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. **Run the Backend Server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Access the Application**
   Open `frontend/index.html` in your browser. (The backend also mounts the frontend as static files, so you can access it via `http://127.0.0.1:8000/` once the backend is running).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check — returns status and models_loaded |
| POST | `/api/risk` | Risk score prediction — accepts applicant financial data |
| POST | `/api/fraud` | Fraud detection — accepts session signals |
| POST | `/api/face-verify` | Face match — accepts 2 image files |
| POST | `/api/face-analyze` | Face analysis — accepts 1 image file, returns age/gender/emotion |
| POST | `/api/session/start` | Start new onboarding session — returns session_id |
| POST | `/api/session/complete` | Complete session — runs risk + fraud, returns full decision |

## ML Models Used

- **Risk Scoring:** LightGBM trained on Home Credit Default dataset.
- **Face Recognition:** DeepFace (Facenet) for high accuracy identity verification.
- **Fraud Detection:** Rule-based expert system utilizing multi-signal analysis.

## Team
- **CredAI Team**
- **Vibethon 2026**
- **NMIT Bengaluru**

## Team Members-contributed to this project
- **T Vaishnavi**
- **Ramya RS**
- **Ganesh**
- **Harshavaradan Reddy HM**