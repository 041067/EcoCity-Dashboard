"""Small synchronous HTTP helper used exclusively by external ESG data clients."""

from collections.abc import Mapping
from time import monotonic
from urllib.parse import urlparse

import httpx

from app.core.config import settings


class ProviderClientError(RuntimeError):
    def __init__(self, provider: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


def require_https_url(value: str, provider: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ProviderClientError(provider, "Provider URL must be a valid HTTPS URL")
    return value


def get_json(
    provider: str,
    url: str,
    *,
    params: Mapping[str, str | float | int] | None = None,
    headers: Mapping[str, str] | None = None,
) -> tuple[dict, int]:
    """Fetch JSON with a bounded retry for transient provider failures."""

    require_https_url(url, provider)
    last_error: Exception | None = None
    for attempt in range(2):
        started = monotonic()
        try:
            response = httpx.get(
                url,
                params=params,
                headers=headers,
                timeout=settings.ESG_PROVIDER_TIMEOUT_SECONDS,
            )
            duration_ms = int((monotonic() - started) * 1000)
            if response.status_code == 429 or response.status_code >= 500:
                last_error = ProviderClientError(provider, "Provider temporarily unavailable", response.status_code)
                if attempt == 0:
                    continue
                raise last_error
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ProviderClientError(provider, "Provider returned an invalid JSON object")
            return data, duration_ms
        except (httpx.TimeoutException, httpx.NetworkError):
            last_error = ProviderClientError(provider, "Provider request timed out")
        except httpx.HTTPStatusError as exc:
            raise ProviderClientError(provider, "Provider returned an HTTP error", exc.response.status_code) from exc
        except ValueError as exc:
            raise ProviderClientError(provider, "Provider returned invalid JSON") from exc
    if isinstance(last_error, ProviderClientError):
        raise last_error
    raise ProviderClientError(provider, "Provider request failed")
