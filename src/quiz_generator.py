import os
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)

def generate_quiz(
    chunk_text,
    difficulty="Medium",
    retries=3,
    delay=10
):
    prompt = f"""
    You are SmartStudy AI's quiz generator.

    Create a {difficulty} level quiz using ONLY the study material below.

    Difficulty Guidelines

    Easy
    - Simple recall questions
    - Definitions
    - Basic factual MCQs

    Medium
    - Conceptual understanding
    - Compare concepts
    - Simple reasoning

    Hard
    - Analytical thinking
    - Scenario-based questions
    - Application of concepts

    Requirements

    Generate exactly 3 questions.

    - 2 MCQs (4 options each)
    - 1 Short Answer

    Return ONLY valid JSON.

    Use this format:

    [
    {{
        "type":"mcq",
        "question":"...",
        "options":["...","...","...","..."],
        "answer":"..."
        }},
    {{
        "type":"mcq",
        "question":"...",
        "options":["...","...","...","..."],
        "answer":"..."
    }},
    {{
        "type":"short_answer",
        "question":"...",
        "answer":"..."
    }}
    ]

    Study Material
    {chunk_text}
    """
    
    for attempt in range(retries):       
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay) 
    
    return None  
if __name__ == "__main__":
    from pdf_processor import extract_text_from_pdf, chunk_text as chunk_fn
    text=extract_text_from_pdf("../test.pdf")
    chunks=chunk_fn(text)
    print(f"Total chunks: {len(chunks)}")
    quiz = generate_quiz(chunks[0])  