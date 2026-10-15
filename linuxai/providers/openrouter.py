from __future__ import annotations

from linuxai.providers.openai_compat import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    id = "openrouter"
    label = "OpenRouter"
    docs_url = "https://openrouter.ai/models"
    needs_base_url = False
    default_base_url = "https://openrouter.ai/api/v1"

    def base_url_for(self, config) -> str:
        # Base URL OpenRouter dikunci supaya API key tidak bisa dialihkan ke host lain.
        return self.default_base_url
