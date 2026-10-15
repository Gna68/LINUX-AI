"""Penyimpanan konfigurasi di ~/.config/linuxai/ (dir 0700, file 0600).

Catatan: API key disimpan sebagai teks biasa di file ber-izin 0600. Siapa pun
yang punya akses ke akun Linux-mu atau ke disk yang tidak terenkripsi tetap
dapat membacanya. Lihat docs/security.md.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from linuxai.config.models import ProviderConfig, StoredConfig

FILENAME = "config.json"


def config_dir() -> Path:
    override = os.environ.get("LINUXAI_CONFIG_DIR")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "linuxai"


class ConfigStore:
    def __init__(self, directory: Optional[Path] = None):
        self.directory = Path(directory) if directory else config_dir()

    @property
    def path(self) -> Path:
        return self.directory / FILENAME

    def exists(self) -> bool:
        return self.path.exists()

    # ---- baca -------------------------------------------------------
    def load(self) -> StoredConfig:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return StoredConfig()
        if not isinstance(data, dict):
            return StoredConfig()
        providers = {}
        raw = data.get("providers")
        if isinstance(raw, dict):
            for pid, item in raw.items():
                if not isinstance(item, dict):
                    continue
                model, key = item.get("model"), item.get("api_key")
                base = item.get("base_url")
                if isinstance(model, str) and isinstance(key, str) and key:
                    providers[str(pid)] = ProviderConfig(
                        provider=str(pid),
                        model=model,
                        api_key=key,
                        base_url=base if isinstance(base, str) else None,
                    )
        active = data.get("active_provider")
        if active not in providers:
            active = None
        self._harden()
        return StoredConfig(active_provider=active, providers=providers)

    # ---- tulis ------------------------------------------------------
    def save_provider(self, cfg: ProviderConfig, make_active: bool = True) -> None:
        current = self.load()
        current.providers[cfg.provider] = cfg
        if make_active:
            current.active_provider = cfg.provider
        self._write(current)

    def set_active(self, provider_id: Optional[str]) -> None:
        current = self.load()
        current.active_provider = provider_id if provider_id in current.providers else None
        self._write(current)

    def update_model(self, provider_id: str, model: str) -> None:
        current = self.load()
        if provider_id in current.providers:
            current.providers[provider_id].model = model
            self._write(current)

    def remove_provider(self, provider_id: str) -> None:
        current = self.load()
        current.providers.pop(provider_id, None)
        if current.active_provider == provider_id:
            current.active_provider = None
        self._write(current)

    def delete_all(self) -> None:
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass
        try:
            os.rmdir(self.directory)
        except OSError:
            pass

    # ---- internal ---------------------------------------------------
    def _harden(self) -> None:
        try:
            os.chmod(self.directory, 0o700)
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def _write(self, cfg: StoredConfig) -> None:
        os.makedirs(self.directory, mode=0o700, exist_ok=True)
        os.chmod(self.directory, 0o700)
        payload = {
            "version": 1,
            "active_provider": cfg.active_provider,
            "providers": {
                pid: {"model": p.model, "api_key": p.api_key, "base_url": p.base_url}
                for pid, p in cfg.providers.items()
            },
        }
        fd, tmp = tempfile.mkstemp(dir=self.directory, prefix=".config-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
        self._harden()
