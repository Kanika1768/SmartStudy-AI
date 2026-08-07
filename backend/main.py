from fastapi import FastAPI
from backend.routers import quiz

app = FastAPI(
    title="SmartStudy AI API",
    version="1.0.0"
)

app.include_router(
    quiz.router,
    prefix="/quiz",
    tags=["Quiz"]
)


@app.get("/")
def home():
    return {
        "message": "SmartStudy AI Backend Running "
    }