"""Dialog pop-up modal (ala OpenCode) untuk /connect: pilih provider, isi model, isi API key."""
from __future__ import annotations

from typing import List, Optional, Tuple

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option


class _Dialog(ModalScreen):
    BINDINGS = [Binding("escape", "cancel", "Batal")]

    def action_cancel(self) -> None:
        self.dismiss(None)

    def nav(self, delta: int) -> None:  # dipanggil app saat tombol panah ditekan
        pass


class ChoiceDialog(_Dialog):
    """Daftar pilihan; opsional kolom pencarian. Mengembalikan nilai pilihan atau None (Esc)."""

    def __init__(self, title: str, options: List[Tuple[str, str]], searchable: bool = False, hint: str = ""):
        super().__init__()
        self._title, self._options = title, list(options)
        self._searchable, self._hint = searchable, hint

    def compose(self):
        with Vertical(id="dialog"):
            with Horizontal(id="dlg-head"):
                yield Static(self._title, id="dlg-title")
                yield Static("esc", id="dlg-esc")
            if self._searchable:
                yield Input(placeholder="Search", id="dlg-search")
            yield OptionList(*[Option(Text(label), id=value) for label, value in self._options], id="dlg-list")
            if self._hint:
                yield Static(self._hint, id="dlg-hint")

    def on_mount(self) -> None:
        lst = self.query_one("#dlg-list", OptionList)
        if self._options:
            lst.highlighted = 0
        (self.query_one("#dlg-search", Input) if self._searchable else lst).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        q = event.value.strip().lower()
        items = [o for o in self._options if q in o[0].lower() or q in o[1].lower()]
        lst = self.query_one("#dlg-list", OptionList)
        lst.clear_options()
        lst.add_options([Option(Text(label), id=value) for label, value in items])
        if items:
            lst.highlighted = 0

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.query_one("#dlg-list", OptionList).action_select()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def nav(self, delta: int) -> None:
        lst = self.query_one("#dlg-list", OptionList)
        lst.action_cursor_down() if delta > 0 else lst.action_cursor_up()


class InputDialog(_Dialog):
    """Satu kolom input (opsional tersembunyi untuk API key). Mengembalikan teks atau None (Esc)."""

    def __init__(self, title: str, placeholder: str = "", password: bool = False, hint: str = ""):
        super().__init__()
        self._title, self._placeholder = title, placeholder
        self._password, self._hint = password, hint

    def compose(self):
        with Vertical(id="dialog"):
            with Horizontal(id="dlg-head"):
                yield Static(self._title, id="dlg-title")
                yield Static("esc", id="dlg-esc")
            yield Input(placeholder=self._placeholder, password=self._password, id="dlg-input")
            if self._hint:
                yield Static(self._hint, id="dlg-hint")
            yield Static(Text.assemble(("enter", "bold"), " submit"), id="dlg-hint2")

    def on_mount(self) -> None:
        self.query_one("#dlg-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.dismiss(event.value)
