import os
import time
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_summary(
    chunk_text,
    retries=3,
    delay=10
):

    prompt = f"""
You are SmartStudy AI.

Generate a study summary using ONLY the study material below.

Return ONLY valid JSON.

Do not wrap the JSON inside markdown code blocks like ```json.

Format:

{{
    "summary":"...",

    "key_concepts":[
        "...",
        "...",
        "..."
    ],

    "definitions":[
        "...",
        "...",
        "..."
    ],

    "exam_tips":[
        "...",
        "...",
        "..."
    ]
}}

Rules:

- Summary should be around 150-200 words.
- Key concepts should contain 5-8 important topics.
- Definitions should contain 5 short definitions.
- Exam tips should contain 5 practical revision tips.
- Do NOT hallucinate.
- Use ONLY the provided study material.

Study Material:

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

            print(f"Attempt {attempt+1} failed: {e}")

            time.sleep(delay)

    return None

if __name__ == "__main__":

    sample = """
    Operating systems manage hardware resources and processes.
    """

    print(generate_summary(sample))