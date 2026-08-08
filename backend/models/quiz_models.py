from pydantic import BaseModel


class QuizRequest(BaseModel):
    document_name: str
    difficulty: str = "Medium"
    num_questions: int = 3