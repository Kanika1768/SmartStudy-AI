from fastapi import APIRouter

from backend.models.quiz_models import QuizRequest

from src.quiz_generator import generate_quiz
from src.qa_engine import retrieve_chunks_by_document

router = APIRouter()


@router.get("/")
def get_quiz():
    return {
        "message": "Quiz API Working!"
    }


@router.post("/generate")
def generate_quiz_api(request: QuizRequest):

    chunks = retrieve_chunks_by_document(
        request.document_name
    )

    

    document_text = "\n\n".join(
    chunk["text"]
    for chunk in chunks
    )

    quiz = generate_quiz(
        document_text,
        difficulty=request.difficulty,
        num_questions=request.num_questions
    )

    return {
        "quiz": quiz
    }