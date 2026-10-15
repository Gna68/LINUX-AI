from __future__ import annotations

from typing import List, Optional

from linuxai.cloud.base import ChatMessage, GetTransport, Transport
from linuxai.config.models import ProviderConfig
from linuxai.prompts.system import SYSTEM_PROMPT


class CloudClient:
    def __init__(self, transport: Optional[Transport] = None, timeout: float = 30.0,
                 get_transport: Optional[GetTransport] = None):
        self.transport = transport
        self.get_transport = get_transport
        self.timeout = timeout

    def _provider(self, config: ProviderConfig):
        from linuxai.providers import get_provider  # import lokal: hindari siklus

        return get_provider(config.provider, transport=self.transport, timeout=self.timeout,
                            get_transport=self.get_transport)

    def list_models(self, config: ProviderConfig) -> List[str]:
        return self._provider(config).list_models(config)

    def send(self, config: ProviderConfig, messages: List[ChatMessage], system_prompt: str = SYSTEM_PROMPT) -> str:
        return self._provider(config).chat(config, messages, system_prompt)

    def test(self, config: ProviderConfig) -> None:
        """Permintaan uji sederhana. Tidak memuat data percakapan apa pun."""
        self.send(
            config,
            [ChatMessage("user", "Balas hanya dengan satu kata: OK")],
            system_prompt="Balas dengan singkat.",
        )
