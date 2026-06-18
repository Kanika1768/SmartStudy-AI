import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)


def generate_quiz(chunk_text):
    prompt = f"""
    You are a quiz generator for a study app.
    Based on the following text, create exactly 3 quiz questions.
    Make 2 of them multiple-choice (with 4 options each) and 1 a short-answer question.

    Respond ONLY with valid JSON. Do not include markdown formatting like ```json. 
    Do not include any explanation outside the JSON.

    Use this exact format:
    [
      {{"type": "mcq", "question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}},
      {{"type": "mcq", "question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}},
      {{"type": "short_answer", "question": "...", "answer": "..."}}
    ]

    Text:
    {chunk_text}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text    

if __name__ == "__main__":
    from pdf_processor import extract_text_from_pdf, chunk_text as chunk_fn
    text=extract_text_from_pdf("../test.pdf")
    chunks=chunk_fn(text)
    print(f"Total chunks: {len(chunks)}")
    quiz = generate_quiz(chunks[0])  # Generate quiz for the first chunk
    print(quiz)