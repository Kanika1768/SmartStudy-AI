from fastapi import FastAPI
from backend.routers import quiz
from backend.routers import flashcards
from backend.routers import summary
from backend.routers import qa
from backend.routers import documents

app = FastAPI(
    title="SmartStudy AI API",
    version="1.0.0"
)

app.include_router(
    quiz.router,
    prefix="/quiz",
    tags=["Quiz"]
)

app.include_router(
    flashcards.router,
    prefix="/flashcards",
    tags=["Flashcards"]
)

app.include_router(
    summary.router,
    prefix="/summary",
    tags=["Summary"]
)

app.include_router(
    qa.router,
    prefix="/qa",
    tags=["Question Answering"]
)

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

@app.get("/")
def home():
    return {
        "message": "SmartStudy AI Backend Running "
    }