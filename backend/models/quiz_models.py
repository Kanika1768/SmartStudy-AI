from pydantic import BaseModel


class QuizRequest(BaseModel):
    document_text: str
    difficulty: str = "Medium"
    num_questions: int = 3