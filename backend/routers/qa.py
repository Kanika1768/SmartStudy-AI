from fastapi import APIRouter

from backend.models.qa_models import QARequest
from src.qa_engine import answer_question

router = APIRouter()


@router.post("/ask")
def ask_question(request: QARequest):

    result = answer_question(
        request.question
    )

    return result