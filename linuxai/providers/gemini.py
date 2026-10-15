from __future__ import annotations

from typing import List, Optional, Tuple
from urllib.parse import quote

from linuxai.cloud.base import ChatMessage, ErrorKind, Provider, ProviderError
from linuxai.config.models import ProviderConfig

BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(Provider):
    id = "gemini"
    label = "Google Gemini API"
    docs_url = "https://ai.google.dev/gemini-api/docs/models"

    def build_request(
        self, config: ProviderConfig, messages: List[ChatMessage], system_prompt: str
    ) -> Tuple[str, dict, dict]:
        model = config.model.strip()
        if model.startswith("models/"):
            model = model[len("models/"):]
        url = f"{BASE}/models/{quote(model, safe='')}:generateContent"
        headers = {"x-goog-api-key": config.api_key}
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]}
                for m in messages
            ],
        }
        return url, headers, payload

    def models_request(self, config: ProviderConfig) -> Tuple[str, dict]:
        return f"{BASE}/models?pageSize=1000", {"x-goog-api-key": config.api_key}

    def parse_models(self, data: Optional[dict]) -> List[str]:
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise ProviderError(ErrorKind.BAD_RESPONSE)
        out = []
        for item in data["models"]:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                continue
            methods = item.get("supportedGenerationMethods")
            if isinstance(methods, list) and "generateContent" not in methods:
                continue
            name = item["name"]
            out.append(name[len("models/"):] if name.startswith("models/") else name)
        return out

    def extract_text(self, data: Optional[dict]) -> str:
        if not isinstance(data, dict):
            raise ProviderError(ErrorKind.BAD_RESPONSE)
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            feedback = data.get("promptFeedback")
            if isinstance(feedback, dict) and feedback.get("blockReason"):
                raise ProviderError(ErrorKind.BLOCKED)
            raise ProviderError(ErrorKind.EMPTY)
        first = candidates[0] if isinstance(candidates[0], dict) else {}
        content = first.get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        texts, tool_requested = [], False
        for part in parts or []:
            if not isinstance(part, dict):
                continue
            if isinstance(part.get("text"), str):
                texts.append(part["text"])
            elif "functionCall" in part or "executableCode" in part:
                tool_requested = True
        text = "".join(texts).strip()
        if text:
            return text
        if tool_requested:
            raise ProviderError(ErrorKind.TOOL_IGNORED)
        if first.get("finishReason") in ("SAFETY", "RECITATION", "PROHIBITED_CONTENT", "BLOCKLIST"):
            raise ProviderError(ErrorKind.BLOCKED)
        raise ProviderError(ErrorKind.EMPTY)
