import os
import tempfile
import uuid
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.face_service import verify_faces, analyze_face

router = APIRouter(prefix="/api", tags=["Face"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
_face_executor = ThreadPoolExecutor(max_workers=2)



def save_upload_file_tmp(upload_file: UploadFile) -> str:
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415,
            detail=f"Unsupported file type: {upload_file.content_type}")

    upload_file.file.seek(0, os.SEEK_END)
    file_size = upload_file.file.tell()
    upload_file.file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    suffix = os.path.splitext(upload_file.filename or "")[1] or ".jpg"
    tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return tmp_path

@router.post("/face-verify")
async def face_verify_route(img1: UploadFile = File(...), img2: UploadFile = File(...)):
    img1_path = img2_path = None
    try:
        img1_path = save_upload_file_tmp(img1)
        img2_path = save_upload_file_tmp(img2)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _face_executor, verify_faces, img1_path, img2_path
        )
    finally:
        for path in (img1_path, img2_path):
            if path and os.path.exists(path):
                os.remove(path)

import tempfile
import os

import numpy as np
import cv2

@router.post("/face-analyze")
async def face_analyze_route(image: UploadFile = File(...)):
    try:
        # 🔥 Read image bytes
        contents = await image.read()

        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise Exception("Image decoding failed")

        # ✅ CRITICAL FIX
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 🔥 Run DeepFace directly on numpy image
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _face_executor,
            analyze_face,
            img   # 👈 PASS IMAGE ARRAY (NOT PATH)
        )

        return result

    except Exception as e:
        print("Face Analyze Error:", str(e))
        return {"success": False, "error": str(e)}
    temp_path = None
    try:
        # 🔥 Read file properly
        contents = await image.read()

        # 🔥 Write safely to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            temp_path = tmp.name

        # 🔥 IMPORTANT: Ensure file exists before processing
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise Exception("Image file not written properly")

        # 🔥 Call DeepFace
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _face_executor,
            analyze_face,
            temp_path
        )

        return result

    except Exception as e:
        print("Face Analyze Error:", str(e))
        return {"success": False, "error": str(e)}

    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
