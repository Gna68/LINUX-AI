"""Provider berformat OpenAI Chat Completions (OpenAI, OpenRouter, server kompatibel)."""
from __future__ import annotations

from typing import List, Optional, Tuple

from linuxai.cloud.base import ChatMessage, ErrorKind, Provider, ProviderError
from linuxai.config.models import ProviderConfig


class OpenAICompatibleProvider(Provider):
    id = "openai-compatible"
    label = "Provider kompatibel OpenAI API"
    docs_url = "https://platform.openai.com/docs/models"
    needs_base_url = True
    default_base_url = "https://api.openai.com/v1"

    def base_url_for(self, config: ProviderConfig) -> str:
        return (config.base_url or self.default_base_url or "").rstrip("/")

    def build_request(
        self, config: ProviderConfig, messages: List[ChatMessage], system_prompt: str
    ) -> Tuple[str, dict, dict]:
        url = self.base_url_for(config) + "/chat/completions"
        headers = {"Authorization": f"Bearer {config.api_key}"}
        payload = {
            "model": config.model,
            "messages": [{"role": "system", "content": system_prompt}]
            + [{"role": m.role, "content": m.content} for m in messages],
        }
        return url, headers, payload

    def models_request(self, config: ProviderConfig) -> Tuple[str, dict]:
        return self.base_url_for(config) + "/models", {"Authorization": f"Bearer {config.api_key}"}

    def parse_models(self, data: Optional[dict]) -> List[str]:
        if not isinstance(data, dict) or not isinstance(data.get("data"), list):
            raise ProviderError(ErrorKind.BAD_RESPONSE)
        return [m["id"] for m in data["data"] if isinstance(m, dict) and isinstance(m.get("id"), str)]

    def extract_text(self, data: Optional[dict]) -> str:
        if not isinstance(data, dict):
            raise ProviderError(ErrorKind.BAD_RESPONSE)
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            err = data.get("error")
            if err:
                code = err.get("code") if isinstance(err, dict) else None
                if code in (401, 403):
                    raise ProviderError(ErrorKind.AUTH)
                if code == 404:
                    raise ProviderError(ErrorKind.MODEL_NOT_FOUND)
                if code == 429:
                    raise ProviderError(ErrorKind.RATE_LIMIT)
                raise ProviderError(ErrorKind.BAD_REQUEST, status=code if isinstance(code, int) else 0)
            raise ProviderError(ErrorKind.EMPTY)
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(
                p.get("text", "") for p in content if isinstance(p, dict) and isinstance(p.get("text"), str)
            )
        text = content.strip() if isinstance(content, str) else ""
        if text:
            return text
        if message.get("tool_calls") or message.get("function_call"):
            raise ProviderError(ErrorKind.TOOL_IGNORED)
        raise ProviderError(ErrorKind.EMPTY)
