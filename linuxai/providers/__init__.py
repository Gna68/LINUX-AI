from __future__ import annotations

from typing import Dict, List, Optional, Type

from linuxai.cloud.base import ErrorKind, GetTransport, Provider, ProviderError, Transport
from linuxai.providers.gemini import GeminiProvider
from linuxai.providers.openai_compat import OpenAICompatibleProvider
from linuxai.providers.openrouter import OpenRouterProvider

PROVIDER_CLASSES: Dict[str, Type[Provider]] = {
    cls.id: cls for cls in (GeminiProvider, OpenRouterProvider, OpenAICompatibleProvider)
}


def provider_ids() -> List[str]:
    return list(PROVIDER_CLASSES)


def get_provider(provider_id: str, transport: Optional[Transport] = None, timeout: float = 30.0,
                 get_transport: Optional[GetTransport] = None) -> Provider:
    cls = PROVIDER_CLASSES.get(provider_id)
    if cls is None:
        raise ProviderError(ErrorKind.CONFIG, "Provider tidak dikenal.")
    return cls(transport=transport, timeout=timeout, get_transport=get_transport)
