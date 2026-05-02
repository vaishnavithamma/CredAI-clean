from fastapi import APIRouter, File, UploadFile
import cv2
import numpy as np
from deepface import DeepFace

router = APIRouter(prefix="/api/analysis", tags=["Live Face Analysis"])

@router.post("/live-face-status")
async def live_face_status(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"success": False, "face_detected": False, "message": "Invalid image"}

        # Lighting heuristics
        mean_brightness = np.mean(img)
        if mean_brightness > 180:
            lighting = "good"
        elif mean_brightness > 80:
            lighting = "moderate"
        else:
            lighting = "low — please move to better light"

        # Analyze face (no enforce detection so it doesn't throw if no face)
        result = DeepFace.analyze(img, actions=['age', 'gender', 'emotion'], enforce_detection=False, detector_backend="opencv")
        
        # DeepFace returns list if multiple faces, dict if single.
        if isinstance(result, list):
            res = result[0]
        else:
            res = result
            
        # Check if face was actually detected using face_confidence
        confidence = res.get('face_confidence', 0)
        face_detected = confidence > 0.6
        
        return {
            "success": True,
            "face_detected": face_detected,
            "estimated_age": res.get("age"),
            "gender": res.get("dominant_gender", res.get("gender", "Unknown")),
            "dominant_emotion": res.get("dominant_emotion"),
            "emotion_scores": res.get("emotion", {}),
            "lighting": lighting,
            "liveness_status": "active" if face_detected else "checking",
            "face_confidence": confidence
        }

    except Exception as e:
        print(f"Live Face Analysis Error: {e}")
        return {"success": True, "face_detected": False, "message": "Please position your face in the camera"}
