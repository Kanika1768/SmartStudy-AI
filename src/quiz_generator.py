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
    num_questions=3,
    retries=3,
    delay=10
):
    prompt = f"""
You are SmartStudy AI's quiz generator.

Create a {difficulty} level quiz using ONLY the study material below.

Difficulty Guidelines

Easy
- Ask only simple recall questions.
- Focus on definitions, facts, and basic concepts.
- Avoid reasoning or application.

Medium
- Ask conceptual questions.
- Include comparison and understanding-based questions.
- Require basic reasoning.

Hard
- Ask analytical and application-based questions.
- Include scenario or case-based questions.
- Require deeper understanding rather than direct recall.

Requirements

Generate exactly {num_questions} questions.

Use approximately:
- 70% MCQs (4 options each)
- 30% Short Answer questions.

Return ONLY valid JSON.

The output must be a JSON array containing exactly {num_questions} question objects.

Each question must follow one of these formats:

MCQ:
{{
    "type": "mcq",
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer": "..."
}}

Short Answer:
{{
    "type": "short_answer",
    "question": "...",
    "answer": "..."
}}

Study Material:
{chunk_text}
"""

    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            return response.text

        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt + 1} failed: {last_error}")

            if attempt < retries - 1:
                time.sleep(delay)

    return f"ERROR: {last_error}"


if __name__ == "__main__":
    from pdf_processor import extract_text_from_pdf, chunk_text as chunk_fn
    text=extract_text_from_pdf("../test.pdf")
    chunks=chunk_fn(text)
    print(f"Total chunks: {len(chunks)}")
    quiz = generate_quiz(chunks[0])  