"""Provider boundary: rate limit, timeout client, JSON parsing, and controlled retry."""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.clients.groq_client import GroqClient
from app.core.config import settings
from app.exceptions.ai_exception import AIRateLimitError, AIResponseValidationError

SchemaT = TypeVar("SchemaT", bound=BaseModel)


@dataclass(frozen=True)
class GatewayResponse:
    content: BaseModel
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


class AIGateway:
    """Keeps Groq-specific transport details out of ESG domain services."""

    _request_times: dict[int, deque[float]] = defaultdict(deque)

    def __init__(self, client: GroqClient | None = None) -> None:
        self.client = client or GroqClient()

    @classmethod
    def _reserve_request(cls, organization_id: int) -> None:
        now = time.monotonic()
        timestamps = cls._request_times[organization_id]
        cutoff = now - settings.AI_RATE_LIMIT_WINDOW_SECONDS
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()
        if len(timestamps) >= settings.AI_RATE_LIMIT_REQUESTS:
            raise AIRateLimitError("AI request limit reached; try again shortly")
        timestamps.append(now)

    def generate(
        self,
        *,
        organization_id: int,
        system_prompt: str,
        user_prompt: str,
        response_model: type[SchemaT],
    ) -> GatewayResponse:
        self._reserve_request(organization_id)
        started = time.perf_counter()
        last_error: Exception | None = None
        for attempt in range(2):
            prompt = user_prompt
            if attempt:
                prompt = (
                    f"{user_prompt}\n\nRETRY: The previous output did not validate. "
                    "Return only one JSON object exactly matching the required fields and allowed IDs."
                )
            raw = self.client.generate_json(system_prompt, prompt)
            try:
                payload = self._parse_content(raw["choices"][0]["message"]["content"])
                content = response_model.model_validate(payload)
                usage = raw.get("usage") or {}
                return GatewayResponse(
                    content=content,
                    model=str(raw.get("model") or settings.GROQ_MODEL),
                    input_tokens=int(usage.get("prompt_tokens") or 0),
                    output_tokens=int(usage.get("completion_tokens") or 0),
                    latency_ms=round((time.perf_counter() - started) * 1000),
                )
            except (KeyError, TypeError, ValueError, ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
        raise AIResponseValidationError("AI response did not match the structured contract") from last_error

    @staticmethod
    def _parse_content(content: str) -> dict:
        normalized = content.strip()
        if normalized.startswith("```"):
            normalized = normalized.split("\n", 1)[-1]
            normalized = normalized.rsplit("```", 1)[0].strip()
        parsed = json.loads(normalized)
        if not isinstance(parsed, dict):
            raise ValueError("AI JSON root must be an object")
        return parsed
