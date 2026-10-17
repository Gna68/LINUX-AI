# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Struktur satu entri basis pengetahuan Local Mode."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Entry:
    id: str
    title: str
    keys: Tuple[str, ...]
    answer: str
    cmd: bool = False    # kunci satu kata yang ambigu: hanya cocok untuk pertanyaan pendek atau yang jelas
    short: bool = False  # entri definisi: kunci satu kata hanya cocok untuk pertanyaan sangat pendek


def T(id: str, title: str, keys: str, answer: str, cmd: bool = False, short: bool = False) -> Entry:
    """Pembuat entri ringkas. `keys` dipisah tanda '|'."""
    return Entry(id, title, tuple(k.strip() for k in keys.split("|") if k.strip()), answer.strip("\n"), cmd, short)
