# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Local Mode: pencocokan pertanyaan berbasis aturan. BUKAN LLM, tidak butuh jaringan.

Cara kerja: (1) normalisasi (huruf kecil, sinonim, buang kata penghubung), (2) koreksi typo ringan
terhadap kosakata basis pengetahuan, (3) cocokkan frasa persis atau kumpulan kata kunci tanpa
memperhatikan urutan, (4) jika tidak ada yang cocok, tawarkan topik terdekat.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set

from linuxai.local.knowledge import ENTRIES, Entry

_TOKEN = re.compile(r"[a-z0-9_./+~\-]+")
MAX_QUESTION_LEN = 2000

_TRIGGERS = {
    "perintah", "command", "cmd", "fungsi", "arti", "maksud", "jelaskan", "apakah",
    "gunakan", "pakai", "menggunakan", "cara", "bagaimana", "gimana", "apa",
}
STOPWORDS = frozenset("""
apa itu yang gimana bagaimana gmn cara caranya dong sih ya tolong saya aku gue gw di ke dari untuk dengan
adalah kah nih deh aja saja bisa bisakah apakah kenapa mengapa kok kalau kalo jika agar supaya dan atau
the a an is are to how what why do does can i my me in on of for with it this that please pls tlg
mau ingin pengen pengertian definisi artinya maksud penjelasan jelaskan sebenarnya sebetulnya tuh lah
yg dgn utk jg juga sama lagi udah sudah masih mulai sedang lagi kamu anda kalian bro kak min admin tau tahu
""".split())
SYNONYMS: Dict[str, str] = {
    "copy": "salin", "menyalin": "salin", "kopi": "salin", "copas": "salin", "duplikat": "salin",
    "paste": "tempel", "menempel": "tempel", "menempelkan": "tempel",
    "menghapus": "hapus", "delete": "hapus", "remove": "hapus", "hapuskan": "hapus", "membuang": "hapus",
    "menginstal": "install", "instal": "install", "menginstall": "install", "memasang": "install",
    "pasang": "install", "installasi": "install", "instalasi": "install",
    "mengunduh": "download", "unduh": "download", "mendownload": "download",
    "berkas": "file", "directory": "folder", "direktori": "folder",
    "wi-fi": "wifi", "wlan": "wifi",
    "memindahkan": "pindah", "move": "pindah", "memindah": "pindah", "pindahkan": "pindah",
    "mengganti": "ganti", "mengubah": "ganti", "change": "ganti", "ubah": "ganti",
    "melihat": "lihat", "cek": "lihat", "mengecek": "lihat", "memeriksa": "lihat", "check": "lihat",
    "show": "lihat", "menampilkan": "lihat", "tampilkan": "lihat", "periksa": "lihat",
    "mencari": "cari", "search": "cari",
    "menjalankan": "jalankan", "run": "jalankan", "membuka": "buka", "open": "buka",
    "lambat": "lemot", "pelan": "lemot", "lag": "lemot", "lola": "lemot",
    "tidak": "gak", "nggak": "gak", "ga": "gak", "enggak": "gak", "tak": "gak", "ngga": "gak", "gk": "gak",
    "terdeteksi": "muncul", "kelihatan": "muncul", "terlihat": "muncul", "tampil": "muncul",
    "laptop": "komputer", "pc": "komputer", "notebook": "komputer",
    "mengupdate": "update", "memperbarui": "update", "perbarui": "update", "pembaruan": "update",
    "menghubungkan": "hubung", "konek": "hubung", "connect": "hubung", "terhubung": "hubung", "menyambung": "hubung",
    "error": "error", "eror": "error", "galat": "error", "kesalahan": "error",
    "ngapain": "fungsi", "kegunaan": "fungsi",
    "nginstall": "install", "nginstal": "install", "ngeinstall": "install", "ngeinstal": "install", "ninstall": "install",
    "nambahin": "tambah", "menambahkan": "tambah", "tambahkan": "tambah", "menambah": "tambah", "nambah": "tambah",
    "ngapus": "hapus", "ngehapus": "hapus", "nghapus": "hapus", "hapusin": "hapus",
    "ngecek": "lihat", "ngelihat": "lihat", "ngganti": "ganti", "gantiin": "ganti", "ngubah": "ganti",
    "bikin": "buat", "nyalin": "salin", "ngopy": "salin", "ngebuka": "buka", "nyari": "cari", "ngejalanin": "jalankan",
    "gabisa": "gak", "gabsa": "gak", "gakbisa": "gak",
}


MISSPELLINGS: Dict[str, str] = {
    "linuks": "linux", "lunix": "linux", "linus": "linux", "linuxx": "linux", "ubunto": "ubuntu", "ubantu": "ubuntu",
    "kernal": "kernel", "terminall": "terminal", "wifi": "wifi", "wify": "wifi", "grup": "grup", "bluetoth": "bluetooth",
    "pasword": "password", "pasword": "password", "passwod": "password", "hyperland": "hyprland", "hyperlan": "hyprland",
}


def tokenize(text: str) -> List[str]:
    tokens = []
    for raw in _TOKEN.findall(text.lower()[:MAX_QUESTION_LEN]):
        tok = raw.rstrip(".")
        if tok:
            tokens.append(tok)
    return tokens


def canon_tokens(tokens: Sequence[str]) -> List[str]:
    """Sinonim -> bentuk baku, kata penghubung dibuang, duplikat dibuang (urutan dipertahankan)."""
    out: List[str] = []
    for tok in tokens:
        tok = SYNONYMS.get(tok, tok)
        if tok in STOPWORDS or tok in out:
            continue
        out.append(tok)
    return out


