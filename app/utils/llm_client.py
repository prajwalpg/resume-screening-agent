"""Minimal OpenAI-compatible chat client.

Works with OpenAI, Groq, Ollama or any OpenAI-compatible endpoint. The
agent is fully functional without an LLM: extraction and explanation fall
back to deterministic heuristics, so this client is strictly optional.
"""

import json
import re
from typing import Optional

from .config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_PROVIDER,
    PROVIDER_DEFAULTS,
)


def parse_json_block(raw: str) -> Optional[dict]:
    """Parse a JSON object out of an LLM response (tolerates code fences)."""
    if not raw:
        return None
    cleaned = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end <= start:
            return None
        cleaned = cleaned[start : end + 1]
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


class LLMClient:
    """Thin wrapper over the OpenAI Python SDK with provider presets."""

    def __init__(
        self,
        provider: str = "",
        model: str = "",
        api_key: str = "",
        base_url: str = "",
    ) -> None:
        self.provider = (provider or LLM_PROVIDER or "").lower()
        defaults = PROVIDER_DEFAULTS.get(self.provider, {})
        self.model = model or LLM_MODEL or defaults.get("model", "")
        self.api_key = api_key or LLM_API_KEY
        self.base_url = base_url or LLM_BASE_URL or defaults.get("base_url", "")
        self._client = None

    # ------------------------------------------------------------------
    def is_available(self) -> bool:
        """True when a provider is configured and reachable in principle."""
        if self.provider == "ollama":
            return True  # Local server: no API key required.
        return bool(self.provider and self.api_key and self.model)

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI  # Lazy import: optional dependency.

            self._client = OpenAI(
                api_key=self.api_key or "not-needed",
                base_url=self.base_url or None,
            )
        return self._client

    # ------------------------------------------------------------------
    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Optional[str]:
        """Return the model reply, or None when unavailable / on failure."""
        if not self.is_available():
            return None
        try:
            response = self._get_client().chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception as exc:  # Network, auth, rate limit, parse...
            print(f"  ! LLM call failed ({exc.__class__.__name__}); using heuristic fallback")
            return None

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Optional[dict]:
        raw = self.chat(system_prompt, user_prompt, temperature)
        return parse_json_block(raw or "")
