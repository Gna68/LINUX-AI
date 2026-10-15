"""Daftar slash command untuk menu saran saat mengetik '/'. Murni data, tanpa UI."""
from __future__ import annotations

from typing import List, Tuple

COMMANDS: List[Tuple[str, str]] = [
    ("/clear", "Bersihkan percakapan"),
    ("/connect", "Hubungkan provider AI"),
    ("/copy", "Salin jawaban terakhir"),
    ("/exit", "Keluar dari LinuxAI"),
    ("/help", "Bantuan"),
    ("/mode", "Pindah Local / Cloud"),
    ("/model", "Lihat atau ganti model"),
    ("/provider", "Lihat atau ganti provider"),
    ("/settings", "Pengaturan dan hapus API key"),
]


def filter_commands(value: str) -> List[Tuple[str, str]]:
    """Saran untuk teks yang diawali '/'. Kosong jika bukan slash atau sudah ada argumen."""
    if not value.startswith("/") or " " in value:
        return []
    prefix = value.lower()
    starts = [c for c in COMMANDS if c[0].startswith(prefix)]
    return starts or [c for c in COMMANDS if prefix[1:] in c[0]]
