from fastapi import APIRouter

from backend.models.quiz_models import QuizRequest

from src.quiz_generator import generate_quiz


router = APIRouter()


@router.get("/")
def get_quiz():
    return {
        "message": "Quiz API Working!"
    }


@router.post("/generate")
def generate_quiz_api(request: QuizRequest):

    quiz = generate_quiz(
        request.document_text,
        difficulty=request.difficulty,
        num_questions=request.num_questions
    )

    return {
        "quiz": quiz
    }