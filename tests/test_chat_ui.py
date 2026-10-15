import asyncio
import unittest

from linuxai.core.controller import HELP_TEXT, Controller
from linuxai.ui import render
from tests.helpers import TmpConfigCase, connect, run

try:
    import textual  # noqa: F401
    HAVE_TEXTUAL = True
except ImportError:  # pragma: no cover
    HAVE_TEXTUAL = False


class RenderTests(unittest.TestCase):
    def flat(self, lines):
        return "\n".join("".join(seg for seg, _ in line) for line in lines)

    def test_hero_has_branding_tagline_description_and_mode(self):
        for width in (20, 40, 120):
            text = self.flat(render.hero_lines("LOCAL", width))
            self.assertIn("Your Linux Companion", text)
            self.assertIn("Ask anything about Linux.", text)
            self.assertIn("[ LOCAL ]", text)
            self.assertIn("/help", text)
        self.assertIn("CLOUD", self.flat(render.hero_lines("CLOUD", 80)))

    def test_code_fences_become_code_lines(self):
        lines = render.message_lines("assistant", "Coba:\n```\nsudo apt update\n```\nSelesai")
        flat = self.flat(lines)
        self.assertIn("\u2502 sudo apt update", flat)
        self.assertNotIn("```", flat)
        self.assertEqual(lines[0], [("LinuxAI", "bold green")])

    def test_shell_highlighting_keeps_text_and_colors_tokens(self):
        for line in ("sudo apt update && sudo apt install -y htop # pasang", 'ls -la ~/x | grep "foto"',
                     "# komentar", "$ cd ..", "echo 'a b' > x.txt", "", "   ", "unterminated 'quote"):
            segs = render.shell_segments(line)
            self.assertEqual("".join(t for t, _ in segs), line)
        d = dict((t, st) for t, st in render.shell_segments("sudo apt install -y htop"))
        self.assertEqual((d["sudo"], d["apt"], d["-y"]), ("bold red", "bold green", "yellow"))
        self.assertEqual(dict(render.shell_segments('grep "x"'))['"x"'], "magenta")
        self.assertEqual(render.shell_segments("# catatan")[0][1], "dim")
        self.assertEqual(dict(render.shell_segments("echo a > file.txt"))["file.txt"], "")  # target redirect bukan perintah

    def test_inline_markdown_is_colored_and_markers_removed(self):
        segs = render.inline_segments("pakai `ls` dan **tebal** ya")
        self.assertEqual("".join(t for t, _ in segs), "pakai ls dan tebal ya")
        self.assertIn(("ls", "bold cyan"), segs)
        self.assertIn(("tebal", "bold"), segs)

    def test_lists_headings_and_slash_commands_colored(self):
        flat = self.flat(render.message_lines("assistant", "# Judul\n- satu\n1. dua"))
        self.assertIn("Judul", flat); self.assertNotIn("# ", flat)
        self.assertIn("\u2022 satu", flat)
        lines = render.message_lines("system", "/connect   Hubungkan")
        self.assertEqual(lines[1][0], ("/connect", "bold cyan"))

    def test_user_and_error_messages_are_not_reformatted(self):
        self.assertEqual(self.flat(render.message_lines("user", "**x** `y` # z")), "Kamu\n**x** `y` # z")
        self.assertEqual(self.flat(render.message_lines("error", "gagal `x`")), "Error\ngagal `x`")

    def test_non_shell_code_block_not_shell_colored(self):
        lines = render.message_lines("assistant", "```python\nprint(1)\n```")
        self.assertEqual(lines[1][1], ("print(1)", "bold"))

    def test_markup_like_text_is_kept_literal(self):
        flat = self.flat(render.message_lines("assistant", "[bold red]x[/] \x1b"))
        self.assertIn("[bold red]x[/]", flat)

    def test_big_logo_scales_with_width(self):
        for width, expect_rows in ((120, 5), (60, 5), (30, 1)):
            rows = render.logo_lines(width)
            self.assertEqual(len(rows), expect_rows)
            for row in rows:
                self.assertLessEqual(len("".join(seg for seg, _ in row)), width)
        wide = self.flat(render.logo_lines(120))
        self.assertIn("\u2588", wide)
        self.assertEqual({st for _, st in render.logo_lines(120)[0]} - {""}, {"dim", "bold"})

    def test_suggestion_menu_highlights_selected_row(self):
        from linuxai.core.commands import filter_commands
        items = filter_commands("/")
        self.assertEqual([c[0] for c in items], sorted(c[0] for c in items))
        lines = render.suggestion_lines(items, 1)
        self.assertEqual(lines[1][0][1], "bold reverse")
        self.assertNotEqual(lines[0][0][1], "bold reverse")

    def test_filter_commands(self):
        from linuxai.core.commands import filter_commands
        self.assertEqual([c[0] for c in filter_commands("/mo")], ["/mode", "/model"])
        self.assertEqual([c[0] for c in filter_commands("/CO")], ["/connect", "/copy"])
        self.assertEqual(filter_commands("halo"), [])
        self.assertEqual(filter_commands("/model gpt"), [])  # sudah ada argumen
        self.assertTrue(filter_commands("/ett"))  # cocok sebagian: /settings

    def test_spinner_and_status(self):
        self.assertTrue(render.status_text("LOCAL", "Menunggu", 3).endswith("Menunggu"))
        self.assertEqual(render.status_text("LOCAL"), "LOCAL")


