from fastapi import APIRouter

from backend.models.summary_models import SummaryRequest
from src.summary_generator import generate_summary

router = APIRouter()


@router.post("/generate")
def generate_summary_api(request: SummaryRequest):

    summary = generate_summary(
        request.document_text
    )

    return {
        "summary": summary
    }