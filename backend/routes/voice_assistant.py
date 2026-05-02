from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.services.question_engine import QuestionEngine
from backend.services.answer_normalizer import AnswerNormalizer

router = APIRouter(prefix="/api/assistant", tags=["Voice Assistant"])
engine = QuestionEngine()
normalizer = AnswerNormalizer()

class NextQuestionRequest(BaseModel):
    language: str
    fields: List[Dict[str, Any]]
    answers: Dict[str, Any]

class MapAnswerRequest(BaseModel):
    field_key: str
    raw_answer: str
    language: str
    field_type: str

@router.post("/next-question")
async def get_next_question(req: NextQuestionRequest):
    return engine.get_next_question(req.fields, req.answers, req.language)

@router.post("/map-answer")
async def map_answer(req: MapAnswerRequest):
    result = normalizer.normalize(
        req.field_key, 
        req.raw_answer, 
        req.language, 
        req.field_type
    )
    return result
