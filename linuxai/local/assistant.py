"""Local Mode: pencocokan pertanyaan berbasis aturan. BUKAN LLM, tidak butuh jaringan."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence

from linuxai.local.knowledge import ENTRIES, Entry

_TOKEN = re.compile(r"[a-z0-9_./+~\-]+")
_TRIGGERS = {
    "perintah", "command", "cmd", "fungsi", "arti", "maksud", "jelaskan", "apakah",
    "gunakan", "pakai", "menggunakan", "cara", "bagaimana", "gimana", "apa",
}
MAX_QUESTION_LEN = 2000
UNKNOWN_EXAMPLES = (
    "apa beda Windows dan Linux?",
    "cara install aplikasi di Linux",
    "apa fungsi perintah grep?",
    "permission denied",
    "wifi tidak muncul",
)


def tokenize(text: str) -> List[str]:
    tokens = []
    for raw in _TOKEN.findall(text.lower()[:MAX_QUESTION_LEN]):
        tok = raw.rstrip(".")
        if tok:
            tokens.append(tok)
    return tokens


def _contains(tokens: Sequence[str], phrase: Sequence[str]) -> bool:
    n = len(phrase)
    if n == 0 or n > len(tokens):
        return False
    return any(list(tokens[i:i + n]) == list(phrase) for i in range(len(tokens) - n + 1))


@dataclass
class LocalAnswer:
    text: str
    matched: bool
    entry_id: Optional[str] = None


class LocalAssistant:
    def __init__(self, entries: Optional[Sequence[Entry]] = None):
        self.entries = list(entries) if entries is not None else list(ENTRIES)
        self._compiled = [
            (e, [tokenize(k) for k in e.keys if tokenize(k)]) for e in self.entries
        ]

    def _score(self, entry: Entry, key_tokens: List[List[str]], tokens: List[str]) -> float:
        if entry.cmd and len(tokens) > 6 and not (set(tokens) & _TRIGGERS):
            return 0.0
        scores = [len(k) * 2 for k in key_tokens if _contains(tokens, k)]
        if not scores:
            return 0.0
        return max(scores) + 0.5 * (len(scores) - 1)

    def find(self, question: str) -> Optional[Entry]:
        tokens = tokenize(question)
        if not tokens:
            return None
        best, best_score = None, 0.0
        for entry, key_tokens in self._compiled:
            score = self._score(entry, key_tokens, tokens)
            if score > best_score:
                best, best_score = entry, score
        return best

    def answer(self, question: str) -> LocalAnswer:
        entry = self.find(question)
        if entry is None:
            return LocalAnswer(self.unknown_text(), matched=False)
        return LocalAnswer(entry.answer, matched=True, entry_id=entry.id)

    @staticmethod
    def unknown_text() -> str:
        examples = "\n".join(f"- {e}" for e in UNKNOWN_EXAMPLES)
        return (
            "Maaf, aku belum punya jawaban untuk pertanyaan itu di Local Mode.\n\n"
            "Local Mode hanya memakai basis pengetahuan bawaan dan aturan sederhana, "
            "bukan AI generatif, jadi tidak bisa menalar pertanyaan di luar topiknya.\n\n"
            "Kamu bisa:\n"
            "- menulis ulang dengan kata kunci yang lebih jelas, misalnya:\n"
            f"{examples}\n"
            "- mengaktifkan Cloud Mode dengan API key milikmu sendiri: ketik /connect "
            "(jawaban AI generatif, butuh internet)."
        )
