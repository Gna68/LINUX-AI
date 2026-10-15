import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from linuxai import __version__, cli
from linuxai.core.controller import one_shot
from tests.helpers import MockTransport, gemini_ok, TmpConfigCase, connect


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.dict(os.environ, {"LINUXAI_CONFIG_DIR": self._tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def call(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_no_args_opens_tui_directly(self):
        with mock.patch.object(cli, "run_tui", return_value=0) as tui:
            self.assertEqual(cli.main([]), 0)
        tui.assert_called_once_with("local")

    def test_cloud_flag_without_question_opens_tui_in_cloud(self):
        with mock.patch.object(cli, "run_tui", return_value=0) as tui:
            cli.main(["--cloud"])
        tui.assert_called_once_with("cloud")

    def test_one_question_answers_without_tui_or_api_key(self):
        with mock.patch.object(cli, "run_tui") as tui:
            code, out, err = self.call(["apa", "itu", "sudo"])
        self.assertEqual(code, 0)
        self.assertIn("sudo", out)
        tui.assert_not_called()

    def test_local_flag(self):
        code, out, _ = self.call(["--local", "apa fungsi perintah grep"])
        self.assertEqual(code, 0)
        self.assertIn("grep", out)

    def test_unknown_question_exit_zero_honest_message(self):
        code, out, _ = self.call(["kapan indonesia merdeka"])
        self.assertEqual(code, 0)
        self.assertIn("belum punya jawaban", out)

    def test_local_and_cloud_conflict(self):
        code, _, err = self.call(["--local", "--cloud", "halo"])
        self.assertEqual(code, 2)

    def test_cloud_without_config_fails_cleanly(self):
        code, out, err = self.call(["--cloud", "halo"])
        self.assertEqual(code, 1)
        self.assertIn("belum dikonfigurasi", err)

    def test_cloud_flag_passes_cloud_mode(self):
        with mock.patch.object(cli, "one_shot", return_value=("ok", True)) as shot:
            self.call(["--cloud", "halo"])
        self.assertEqual(shot.call_args[0][1], "cloud")

    def test_version_and_help(self):
        code, out, _ = self.call(["--version"])
        self.assertEqual(code, 0)
        self.assertIn(__version__, out)
        code, out, _ = self.call(["--help"])
        self.assertEqual(code, 0)
        for word in ("--local", "--cloud", "--version", "/connect"):
            self.assertIn(word, out)

    def test_missing_textual_gives_friendly_error(self):
        real_import = __import__

        def fake(name, *a, **k):
            if name == "linuxai.app":
                raise ImportError("textual")
            return real_import(name, *a, **k)

        with mock.patch("builtins.__import__", side_effect=fake):
            code, _, err = self.call([])
        self.assertEqual(code, 1)
        self.assertIn("textual", err)


class OneShotCloudTests(TmpConfigCase):
    def test_one_shot_cloud_uses_configured_provider(self):
        connect(self.controller(), save="y")
        transport = MockTransport(gemini_ok("dari cloud"))
        text, ok = one_shot("halo", "cloud", store=self.store, transport=transport)
        self.assertTrue(ok)
        self.assertEqual(text, "dari cloud")
        self.assertEqual(len(transport.calls), 1)

    def test_one_shot_local_never_calls_transport(self):
        transport = MockTransport()
        one_shot("halo", "local", store=self.store, transport=transport)
        self.assertEqual(transport.calls, [])
