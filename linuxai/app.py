# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""TUI layar penuh LinuxAI (Textual). Logika ada di core.controller."""
from __future__ import annotations

import asyncio
from typing import Callable, List, Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from linuxai.core.commands import filter_commands
from linuxai.core.controller import Controller, Outcome, Reply
from linuxai.ui import render
from linuxai.ui.css import APP_CSS
from linuxai.ui.dialogs import ChoiceDialog, InputDialog

MAX_WIDGETS = 300


def _to_text(lines: List[render.Line], justify: Optional[str] = None) -> Text:
    out = Text(justify=justify) if justify else Text()
    for i, line in enumerate(lines):
        if i:
            out.append("\n")
        for seg, style in line:
            out.append(seg, style=style or None)
    return out


class LinuxAIApp(App):
    TITLE = "LinuxAI"
    CSS = APP_CSS
    BINDINGS = [
        Binding("ctrl+c", "quit_app", "Keluar", show=False, priority=True),
        Binding("escape", "cancel", "Batal", show=False),
        Binding("pageup", "chat_page_up", "Scroll naik", show=False),
        Binding("pagedown", "chat_page_down", "Scroll turun", show=False),
        Binding("ctrl+l", "clear_chat", "Bersihkan", show=False),
        Binding("ctrl+t", "toggle_theme", "Tema", show=False),
        Binding("up", "suggest_prev", "Saran sebelumnya", show=False, priority=True),
        Binding("down", "suggest_next", "Saran berikutnya", show=False, priority=True),
        Binding("tab", "suggest_accept", "Lengkapi", show=False, priority=True),
    ]

    def __init__(self, controller: Optional[Controller] = None):
        super().__init__()
        self.controller = controller or Controller()
        self.controller.echo_wizard = False  # wizard memakai dialog, bukan chat
        self._dialog_open = False
        self._busy = False
        self._busy_note = ""
        self._frame = 0
        self._spinner = None
        self._chat_started = False
        self._sug: list = []
        self._sug_idx = 0

    def _q(self, selector, expect_type=None):
        """Query pada layar utama, tetap benar walau dialog modal sedang terbuka."""
        return self.screen_stack[0].query_one(selector, expect_type)

    # ------------------------------------------------------------ layout
    def compose(self) -> ComposeResult:
        yield Static(id="header")
        yield Static(id="hero")
        yield VerticalScroll(id="chat")
        yield Static(id="suggest")
        yield Static("/ perintah \u00b7 PgUp/PgDn scroll \u00b7 Esc batal \u00b7 Ctrl+T tema \u00b7 Shift+drag pilih teks", id="hints")
        yield Input(id="prompt", placeholder=self.controller.prompt_hint())
        yield Static(id="status")

    async def on_mount(self) -> None:
        self._q("#prompt", Input).focus()
        self._refresh_chrome()
        for reply in self.controller.startup_replies:
            await self._add_message(reply)

    def on_resize(self, event) -> None:
        if not self._chat_started:
            self._refresh_chrome()

    # ------------------------------------------------------------ chrome
    def _mode_label(self) -> str:
        return self.controller.mode.upper()

    def _refresh_chrome(self) -> None:
        width = max(self.size.width, 20)
        self._q("#hero", Static).update(
            _to_text(render.hero_lines(self._mode_label(), width), justify="center"))
        self._q("#header", Static).update(render.header_text(self._mode_label()))
        self._q("#status", Static).update(
            render.status_text(self.controller.status_line(), self._busy_note, self._frame))
        prompt = self._q("#prompt", Input)
        prompt.password = self.controller.secret_input
        prompt.placeholder = self.controller.prompt_hint()

    def _tick(self) -> None:
        self._frame += 1
        self._q("#status", Static).update(
            render.status_text(self.controller.status_line(), self._busy_note, self._frame))

    # ------------------------------------------------------------ saran "/"
    def _show_suggestions(self) -> None:
        box = self._q("#suggest", Static)
        if not self._sug:
            box.display = False
            return
        self._sug_idx = max(0, min(self._sug_idx, len(self._sug) - 1))
        box.update(_to_text(render.suggestion_lines(self._sug, self._sug_idx)))
        box.display = True

    def _hide_suggestions(self) -> None:
        self._sug = []
        self._sug_idx = 0
        self._q("#suggest", Static).display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "prompt":
            return
        if self.controller.in_wizard:
            self._hide_suggestions()
            return
        items = filter_commands(event.value)
        if [c[0] for c in items] != [c[0] for c in self._sug]:
            self._sug_idx = 0
        self._sug = items
        self._show_suggestions()

    def _modal(self):
        return self.screen if isinstance(self.screen, ModalScreen) else None

    def action_suggest_prev(self) -> None:
        if self._modal() is not None:
            self._modal().nav(-1)
            return
        if self._sug:
            self._sug_idx = (self._sug_idx - 1) % len(self._sug)
            self._show_suggestions()

    def action_suggest_next(self) -> None:
        if self._modal() is not None:
            self._modal().nav(1)
            return
        if self._sug:
            self._sug_idx = (self._sug_idx + 1) % len(self._sug)
            self._show_suggestions()

    def action_suggest_accept(self) -> None:
        """Tab: lengkapi perintah terpilih tanpa menjalankannya."""
        if self._modal() is None and self._sug:
            prompt = self._q("#prompt", Input)
            prompt.value = self._sug[self._sug_idx][0] + " "
            prompt.cursor_position = len(prompt.value)

    # ------------------------------------------------------------ pesan
    async def _add_message(self, reply: Reply) -> None:
        chat = self._q("#chat", VerticalScroll)
        if not self._chat_started:
            self._chat_started = True
            self._q("#hero").display = False
            self._q("#header").display = True
            chat.display = True
        widget = Static(_to_text(render.message_lines(reply.kind, reply.text)), classes=f"msg {reply.kind}")
        await chat.mount(widget)
        children = list(chat.children)
        for old in children[:-MAX_WIDGETS]:
            await old.remove()
        chat.scroll_end(animate=False)

    def _copy(self, text: str) -> None:
        try:
            self.copy_to_clipboard(text)
        except Exception:
            self.notify("Gagal menyalin. Perbarui Textual, atau tahan Shift lalu seret mouse untuk memilih teks.",
                        severity="error")

    async def _clear_chat(self) -> None:
        chat = self._q("#chat", VerticalScroll)
        for child in list(chat.children):
            await child.remove()

    def _visible(self, replies: List[Reply]) -> List[Reply]:
        """Saat dialog akan tampil, teks pertanyaan wizard tidak perlu masuk chat."""
        if self.controller.dialog_spec() is None:
            return list(replies)
        return [r for r in replies if r.kind != "system"]

    async def _apply(self, outcome: Outcome) -> None:
        if outcome.clear:
            await self._clear_chat()
        for reply in self._visible(outcome.replies):
            await self._add_message(reply)
        if outcome.copy is not None:
            self._copy(outcome.copy)
        if outcome.exit:
            self.exit()
            return
        self._refresh_chrome()
        if outcome.job is not None:
            self._start_job(outcome.job, outcome.job_label)
        else:
            self._maybe_open_dialog()

    # ------------------------------------------------------------ dialog /connect
    def _maybe_open_dialog(self) -> None:
        spec = self.controller.dialog_spec()
        if spec is None or self._dialog_open:
            return
        if spec.kind == "choice":
            screen = ChoiceDialog(spec.title, spec.options, searchable=spec.searchable, hint=spec.hint)
        else:
            screen = InputDialog(spec.title, placeholder=spec.placeholder, password=spec.password, hint=spec.hint)
        self._dialog_open = True
        self.push_screen(screen, self._dialog_done)

    async def _dialog_done(self, result) -> None:
        self._dialog_open = False
        if result is None:  # Esc
            await self._apply(self.controller.cancel_wizard())
            return
        await self._apply(self.controller.handle(result))

    # ------------------------------------------------------------ job cloud
    def _start_job(self, job: Callable[[], List[Reply]], label: str) -> None:
        self._busy = True
        self._busy_note = label or "Cloud AI sedang memproses..."
        self._spinner = self.set_interval(0.12, self._tick)
        self.run_worker(self._run_job(job), exclusive=True)

    async def _run_job(self, job: Callable[[], List[Reply]]) -> None:
        try:
            replies = await asyncio.to_thread(job)
        except Exception:  # jangan pernah crash karena permintaan cloud
            self.controller.abort_job()
            replies = [Reply("Terjadi kesalahan tak terduga saat memproses permintaan.", "error")]
        finally:
            if self._spinner is not None:
                self._spinner.stop()
                self._spinner = None
            self._busy = False
            self._busy_note = ""
        for reply in self._visible(replies):
            await self._add_message(reply)
        self._refresh_chrome()
        self._maybe_open_dialog()

    # ------------------------------------------------------------ input
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "prompt" or self._busy:
            return
        value = event.value
        if self._sug and value.startswith("/"):
            value = self._sug[self._sug_idx][0]  # Enter menjalankan saran yang disorot
        event.input.value = ""
        self._hide_suggestions()
        await self._apply(self.controller.handle(value))

    # ------------------------------------------------------------ aksi
    def action_quit_app(self) -> None:
        """Ctrl+C: jika ada teks yang dipilih, salin; jika tidak, keluar."""
        selected = None
        try:
            selected = self.screen.get_selected_text()
        except Exception:
            pass
        if selected:
            self._copy(selected)
            self.notify("Teks disalin.")
            return
        self.exit()

    async def action_cancel(self) -> None:
        if self._sug:
            self._hide_suggestions()
            return
        if not self._busy:
            await self._apply(self.controller.cancel_wizard())

    async def action_clear_chat(self) -> None:
        if not self._busy:
            await self._apply(self.controller.clear())

    def action_chat_page_up(self) -> None:
        self._q("#chat", VerticalScroll).scroll_page_up()

    def action_chat_page_down(self) -> None:
        self._q("#chat", VerticalScroll).scroll_page_down()

    def action_toggle_theme(self) -> None:
        try:
            self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"
        except Exception:
            try:
                self.dark = not self.dark
            except Exception:
                pass


def run(start_mode: str = "local") -> int:
    LinuxAIApp(Controller(start_mode=start_mode)).run()
    return 0
