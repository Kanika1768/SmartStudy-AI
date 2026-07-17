import os
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)

def generate_quiz(chunk_text, retries=3, delay=10):
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
    
    for attempt in range(3):       
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(10) 
    
    return None  
if __name__ == "__main__":
    from pdf_processor import extract_text_from_pdf, chunk_text as chunk_fn
    text=extract_text_from_pdf("../test.pdf")
    chunks=chunk_fn(text)
    print(f"Total chunks: {len(chunks)}")
    quiz = generate_quiz(chunks[0])  