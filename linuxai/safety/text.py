"""Sanitasi teks dari model: respons hanya boleh berupa teks polos."""
from __future__ import annotations

import re

_CSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
_OTHER_ESC = re.compile(r"\x1b[@-Z\\-_]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

MAX_LEN = 20000


def clean_model_text(text: str, max_len: int = MAX_LEN) -> str:
    """Buang escape sequence terminal dan karakter kontrol, lalu batasi panjang."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _OSC.sub("", text)
    text = _CSI.sub("", text)
    text = _OTHER_ESC.sub("", text)
    text = _CONTROL.sub("", text)
    text = text.replace("\x1b", "")
    text = text.strip()
    if len(text) > max_len:
        text = text[:max_len].rstrip() + "\n[...dipotong]"
    return text
