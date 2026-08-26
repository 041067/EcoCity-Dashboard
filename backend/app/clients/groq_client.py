import httpx

from app.core.config import settings
from app.exceptions.ai_exception import AIUnavailableError
from app.logs.logger import logger


class GroqClient:
    def __init__(self) -> None:
        self.api_key = settings.GROQ_API_KEY

    def _complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> dict:
        if not self.api_key:
            raise AIUnavailableError("AI provider is not configured")

        try:
            payload: dict = {
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or settings.AI_MAX_COMPLETION_TOKENS,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result: dict = response.json()
            if not result.get("choices") or not result["choices"][0].get("message", {}).get("content"):
                raise AIUnavailableError("AI provider returned an empty response")
            return result
        except httpx.HTTPStatusError as e:
            raise AIUnavailableError(f"AI provider HTTP status {e.response.status_code}") from e
        except httpx.TimeoutException:
            raise AIUnavailableError("AI provider timed out") from None
        except AIUnavailableError:
            raise
        except Exception as e:
            logger.warning("Groq request failed: %s", type(e).__name__)
            raise AIUnavailableError("AI provider request failed") from e

    def generate_insight(self, prompt: str) -> str:
        """Compatibility method for the pre-Sprint-10 city AI screens."""
        try:
            result = self._complete([{"role": "user", "content": prompt}], temperature=0.5)
            return result["choices"][0]["message"]["content"]
        except AIUnavailableError:
            logger.warning("Legacy AI insight unavailable")
            return "Insight generation temporarily unavailable."

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        return self._complete(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            json_mode=True,
        )
