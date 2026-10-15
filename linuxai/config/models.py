from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ProviderConfig:
    provider: str
    model: str
    api_key: str = field(repr=False)
    base_url: Optional[str] = None


@dataclass
class StoredConfig:
    active_provider: Optional[str] = None
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
