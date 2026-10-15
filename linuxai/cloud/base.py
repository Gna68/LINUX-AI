"""Antarmuka provider cloud. Hanya mengirim teks dan menerima teks."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Tuple

from linuxai.config.models import ProviderConfig
from linuxai.config.secrets import redact
from linuxai.config.validation import MODEL_RE, ValidationError, validate_api_key, validate_model
from linuxai.safety.text import clean_model_text
from linuxai.utils.http import HttpConnectionError, HttpResult, HttpTimeout, get_json, post_json


class ErrorKind(str, Enum):
    CONFIG = "config"
    AUTH = "auth"
    MODEL_NOT_FOUND = "model_not_found"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    BAD_REQUEST = "bad_request"
    SERVER = "server"
    BAD_RESPONSE = "bad_response"
    EMPTY = "empty"
    BLOCKED = "blocked"
    TOOL_IGNORED = "tool_ignored"


_MESSAGES = {
    ErrorKind.AUTH: "Autentikasi gagal. Periksa API key dan izin akunmu (ketik /connect untuk menggantinya).",
    ErrorKind.MODEL_NOT_FOUND: "Model tidak ditemukan atau tidak tersedia untuk akunmu. Cek nama model (ketik /model untuk mengganti).",
    ErrorKind.RATE_LIMIT: "Batas permintaan atau kuota tercapai. Tunggu sebentar atau cek kuota akunmu di penyedia.",
    ErrorKind.TIMEOUT: "Permintaan melewati batas waktu. Coba lagi sebentar lagi.",
    ErrorKind.NETWORK: "Tidak dapat terhubung ke penyedia. Periksa koneksi internetmu.",
    ErrorKind.BAD_REQUEST: "Permintaan ditolak oleh penyedia (kode {status}).",
    ErrorKind.SERVER: "Penyedia sedang bermasalah (kode {status}). Coba lagi nanti.",
    ErrorKind.BAD_RESPONSE: "Respons dari penyedia tidak dapat dipahami.",
    ErrorKind.EMPTY: "Penyedia mengembalikan respons kosong.",
    ErrorKind.BLOCKED: "Respons diblokir oleh kebijakan penyedia.",
    ErrorKind.TOOL_IGNORED: "Model meminta menjalankan tool atau perintah. LinuxAI hanya chatbot teks, jadi permintaan itu diabaikan.",
}


class ProviderError(Exception):
    """Error dengan pesan aman: tidak pernah memuat isi respons mentah atau API key."""

    def __init__(self, kind: ErrorKind, message: Optional[str] = None, status: Optional[int] = None):
        self.kind = kind
        self.status = status
        self.message = message or _MESSAGES[kind].format(status=status)
        super().__init__(self.message)


@dataclass(frozen=True)
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str


Transport = Callable[[str, dict, dict, float], HttpResult]
GetTransport = Callable[[str, dict, float], HttpResult]
MAX_MODELS = 500


class Provider(ABC):
    id: str = ""
    label: str = ""
    docs_url: str = ""
    needs_base_url: bool = False
    default_base_url: Optional[str] = None

    def __init__(self, transport: Optional[Transport] = None, timeout: float = 30.0,
                 get_transport: Optional[GetTransport] = None):
        self.transport: Transport = transport or post_json
        self.get_transport: GetTransport = get_transport or get_json
        self.timeout = timeout

    @abstractmethod
    def build_request(
        self, config: ProviderConfig, messages: List[ChatMessage], system_prompt: str
    ) -> Tuple[str, dict, dict]:
        """Kembalikan (url, headers, payload). Payload TIDAK boleh memuat tools."""

    @abstractmethod
    def extract_text(self, data: Optional[dict]) -> str:
        """Ambil teks dari respons. Abaikan tool/function call."""

    def models_request(self, config: ProviderConfig) -> Tuple[str, dict]:
        """(url, headers) untuk mengambil daftar model."""
        raise ProviderError(ErrorKind.CONFIG, "Provider ini tidak mendukung pengambilan daftar model.")

    def parse_models(self, data: Optional[dict]) -> List[str]:
        raise ProviderError(ErrorKind.BAD_RESPONSE)

    def list_models(self, config: ProviderConfig) -> List[str]:
        """Ambil daftar model dari provider (GET). Hanya id yang valid yang dikembalikan."""
        try:
            validate_api_key(config.api_key)
        except ValidationError as err:
            raise ProviderError(ErrorKind.CONFIG, str(err))
        url, headers = self.models_request(config)
        try:
            result = self.get_transport(url, headers, self.timeout)
        except HttpTimeout:
            raise ProviderError(ErrorKind.TIMEOUT)
        except HttpConnectionError:
            raise ProviderError(ErrorKind.NETWORK)
        self._check_status(result)
        found = {m for m in self.parse_models(result.data) if isinstance(m, str) and MODEL_RE.match(m) and ".." not in m}
        if not found:
            raise ProviderError(ErrorKind.EMPTY, "Provider tidak mengembalikan daftar model.")
        return sorted(found)[:MAX_MODELS]

    def chat(self, config: ProviderConfig, messages: List[ChatMessage], system_prompt: str) -> str:
        try:
            validate_model(config.model)
            validate_api_key(config.api_key)
        except ValidationError as err:
            raise ProviderError(ErrorKind.CONFIG, str(err))
        url, headers, payload = self.build_request(config, messages, system_prompt)
        try:
            result = self.transport(url, headers, payload, self.timeout)
        except HttpTimeout:
            raise ProviderError(ErrorKind.TIMEOUT)
        except HttpConnectionError:
            raise ProviderError(ErrorKind.NETWORK)
        self._check_status(result)
        text = self.extract_text(result.data)
        return redact(clean_model_text(text), config.api_key)

    # ---- util -------------------------------------------------------
    def _check_status(self, result: HttpResult) -> None:
        status = result.status
        if 200 <= status < 300:
            return
        hint = _error_hint(result.data)
        if status in (401, 403) or (status == 400 and "api key" in hint):
            raise ProviderError(ErrorKind.AUTH, status=status)
        if status == 404:
            raise ProviderError(ErrorKind.MODEL_NOT_FOUND, status=status)
        if status == 429:
            raise ProviderError(ErrorKind.RATE_LIMIT, status=status)
        if status in (408, 504):
            raise ProviderError(ErrorKind.TIMEOUT, status=status)
        if 300 <= status < 400:
            raise ProviderError(ErrorKind.BAD_RESPONSE, status=status)
        if status >= 500:
            raise ProviderError(ErrorKind.SERVER, status=status)
        raise ProviderError(ErrorKind.BAD_REQUEST, status=status)


def _error_hint(data: Optional[dict]) -> str:
    try:
        err = data.get("error") if isinstance(data, dict) else None
        if isinstance(err, dict):
            return str(err.get("message", "")).lower()
        if isinstance(err, str):
            return err.lower()
    except Exception:
        pass
    return ""
