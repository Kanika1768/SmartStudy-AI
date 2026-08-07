from fastapi import FastAPI
from backend.routers import quiz
from backend.routers import flashcards
from backend.routers import summary

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

@app.get("/")
def home():
    return {
        "message": "SmartStudy AI Backend Running "
    }