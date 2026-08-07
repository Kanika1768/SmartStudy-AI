from pydantic import BaseModel


class FlashcardRequest(BaseModel):
    document_text: str