import unittest
from pathlib import Path

from linuxai.cloud.base import ChatMessage, ErrorKind, ProviderError
from linuxai.config.models import ProviderConfig
from linuxai.providers import get_provider, provider_ids
from linuxai.safety.scanner import scan_source, scan_tree
from linuxai.safety.text import clean_model_text
from linuxai.utils.http import HttpResult
from tests.helpers import KEY, MockTransport, TmpConfigCase, connect, run

PKG = Path(__file__).resolve().parents[1] / "linuxai"
TOOL_KEYS = {"tools", "tool_choice", "functions", "function_call", "functionDeclarations",
             "function_declarations", "toolConfig", "tool_config"}


def walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_keys(v)


class ScannerOnPackageTests(unittest.TestCase):
    def test_package_has_no_execution_filesystem_or_tool_paths(self):
        violations = scan_tree(PKG)
        self.assertEqual([str(v) for v in violations], [])


class ScannerDetectionTests(unittest.TestCase):
    """Pastikan pemindai benar-benar menangkap pelanggaran (bukan lolos diam-diam)."""

    CASES = {
        "import subprocess": "exec",
        "import subprocess as sp\nsp.run(['ls'])": "exec",
        "from subprocess import run": "exec",
        "import os\nos.system('ls')": "exec",
        "import os as o\no.popen('ls')": "exec",
        "from os import system\nsystem('ls')": "exec",
        "import os\nos.execvp('ls', [])": "exec",
        "import pty": "exec",
        "eval('1+1')": "dynamic",
        "exec('x=1')": "dynamic",
        "__import__('os')": "dynamic",
        "import pyautogui": "control",
        "import webbrowser": "control",
        "payload = {'tools': []}": "tools",
        "payload['tool_choice'] = 'auto'": "tools",
        "client.create(tools=[1])": "tools",
        "open('/etc/passwd')": "fs",
        "import shutil": "fs",
        "import os\nos.remove('x')": "fs",
        "from pathlib import Path\nPath('x').write_text('y')": "fs",
    }

    def test_detects_each_violation(self):
        for source, category in self.CASES.items():
            with self.subTest(source=source):
                found = scan_source(source)
                self.assertTrue(found, f"tidak terdeteksi: {source!r}")
                self.assertIn(category, {v.category for v in found})

    def test_ignores_docs_comments_and_strings(self):
        source = '"""subprocess os.system eval tools"""\n# import subprocess\nx = "os.system(\'rm -rf /\')"\nprint("tool_choice")\n'
        self.assertEqual(scan_source(source), [])

    def test_reading_tool_call_fields_from_responses_is_allowed(self):
        self.assertEqual(scan_source("msg.get('tool_calls')\n'functionCall' in part\n"), [])

    def test_fs_only_allowed_in_config_and_safety(self):
        self.assertEqual(scan_source("open('x', 'w')", "config/store.py", allow_fs=True), [])
        self.assertTrue(scan_source("open('x', 'w')", "cloud/x.py", allow_fs=False))
        # exec tetap dilarang walau di folder yang boleh fs
        self.assertTrue(scan_source("import subprocess", "config/x.py", allow_fs=True))


class NoToolPathTests(TmpConfigCase):
    def test_no_provider_ever_sends_tools(self):
        for pid in provider_ids():
            t = MockTransport(HttpResult(200, {"choices": [{"message": {"content": "x"}}],
                                                "candidates": [{"content": {"parts": [{"text": "x"}]}}]}))
            get_provider(pid, t).chat(ProviderConfig(pid, "m", KEY), [ChatMessage("user", "halo")], "SYS")
            self.assertFalse(TOOL_KEYS & set(walk_keys(t.calls[0]["payload"])), pid)

    def test_model_tool_requests_are_ignored_not_executed(self):
        executed = []
        gemini = HttpResult(200, {"candidates": [{"content": {"parts": [
            {"functionCall": {"name": "run_shell", "args": {"cmd": "rm -rf ~"}}}]}}]})
        openai = HttpResult(200, {"choices": [{"message": {"content": None, "tool_calls": [
            {"id": "1", "type": "function", "function": {"name": "run_shell", "arguments": "{}"}}]}}]})
        for pid, res in (("gemini", gemini), ("openrouter", openai), ("openai-compatible", openai)):
            with self.subTest(provider=pid):
                with self.assertRaises(ProviderError) as ctx:
                    get_provider(pid, MockTransport(res)).chat(ProviderConfig(pid, "m", KEY), [ChatMessage("user", "x")], "S")
                self.assertEqual(ctx.exception.kind, ErrorKind.TOOL_IGNORED)
        self.assertEqual(executed, [])

    def test_text_alongside_tool_call_returns_only_text(self):
        res = HttpResult(200, {"choices": [{"message": {"content": "hanya teks", "tool_calls": [{"id": "1"}]}}]})
        out = get_provider("openrouter", MockTransport(res)).chat(ProviderConfig("openrouter", "m", KEY), [], "S")
        self.assertEqual(out, "hanya teks")

    def test_controller_replies_are_text_only(self):
        c = self.controller()
        connect(c, save="y", use="1")
        self.transport.result = HttpResult(200, {"candidates": [{"content": {"parts": [
            {"text": "pakai ini: `ls`"}, {"functionCall": {"name": "x", "args": {}}}]}}]})
        for r in run(c, "halo") + run(c, "/settings"):
            self.assertIsInstance(r.text, str)
            self.assertIn(r.kind, {"user", "assistant", "system", "error"})

    def test_terminal_escape_sequences_from_model_are_stripped(self):
        dirty = "aman\x1b[2J\x1b[31mmerah\x1b[0m\x1b]0;judul\x07\x00\x08selesai"
        clean = clean_model_text(dirty)
        self.assertNotIn("\x1b", clean)
        self.assertNotIn("\x07", clean)
        self.assertIn("aman", clean)
        self.assertIn("selesai", clean)
        self.transport.result = HttpResult(200, {"candidates": [{"content": {"parts": [{"text": dirty}]}}]})
        out = get_provider("gemini", self.transport).chat(ProviderConfig("gemini", "m", KEY), [], "S")
        self.assertNotIn("\x1b", out)

    def test_system_prompt_states_text_only_limits(self):
        from linuxai.prompts.system import SYSTEM_PROMPT
        for phrase in ("hanya menghasilkan teks", "TIDAK bisa menjalankan perintah", "bahasa Indonesia"):
            self.assertIn(phrase, SYSTEM_PROMPT)
