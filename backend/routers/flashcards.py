from fastapi import APIRouter

from backend.models.flashcard_models import FlashcardRequest

from src.flashcard_generator import generate_flashcards

router = APIRouter()


@router.post("/generate")
def generate_flashcards_api(request: FlashcardRequest):

    flashcards = generate_flashcards(
        request.document_text
    )

    return {
        "flashcards": flashcards
    }