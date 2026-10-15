# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Entry point CLI: `linuxai` membuka TUI; `linuxai "pertanyaan"` menjawab sekali."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from linuxai import __version__
from linuxai.core.controller import one_shot
from linuxai.safety.text import clean_model_text

EPILOG = """Di dalam TUI: /connect /provider /model /mode /help /clear /settings /exit
Local Mode (default) tidak butuh internet atau API key. LinuxAI tidak menjalankan perintah apa pun."""


def run_tui(start_mode: str = "local") -> int:
    try:
        from linuxai.app import run
    except ImportError:
        print("Antarmuka layar penuh membutuhkan paket 'textual'.\n"
              "Pasang dengan: pip install textual  (atau pasang ulang LinuxAI dengan pipx).",
              file=sys.stderr)
        return 1
    return run(start_mode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linuxai",
        description="LinuxAI - Your Linux Companion. Chatbot terminal untuk pengguna Windows yang baru pindah ke Linux.",
        epilog=EPILOG,
    )
    parser.add_argument("question", nargs="*", help="pertanyaan sekali jalan (tanpa ini, TUI dibuka)")
    parser.add_argument("--local", action="store_true", help="paksa Local Mode (default)")
    parser.add_argument("--cloud", action="store_true", help="pakai provider cloud yang sudah dikonfigurasi")
    parser.add_argument("--version", action="version", version=f"LinuxAI {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.local and args.cloud:
        parser.error("--local dan --cloud tidak bisa dipakai bersamaan")
    mode = "cloud" if args.cloud else "local"
    question = " ".join(args.question).strip()
    if not question:
        return run_tui(mode)
    text, ok = one_shot(question, mode)
    try:
        print(clean_model_text(text), file=sys.stdout if ok else sys.stderr)
    except BrokenPipeError:  # mis. `linuxai "..." | head`
        pass
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
