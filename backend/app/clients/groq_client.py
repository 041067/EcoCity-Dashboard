import httpx
from app.core.config import settings
from app.exceptions.external_api_exception import ExternalApiException
from app.logs.logger import logger


class GroqClient:
    def __init__(self) -> None:
        self.api_key = settings.GROQ_API_KEY

    def generate_insight(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set, skipping insight generation")
            return "Insight generation unavailable: missing API key."

        try:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                },
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info("Groq insight generated successfully")
            return content
        except httpx.HTTPStatusError as e:
            raise ExternalApiException("Groq", "HTTP error", e.response.status_code)
        except httpx.TimeoutException:
            raise ExternalApiException("Groq", "Request timed out", 408)
        except Exception as e:
            raise ExternalApiException("Groq", str(e))
