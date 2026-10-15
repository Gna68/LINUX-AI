from __future__ import annotations


def mask_key(key: str) -> str:
    """Tampilkan API key tersamarkan. Kunci pendek tidak menampilkan karakter apa pun."""
    if not key:
        return "(kosong)"
    if len(key) < 16:
        return "\u2022" * 8
    return "\u2022\u2022\u2022\u2022" + key[-4:]


def redact(text: str, secret: str) -> str:
    if secret and len(secret) >= 4:
        return text.replace(secret, "[API-KEY]")
    return text
