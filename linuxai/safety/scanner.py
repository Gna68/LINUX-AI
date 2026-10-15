# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Pemindai source code berbasis AST untuk menegakkan batasan "hanya chatbot".

Mencari mekanisme eksekusi perintah, eksekusi kode dinamis, kontrol perangkat,
tool/function calling, dan akses filesystem. Karena memakai AST, teks di
docstring/komentar/string tidak dianggap pelanggaran.

Akses filesystem hanya diizinkan di config/ (penyimpanan konfigurasi) dan
safety/ (pemindai ini; alat pengembangan, tidak dipanggil saat aplikasi jalan).

Pakai:  python -m linuxai.safety.scanner [folder]
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

FORBIDDEN_MODULES: Dict[str, str] = {
    "subprocess": "exec", "pty": "exec", "pexpect": "exec", "ptyprocess": "exec",
    "sh": "exec", "plumbum": "exec", "commands": "exec",
    "runpy": "dynamic", "code": "dynamic", "codeop": "dynamic",
    "pyautogui": "control", "pynput": "control", "keyboard": "control",
    "mouse": "control", "webbrowser": "control", "selenium": "control",
    "mcp": "tools", "langchain": "tools", "autogen": "tools", "crewai": "tools",
}
FORBIDDEN_BUILTINS: Dict[str, str] = {
    "eval": "dynamic", "exec": "dynamic", "compile": "dynamic", "__import__": "dynamic",
}
OS_EXACT = {
    "os.system", "os.popen", "os.fork", "os.forkpty", "os.startfile", "os.kill", "os.killpg",
}
OS_PREFIXES = ("os.exec", "os.spawn", "os.posix_spawn")
FS_OS_CALLS = {
    "os.remove", "os.unlink", "os.rmdir", "os.removedirs", "os.rename", "os.renames",
    "os.replace", "os.mkdir", "os.makedirs", "os.chmod", "os.chown", "os.symlink",
    "os.link", "os.truncate", "os.listdir", "os.scandir", "os.walk", "os.open",
}
FS_MODULES = {"shutil", "glob", "tempfile"}
FS_METHODS = {
    "write_text", "write_bytes", "read_text", "read_bytes", "unlink", "rmdir", "touch",
    "mkdir", "chmod", "symlink_to", "hardlink_to", "iterdir", "glob", "rglob",
}
TOOL_KEYS = {
    "tools", "tool_choice", "functions", "function_call", "functionDeclarations",
    "function_declarations", "toolConfig", "tool_config",
}
FS_ALLOWED_DIRS = ("config", "safety")


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    category: str
    detail: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.category}] {self.detail}"


class _Visitor(ast.NodeVisitor):
    def __init__(self, rel: str, allow_fs: bool):
        self.rel = rel
        self.allow_fs = allow_fs
        self.aliases: Dict[str, str] = {}
        self.found: List[Violation] = []

    def _add(self, node: ast.AST, category: str, detail: str) -> None:
        if category == "fs" and self.allow_fs:
            return
        self.found.append(Violation(self.rel, getattr(node, "lineno", 0), category, detail))

    def _resolve(self, node: ast.AST) -> Optional[str]:
        parts: List[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(self.aliases.get(node.id, node.id))
            return ".".join(reversed(parts))
        return None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top = alias.name.split(".")[0]
            self.aliases[alias.asname or top] = alias.name if alias.asname else top
            self._check_module(node, alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level == 0 and module:
            self._check_module(node, module)
            for alias in node.names:
                self.aliases[alias.asname or alias.name] = f"{module}.{alias.name}"
                self._check_dotted(node, f"{module}.{alias.name}")
        self.generic_visit(node)

    def _check_module(self, node: ast.AST, name: str) -> None:
        top = name.split(".")[0]
        if top in FORBIDDEN_MODULES:
            self._add(node, FORBIDDEN_MODULES[top], f"import '{name}'")
        if top in FS_MODULES:
            self._add(node, "fs", f"import '{name}'")

    def _check_dotted(self, node: ast.AST, dotted: str) -> None:
        if dotted in OS_EXACT or dotted.startswith(OS_PREFIXES):
            self._add(node, "exec", f"'{dotted}'")
        elif dotted in FS_OS_CALLS:
            self._add(node, "fs", f"'{dotted}'")

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            if func.id in FORBIDDEN_BUILTINS and func.id not in self.aliases:
                self._add(node, FORBIDDEN_BUILTINS[func.id], f"panggilan '{func.id}()'")
            if func.id == "open" and "open" not in self.aliases:
                self._add(node, "fs", "panggilan 'open()'")
        dotted = self._resolve(func)
        if dotted:
            self._check_dotted(node, dotted)
            if dotted.split(".")[0] in FS_MODULES:
                self._add(node, "fs", f"'{dotted}'")
        if isinstance(func, ast.Attribute) and func.attr in FS_METHODS:
            self._add(node, "fs", f"metode '.{func.attr}()'")
        for kw in node.keywords:
            if kw.arg in TOOL_KEYS:
                self._add(node, "tools", f"argumen '{kw.arg}='")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        for key in node.keys:
            if isinstance(key, ast.Constant) and key.value in TOOL_KEYS:
                self._add(node, "tools", f"kunci dict '{key.value}'")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        sl = node.slice
        if isinstance(node.ctx, ast.Store) and isinstance(sl, ast.Constant) and sl.value in TOOL_KEYS:
            self._add(node, "tools", f"penugasan kunci '{sl.value}'")
        self.generic_visit(node)


def scan_source(source: str, rel: str = "<string>", allow_fs: bool = False) -> List[Violation]:
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        return [Violation(rel, err.lineno or 0, "parse", "file tidak bisa diparse")]
    visitor = _Visitor(rel, allow_fs)
    visitor.visit(tree)
    return visitor.found


def scan_tree(root: Path, skip: Iterable[str] = ()) -> List[Violation]:
    root = Path(root)
    skip_set: Set[str] = set(skip)
    violations: List[Violation] = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if any(rel.startswith(s) for s in skip_set):
            continue
        parts = rel.split("/")
        allow_fs = len(parts) > 1 and parts[0] in FS_ALLOWED_DIRS
        violations.extend(scan_source(path.read_text(encoding="utf-8"), rel, allow_fs))
    return violations


def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
    found = scan_tree(root)
    for v in found:
        print(v)
    print(f"{len(found)} pelanggaran ditemukan di {root}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
