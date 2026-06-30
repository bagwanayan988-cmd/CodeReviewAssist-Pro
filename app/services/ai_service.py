import os
import requests


class AIService:

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set."
            )

    def review_code(self, code: str, language: str):

        prompt = f"""
You are an expert Senior Software Engineer.

Review this {language} code.

Provide:

1. Overall Rating (/10)

2. Summary

3. Bugs

4. Security Issues

5. Performance Improvements

6. Clean Code Suggestions

7. Best Practices

8. Improved Version

Code:

{code}
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
                    "content": "You are an expert code reviewer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1800
        }

        try:

            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "review": data["choices"][0]["message"]["content"]
            }

        except Exception as e:

            return {
                "success": False,
                "review": str(e)
            }