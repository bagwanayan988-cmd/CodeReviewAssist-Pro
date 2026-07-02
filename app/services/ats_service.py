import os
import re
import requests


class ATSService:

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

    def analyze_resume(self, resume_text: str):

        prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze this resume.

Return ONLY in this format:

ATS Score: <number>/100

Summary:
...

Strengths:
- ...

Weaknesses:
- ...

Missing Keywords:
- ...

Suggestions:
- ...

Resume:

{resume_text}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4.1-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an ATS Resume Expert."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1200
        }

        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        review = response.json()["choices"][0]["message"]["content"]

        score = self.extract_score(review)

        return {
            "success": True,
            "score": score,
            "review": review
        }

    @staticmethod
    def extract_score(review: str):

        match = re.search(r'(\d{1,3})\s*/\s*100', review)

        if match:
            return int(match.group(1))

        return 0