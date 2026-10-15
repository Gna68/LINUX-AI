"""Validasi input dasar. Pesan error TIDAK PERNAH memuat nilai API key."""
from __future__ import annotations

import re
from urllib.parse import urlparse

MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/\-]{0,199}$")
KEY_RE = re.compile(r"^[\x21-\x7e]+$")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class ValidationError(ValueError):
    pass


def validate_model(value: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValidationError("Nama model tidak boleh kosong.")
    if ".." in v or not MODEL_RE.match(v):
        raise ValidationError(
            "Nama model hanya boleh berisi huruf, angka, titik, titik dua, garis miring, "
            "strip, dan underscore (maks. 200 karakter)."
        )
    return v


def validate_api_key(value: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValidationError("API key tidak boleh kosong.")
    if len(v) < 8 or len(v) > 512:
        raise ValidationError("Panjang API key tidak wajar (harus 8-512 karakter).")
    if not KEY_RE.match(v):
        raise ValidationError("API key tidak boleh memuat spasi atau karakter non-ASCII.")
    return v


def validate_base_url(value: str) -> str:
    v = (value or "").strip()
    try:
        parsed = urlparse(v)
        host = parsed.hostname or ""
    except ValueError:
        raise ValidationError("Base URL tidak valid.")
    if parsed.scheme not in ("http", "https") or not host:
        raise ValidationError("Base URL harus diawali https:// (contoh: https://api.example.com/v1).")
    if parsed.scheme == "http" and host not in LOCAL_HOSTS:
        raise ValidationError("http:// hanya diizinkan untuk localhost. Gunakan https://.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValidationError("Base URL tidak boleh memuat kredensial, query, atau fragment.")
    return v.rstrip("/")
