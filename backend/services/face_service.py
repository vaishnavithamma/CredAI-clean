from deepface import DeepFace

def verify_faces(img1_path: str, img2_path: str) -> dict:
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=False
        )
        
        threshold = result.get("threshold", 0.40)
        distance  = result.get("distance", 1.0)
        # Normalize: 1.0 when distance=0, 0.0 when distance=threshold
        match_score = max(0.0, 1.0 - (distance / threshold)) if threshold > 0 else 0.0
        
        return {
            "success": True,
            "verified": result.get("verified", False),
            "distance": distance,
            "threshold": result.get("threshold", 0.40),
            "match_score": match_score
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

from deepface import DeepFace

def analyze_face(img_path: str) -> dict:
    try:
        from PIL import Image

        # 🔥 Load image safely
        img = Image.open(img_path).convert("RGB")

        # 🔥 Single stable call (NO splitting)
        result = DeepFace.analyze(
            img_path=img,
            actions=["age", "gender", "emotion"],
            enforce_detection=False
        )

        if isinstance(result, list):
            result = result[0]

        return {
            "success": True,
            "estimated_age": result.get("age", 0),
            "gender": result.get("dominant_gender", "Unknown"),
            "emotion": result.get("dominant_emotion", "Unknown"),
            "emotion_scores": result.get("emotion", {})
        }

    except Exception as e:
        print("DeepFace ERROR:", str(e))
        return {
            "success": False,
            "error": str(e)
        }
    