class ChatFlowTests(TmpConfigCase):
    def test_repeated_conversation_in_one_session(self):
        c = self.controller()
        for q in ("apa itu sudo", "cara install aplikasi di linux", "wifi tidak muncul"):
            replies = run(c, q)
            self.assertEqual([r.kind for r in replies], ["user", "assistant"])

    def test_dialog_specs_follow_wizard_steps(self):
        c = self.controller()
        self.assertIsNone(c.dialog_spec())
        run(c, "/connect")
        spec = c.dialog_spec()
        self.assertEqual((spec.kind, spec.searchable), ("choice", True))
        self.assertEqual([v for _, v in spec.options], ["gemini", "openrouter", "openai-compatible"])
        run(c, "gemini")
        spec = c.dialog_spec()  # API key dulu
        self.assertEqual((spec.kind, spec.password), ("input", True))
        run(c, "TESTKEY-1234567890")
        self.assertEqual([v for _, v in c.dialog_spec().options], ["y", "n"])  # ambil daftar model?
        run(c, "y")
        spec = c.dialog_spec()  # pilih model dari daftar
        self.assertTrue(spec.searchable)
        run(c, "model-a")
        self.assertEqual([v for _, v in c.dialog_spec().options], ["y", "n"])  # tes?
        run(c, "n")
        self.assertEqual([v for _, v in c.dialog_spec().options], ["y", "n"])  # simpan?
        run(c, "n")
        self.assertEqual([v for _, v in c.dialog_spec().options], ["1", "2"])
        run(c, "1")
        self.assertIsNone(c.dialog_spec())
        self.assertEqual(c.mode, "cloud")
        self.assertEqual(c.active_config.model, "model-a")

    def test_manual_model_dialog_when_list_skipped(self):
        c = self.controller()
        run(c, "/connect"); run(c, "gemini"); run(c, "TESTKEY-1234567890"); run(c, "n")
        spec = c.dialog_spec()
        self.assertEqual((spec.kind, spec.password), ("input", False))
        self.assertIn("ai.google.dev", spec.hint)

    def test_dialog_values_drive_the_same_wizard_and_cancel_works(self):
        c = self.controller()
        run(c, "/connect")
        self.assertIsNotNone(c.dialog_spec())
        c.cancel_wizard()
        self.assertIsNone(c.dialog_spec())

    def test_openai_compatible_has_base_url_dialog(self):
        c = self.controller()
        run(c, "/connect"); run(c, "openai-compatible")
        self.assertIn("Base URL", c.dialog_spec().title)

    def test_dialog_mode_suppresses_echo_and_key_never_in_dialog_spec(self):
        c = self.controller()
        c.echo_wizard = False
        run(c, "/connect"); run(c, "1")
        replies = run(c, "TESTKEY-1234567890")
        self.assertNotIn("user", [r.kind for r in replies])
        run(c, "n")
        replies = run(c, "model-x")
        self.assertNotIn("user", [r.kind for r in replies])
        spec = c.dialog_spec()
        self.assertNotIn("TESTKEY-1234567890", repr(spec))

    def test_final_message_includes_connection_summary(self):
        c = self.controller()
        connect(c, save="n", use="1")
        # use_now terakhir memuat ringkasan koneksi
        c2 = self.controller()
        for step in ("/connect", "1", "TESTKEY-1234567890", "n", "m-x", "n", "n"):
            run(c2, step)
        last = run(c2, "1")[-1].text
        self.assertIn("Terhubung ke", last)
        self.assertIn("Cloud Mode aktif", last)

    def test_copy_command(self):
        c = self.controller()
        self.assertEqual(run(c, "/copy")[-1].kind, "error")  # belum ada jawaban
        run(c, "apa itu sudo")
        out = c.handle("/copy")
        self.assertIn("sudo", out.copy)
        self.assertEqual(out.replies[0].kind, "system")

    def test_empty_input_is_ignored(self):
        out = self.controller().handle("   ")
        self.assertEqual(out.replies, [])

    def test_slash_commands(self):
        c = self.controller()
        self.assertEqual(run(c, "/help")[0].text, HELP_TEXT)
        for cmd in ("/connect", "/provider", "/model", "/mode", "/help", "/clear", "/settings", "/exit"):
            self.assertIn(cmd, HELP_TEXT)
        self.assertTrue(c.handle("/clear").clear)
        self.assertTrue(c.handle("/exit").exit)
        self.assertEqual(run(c, "/tidak-ada")[0].kind, "error")
        self.assertEqual(run(c, "/mode")[0].text.split()[0], "Cloud")  # toggle gagal: belum dikonfigurasi

    def test_help_text_in_local_mode_answers_are_plain_text(self):
        for r in run(self.controller(), "apa itu terminal"):
            self.assertIsInstance(r.text, str)

    def test_prompt_hint_and_secret_flag_follow_wizard(self):
        c = self.controller()
        self.assertFalse(c.secret_input)
        run(c, "/connect"); run(c, "1")
        self.assertTrue(c.secret_input)
        self.assertIn("tersembunyi", c.prompt_hint())

    def test_clear_resets_cloud_context(self):
        c = self.controller()
        connect(c, save="y", use="1")
        run(c, "halo")
        self.assertTrue(c.cloud_history)
        c.handle("/clear")
        self.assertEqual(c.cloud_history, [])

    def test_startup_notice_when_cloud_requested_but_unconfigured(self):
        c = self.controller(start_mode="cloud")
        self.assertEqual(c.mode, "local")
        self.assertTrue(c.startup_replies)