def _within_one_edit(a: str, b: str) -> bool:
    """Jarak edit <= 1 (sisip/hapus/ganti/tukar dua huruf bersebelahan)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = [i for i in range(la) if a[i] != b[i]]
        if len(diff) == 1:
            return True
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    short, long_ = (a, b) if la < lb else (b, a)
    i = j = 0
    skipped = False
    while i < len(short) and j < len(long_):
        if short[i] == long_[j]:
            i += 1
            j += 1
        elif skipped:
            return False
        else:
            skipped = True
            j += 1
    return True


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
    suggestions: List[str] = field(default_factory=list)


@dataclass
class _Compiled:
    entry: Entry
    keys: List[tuple]  # (raw_tokens, canon_tokens)
    vocab: Set[str]


UNKNOWN_EXAMPLES = (
    "apa beda Windows dan Linux?",
    "cara install aplikasi di Linux",
    "apa fungsi perintah grep?",
    "permission denied",
    "wifi tidak muncul",
)


class LocalAssistant:
    def __init__(self, entries: Optional[Sequence[Entry]] = None):
        self.entries = list(entries) if entries is not None else list(ENTRIES)
        self._compiled: List[_Compiled] = []
        spelling: Set[str] = set()
        for e in self.entries:
            keys, vocab = [], set()
            for k in e.keys:
                raw = tokenize(k)
                if not raw:
                    continue
                canon = canon_tokens(raw)
                keys.append((raw, canon))
                vocab.update(canon)
                spelling.update(t for t in raw if len(t) >= 5 and t.isalpha())
            vocab.update(t for t in canon_tokens(tokenize(e.title)))
            self._compiled.append(_Compiled(e, keys, vocab))
        self._spelling = sorted(spelling - STOPWORDS - set(SYNONYMS))

    # ---------------------------------------------------------------- normalisasi
    def _fix_typos(self, tokens: List[str]) -> List[str]:
        known = set(self._spelling)
        fixed = []
        for tok in tokens:
            tok = MISSPELLINGS.get(tok, tok)
            if len(tok) >= 5 and tok.isalpha() and tok not in known and tok not in STOPWORDS and tok not in SYNONYMS:
                close = difflib.get_close_matches(tok, self._spelling, n=1, cutoff=0.85)
                if not close:  # typo satu huruf pada kata pendek: huruf awal harus sama
                    close = [w for w in self._spelling if w[0] == tok[0] and _within_one_edit(tok, w)][:1]
                if close:
                    tok = close[0]
            fixed.append(tok)
        return fixed

    def _prepare(self, question: str):
        raw = self._fix_typos(tokenize(question))
        return raw, canon_tokens(raw)

    # ---------------------------------------------------------------- skor
    def _score(self, item: _Compiled, raw_q: List[str], canon_q: List[str]) -> float:
        e = item.entry
        if e.cmd and len(raw_q) > 6 and not (set(raw_q) & _TRIGGERS):
            return 0.0
        gate_single = e.short and len(canon_q) > 2
        canon_set = set(canon_q)
        scores = []
        for raw_k, canon_k in item.keys:
            if len(raw_k) == 1 and gate_single:
                continue
            if _contains(raw_q, raw_k):
                scores.append(len(raw_k) * 2 + 1)
            elif len(canon_k) >= 2 and set(canon_k) <= canon_set:
                scores.append(len(canon_k) * 2)
        if not scores:
            return 0.0
        return max(scores) + 0.5 * (len(scores) - 1)

    def find(self, question: str) -> Optional[Entry]:
        raw_q, canon_q = self._prepare(question[:MAX_QUESTION_LEN])
        if not raw_q:
            return None
        best, best_score = None, 0.0
        for item in self._compiled:
            score = self._score(item, raw_q, canon_q)
            if score > best_score:
                best, best_score = item.entry, score
        return best

    def suggest(self, question: str, limit: int = 3) -> List[Entry]:
        """Topik terdekat (tumpang-tindih kata) untuk pertanyaan yang tidak cocok persis."""
        _, canon_q = self._prepare(question[:MAX_QUESTION_LEN])
        words = {t for t in canon_q if len(t) >= 4}
        if not words:
            return []
        ranked = []
        for item in self._compiled:
            overlap = len(words & item.vocab)
            if overlap:
                ranked.append((overlap, item.entry))
        ranked.sort(key=lambda x: -x[0])
        return [e for _, e in ranked[:limit]]

    def answer(self, question: str) -> LocalAnswer:
        entry = self.find(question)
        if entry is not None:
            return LocalAnswer(entry.answer, matched=True, entry_id=entry.id)
        sugg = self.suggest(question)
        return LocalAnswer(self.unknown_text(sugg), matched=False, suggestions=[s.title for s in sugg])

    @staticmethod
    def unknown_text(suggestions: Optional[Sequence[Entry]] = None) -> str:
        parts = ["Maaf, aku belum punya jawaban untuk pertanyaan itu di Local Mode.\n"]
        if suggestions:
            parts.append("Mungkin maksudmu salah satu topik ini? Tulis ulang pertanyaannya dengan judul topik:")
            parts.extend(f"- {s.title}" for s in suggestions)
            parts.append("")
        parts.append(
            "Local Mode hanya memakai basis pengetahuan bawaan dan aturan sederhana, "
            "bukan AI generatif, jadi tidak bisa menalar pertanyaan di luar topiknya.\n")
        parts.append("Kamu bisa:\n- menulis ulang dengan kata kunci yang lebih jelas, misalnya:")
        parts.extend(f"  - {e}" for e in UNKNOWN_EXAMPLES)
        parts.append("- mengaktifkan Cloud Mode dengan API key milikmu sendiri: ketik /connect "
                     "(jawaban AI generatif, butuh internet).")
        return "\n".join(parts)

