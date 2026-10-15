import http.server
import os
import re
import stat
import threading
import unittest
from pathlib import Path

from linuxai.config.models import ProviderConfig
from linuxai.config.secrets import mask_key, redact
from linuxai.providers import get_provider
from linuxai.utils.http import post_json
from tests.helpers import KEY, MockTransport, TmpConfigCase, connect, run

PKG = Path(__file__).resolve().parents[1] / "linuxai"


class KeyHandlingTests(TmpConfigCase):
    def test_file_and_dir_permissions(self):
        connect(self.controller(), save="y")
        self.assertEqual(stat.S_IMODE(os.stat(self.store.directory).st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(os.stat(self.store.path).st_mode), 0o600)

    def test_loose_permissions_are_tightened_on_load(self):
        connect(self.controller(), save="y")
        os.chmod(self.store.path, 0o644)
        os.chmod(self.store.directory, 0o755)
        self.store.load()
        self.assertEqual(stat.S_IMODE(os.stat(self.store.path).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(self.store.directory).st_mode), 0o700)

    def test_key_never_appears_in_any_reply(self):
        c = self.controller()
        replies = connect(c, test="y", save="y", use="1")
        replies += run(c, "halo")
        replies += run(c, "/settings")
        replies += run(c, "/provider")
        replies += run(c, "/model")
        for r in replies:
            self.assertNotIn(KEY, r.text)

    def test_key_echo_is_hidden_and_input_is_masked_only_for_key_step(self):
        c = self.controller()
        run(c, "/connect"); run(c, "1")
        self.assertTrue(c.secret_input)
        replies = run(c, KEY)
        self.assertFalse(c.secret_input)
        self.assertTrue(replies[0].kind == "user" and KEY not in replies[0].text)

    def test_settings_shows_masked_key_only(self):
        c = self.controller()
        connect(c, save="y")
        text = run(c, "/settings")[-1].text
        self.assertNotIn(KEY, text)
        self.assertIn(KEY[-4:], text)
        self.assertEqual(mask_key("short"), "\u2022" * 8)

    def test_key_not_in_repr_history_or_errors(self):
        cfg = ProviderConfig("gemini", "m", KEY)
        self.assertNotIn(KEY, repr(cfg))
        c = self.controller()
        connect(c, save="y", use="1")
        run(c, "halo")
        self.assertNotIn(KEY, str(c.cloud_history))
        self.assertNotIn(KEY, redact(f"detail {KEY}", KEY))

    def test_key_only_sent_to_configured_provider_host(self):
        c = self.controller()
        connect(c, provider="2", save="y", use="1")
        self.transport.calls.clear()
        run(c, "halo")
        call = self.transport.calls[0]
        self.assertTrue(call["url"].startswith("https://openrouter.ai/"))
        self.assertNotIn(KEY, call["url"])
        self.assertNotIn(KEY, str(call["payload"]))

    def test_model_echoing_key_is_redacted(self):
        t = MockTransport()
        from tests.helpers import gemini_ok
        t.result = gemini_ok(f"kuncimu {KEY}")
        out = get_provider("gemini", t).chat(ProviderConfig("gemini", "m", KEY), [], "S")
        self.assertNotIn(KEY, out)


class SourceHygieneTests(unittest.TestCase):
    def test_no_embedded_credentials_in_source(self):
        pattern = re.compile(r"(AIza[0-9A-Za-z_\-]{20,}|sk-[A-Za-z0-9_\-]{20,}|sk-or-[A-Za-z0-9_\-]{10,})")
        for path in list(PKG.rglob("*.py")) + list(PKG.parent.glob("*.md")) + list((PKG.parent / "docs").glob("*.md")):
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), path)

    def test_no_logging_module_used(self):
        for path in PKG.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"^\s*(import|from)\s+logging\b", str(path))

    def test_gitignore_excludes_config(self):
        gi = (PKG.parent / ".gitignore").read_text()
        for item in ("config.json", ".env"):
            self.assertIn(item, gi)


class _Sink(http.server.BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):
        _Sink.seen.append(dict(self.headers))
        self.send_response(200); self.end_headers(); self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


class _Redirector(http.server.BaseHTTPRequestHandler):
    target = ""

    def do_POST(self):
        self.send_response(302)
        self.send_header("Location", _Redirector.target)
        self.end_headers()

    def log_message(self, *a):
        pass


class NoRedirectTests(unittest.TestCase):
    def test_redirect_is_not_followed_so_key_cannot_leak(self):
        sink = http.server.HTTPServer(("127.0.0.1", 0), _Sink)
        redirector = http.server.HTTPServer(("127.0.0.1", 0), _Redirector)
        _Redirector.target = f"http://127.0.0.1:{sink.server_port}/steal"
        _Sink.seen.clear()
        for srv in (sink, redirector):
            threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            res = post_json(f"http://127.0.0.1:{redirector.server_port}/", {"Authorization": f"Bearer {KEY}"}, {"a": 1}, timeout=5)
        finally:
            sink.shutdown(); redirector.shutdown()
            sink.server_close(); redirector.server_close()
        self.assertEqual(res.status, 302)
        self.assertEqual(_Sink.seen, [])