@unittest.skipUnless(HAVE_TEXTUAL, "textual tidak terpasang di lingkungan ini")
class TextualAppTests(TmpConfigCase):
    def drive(self, scenario):
        from linuxai.app import LinuxAIApp
        self.controller_ref = self.controller()
        app = LinuxAIApp(self.controller_ref)

        async def main():
            async with app.run_test(size=(100, 30)) as pilot:
                await scenario(app, pilot)

        asyncio.run(main())

    def test_opens_with_centered_branding_and_input(self):
        async def scenario(app, pilot):
            await pilot.pause()
            self.assertTrue(app.query_one("#hero").display)
            self.assertFalse(app.query_one("#chat").display)
            self.assertTrue(app.query_one("#prompt").has_focus)
        self.drive(scenario)

    def test_message_flow_switches_to_chat_view(self):
        async def scenario(app, pilot):
            app.query_one("#prompt").value = "apa itu sudo"
            await pilot.press("enter")
            await pilot.pause()
            self.assertFalse(app.query_one("#hero").display)
            self.assertTrue(app.query_one("#chat").display)
            self.assertGreaterEqual(len(app.query_one("#chat").children), 2)
        self.drive(scenario)

    def test_slash_opens_suggestion_menu_and_enter_runs_selection(self):
        async def scenario(app, pilot):
            prompt = app.query_one("#prompt")
            prompt.value = "/"
            await pilot.pause()
            self.assertTrue(app.query_one("#suggest").display)
            prompt.value = "/he"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            self.assertFalse(app.query_one("#suggest").display)
            self.assertTrue(app.query_one("#chat").display)  # /help dijalankan
        self.drive(scenario)

    def test_connect_opens_popup_dialogs_in_order(self):
        from linuxai.ui.dialogs import ChoiceDialog, InputDialog

        async def scenario(app, pilot):
            app.query_one("#prompt").value = "/connect"
            await pilot.press("enter")
            await pilot.pause()
            self.assertIsInstance(app.screen, ChoiceDialog)  # pilih provider
            await pilot.press("enter")  # provider pertama
            await pilot.pause()
            self.assertIsInstance(app.screen, InputDialog)  # API key (tersembunyi)
            self.assertTrue(app.screen.query_one("#dlg-input").password)
            app.screen.query_one("#dlg-input").value = "TESTKEY-1234567890"
            await pilot.press("enter")
            await pilot.pause()
            self.assertIsInstance(app.screen, ChoiceDialog)  # ambil daftar model?
            await pilot.press("escape")  # batal
            await pilot.pause()
            self.assertNotIsInstance(app.screen, (ChoiceDialog, InputDialog))
            self.assertIsNone(self.controller_ref.active_config)
        self.drive(scenario)
