from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from backend.services.pdf_parser_service import PDFParserService

router = APIRouter(prefix="/api/pdf", tags=["PDF Extraction"])
parser_service = PDFParserService()

@router.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        result = parser_service.parse_pdf(content)
        return result
    except Exception as e:
        print(f"PDF Parse Error: {e}")
        # Fallback to default schema if crash
        return {
            "success": False,
            "error": str(e),
            "total_fields": 0,
            "fields": []
        }
