import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_flashcards(
    chunk_text,
    num_cards=10,
    retries=3,
    delay=10
):

    prompt = f"""
You are SmartStudy AI's Flashcard Generator.

Generate exactly {num_cards} flashcards
using ONLY the study material below.

Rules

- One concept per flashcard.
- Front should contain a question or keyword.
- Back should contain a short explanation.
- Keep answers concise.
- Do NOT hallucinate.
- Return ONLY valid JSON.

Format:

[
{{
    "front":"What is Deadlock?",
    "back":"Deadlock is a state where..."
}},
{{
    "front":"Paging",
    "back":"Paging is..."
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