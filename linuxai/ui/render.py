"""Helper tampilan murni-Python (tanpa Textual/Rich) agar mudah diuji.

Mengembalikan segmen (teks, gaya) yang diubah menjadi rich.Text oleh app.py.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from linuxai import DESCRIPTION, TAGLINE

Segment = Tuple[str, str]
Line = List[Segment]

LABELS = {
    "user": ("Kamu", "bold blue"),
    "assistant": ("LinuxAI", "bold green"),
    "system": ("LinuxAI", "bold"),
    "error": ("Error", "bold red"),
}
_FONT = {
    "L": ["X...", "X...", "X...", "X...", "XXXX"],
    "I": ["XXX", ".X.", ".X.", ".X.", "XXX"],
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X"],
    "U": ["X...X", "X...X", "X...X", "X...X", ".XXX."],
    "X": ["X...X", ".X.X.", "..X..", ".X.X.", "X...X"],
    "A": [".XXX.", "X...X", "XXXXX", "X...X", "X...X"],
}


def _word_rows(word: str, cell: str) -> List[str]:
    blank = " " * len(cell)
    rows = []
    for r in range(5):
        letters = ["".join(cell if px == "X" else blank for px in _FONT[ch][r]) for ch in word]
        rows.append(blank.join(letters))
    return rows


def logo_lines(width: int) -> List[Line]:
    """Logo blok besar ala OpenCode: LINUX redup, AI tebal. Menyesuaikan lebar terminal."""
    if width >= 76:
        cell = "\u2588\u2588"
    elif width >= 44:
        cell = "\u2588"
    else:
        return [[("LinuxAI", "bold green")]]
    gap = " " * len(cell)
    left, right = _word_rows("LINUX", cell), _word_rows("AI", cell)
    return [[(l, "dim"), (gap, ""), (r, "bold")] for l, r in zip(left, right)]


def suggestion_lines(items, index: int) -> List[Line]:
    """Menu saran slash command; baris terpilih disorot."""
    width = max((len(name) for name, _ in items), default=0) + 3
    lines: List[Line] = []
    for i, (name, desc) in enumerate(items):
        if i == index:
            lines.append([(f" {name:<{width}}{desc} ", "bold reverse")])
        else:
            lines.append([(f" {name:<{width}}", "bold"), (desc, "dim")])
    return lines


SPINNER = "\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f"


def hero_lines(mode_label: str, width: int) -> List[Line]:
    """Branding di tengah layar saat belum ada percakapan."""
    hint = "Enter kirim \u00b7 /help bantuan \u00b7 /connect Cloud AI \u00b7 Ctrl+C keluar"
    if width < len(hint) + 4:
        hint = "/help bantuan \u00b7 Ctrl+C keluar"
    return [
        *logo_lines(width),
        [("", "")],
        [(TAGLINE, "bold")],
        [(DESCRIPTION, "")],
        [("", "")],
        [(f"[ {mode_label} ]", "bold reverse")],
        [("", "")],
        [(hint, "dim")],
    ]


def header_text(mode_label: str) -> str:
    return f"LinuxAI \u00b7 {TAGLINE}  [{mode_label}]"


# ---------------------------------------------------------------- pewarnaan
# Hanya warna ANSI bernama (cyan, green, ...) agar mengikuti tema terminal gelap maupun terang.
_INLINE = re.compile(r"(`[^`\n]+`|\*\*[^*\n]+\*\*)")
_BULLET = re.compile(r"^(\s*)([-*\u2022])\s+(.*)$")
_NUMBERED = re.compile(r"^(\s*)(\d+[.)])\s+(.*)$")
_HEADING = re.compile(r"^\s{0,3}#{1,4}\s+(.*)$")
_SLASH_CMD = re.compile(r"^(/[a-z]+)(\s+.*)?$")
_SHELL_TOKEN = re.compile(r"\s+|\"[^\"]*\"?|'[^']*'?|[^\s]+")
_SHELL_LANGS = {"", "bash", "sh", "shell", "console", "zsh", "terminal"}
_CMD_PREFIX = {"sudo", "time", "env", "xargs", "nohup", "exec"}
_OPERATORS = {"|", "||", "&&", ";", "&"}  # setelah ini muncul perintah baru
_REDIRECTS = {">", ">>", "<", "2>", "2>&1"}


def inline_segments(text: str, base: str = "") -> Line:
    """`kode` jadi cyan tebal, **tebal** jadi tebal; tanda markdown-nya dibuang."""
    out: Line = []
    for part in _INLINE.split(text):
        if not part:
            continue
        if len(part) > 2 and part.startswith("`") and part.endswith("`"):
            out.append((part[1:-1], "bold cyan"))
        elif len(part) > 4 and part.startswith("**") and part.endswith("**"):
            out.append((part[2:-2], (base + " bold").strip()))
        else:
            out.append((part, base))
    return out or [("", base)]


def shell_segments(line: str) -> Line:
    """Pewarnaan sederhana untuk baris perintah shell (tanpa mengubah teksnya)."""
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return [(line, "dim")]
    out: Line = []
    expect_cmd = True
    for tok in _SHELL_TOKEN.findall(line):
        if tok.isspace():
            out.append((tok, ""))
        elif tok == "#" or (tok.startswith("#") and not expect_cmd):
            consumed = "".join(t for t, _ in out)
            out.append((line[len(consumed):], "dim"))
            break
        elif tok == "$" and not out[:-1] and expect_cmd:
            out.append((tok, "dim"))
        elif tok in _OPERATORS:
            out.append((tok, "bold"))
            expect_cmd = True
        elif tok in _REDIRECTS:
            out.append((tok, "bold"))
            expect_cmd = False
        elif tok[0] in "\"'":
            out.append((tok, "magenta"))
            expect_cmd = False
        elif tok.startswith("-") and not expect_cmd:
            out.append((tok, "yellow"))
        elif tok == "sudo":
            out.append((tok, "bold red"))
        elif expect_cmd:
            out.append((tok, "bold green"))
            if tok not in _CMD_PREFIX:
                expect_cmd = False
        else:
            out.append((tok, ""))
    return out or [(line, "")]


def _text_line(raw: str, kind: str) -> Line:
    base = "italic" if kind == "system" else ""
    heading = _HEADING.match(raw)
    if heading:
        return [(heading.group(1), "bold yellow")]
    bullet = _BULLET.match(raw)
    if bullet:
        return [(bullet.group(1), ""), ("\u2022 ", "bold magenta")] + inline_segments(bullet.group(3), base)
    numbered = _NUMBERED.match(raw)
    if numbered:
        return [(numbered.group(1), ""), (numbered.group(2) + " ", "bold yellow")] + inline_segments(numbered.group(3), base)
    if kind == "system":
        cmd = _SLASH_CMD.match(raw.strip())
        if cmd and raw == raw.strip():
            return [(cmd.group(1), "bold cyan"), (cmd.group(2) or "", "")]
    return inline_segments(raw, base)


def message_lines(kind: str, text: str) -> List[Line]:
    """Ubah satu pesan menjadi baris-baris bergaya.

    Pesan pengguna dan error tampil apa adanya. Pesan LinuxAI/sistem: markdown ringan
    (**tebal**, `kode`, judul, daftar) dan blok ``` diwarnai seperti sintaks shell.
    """
    label, style = LABELS.get(kind, LABELS["system"])
    lines: List[Line] = [[(label, style)]]
    if kind in ("user", "error"):
        lines.extend([[(raw, "")] for raw in text.split("\n")])
        return lines
    in_code, lang = False, ""
    for raw in text.split("\n"):
        fence = raw.strip()
        if fence.startswith("```"):
            in_code = not in_code
            lang = fence[3:].strip().lower() if in_code else ""
            continue
        if in_code:
            body = shell_segments(raw) if lang in _SHELL_LANGS else [(raw, "bold")]
            lines.append([("  \u2502 ", "dim")] + body)
        else:
            lines.append(_text_line(raw, kind))
    return lines


def status_text(status_line: str, busy_note: str = "", frame: int = 0) -> str:
    if busy_note:
        return f"{SPINNER[frame % len(SPINNER)]} {busy_note}"
    return status_line
