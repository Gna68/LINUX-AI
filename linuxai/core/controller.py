# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Otak aplikasi: mode, sesi chat, slash commands, wizard /connect.

Tidak bergantung pada Textual sehingga bisa diuji tanpa UI. Controller hanya
menghasilkan teks (Reply). Permintaan cloud dikembalikan sebagai `job`
(callable) agar UI bisa menjalankannya di thread terpisah tanpa membeku.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from linuxai import __version__
from linuxai.cloud.base import ChatMessage, ErrorKind, ProviderError
from linuxai.cloud.client import CloudClient
from linuxai.config.models import ProviderConfig, StoredConfig
from linuxai.config.secrets import mask_key
from linuxai.config.store import ConfigStore
from linuxai.config.validation import (
    ValidationError, validate_api_key, validate_base_url, validate_model,
)
from linuxai.local.assistant import LocalAssistant
from linuxai.providers import PROVIDER_CLASSES, provider_ids

MAX_CLOUD_HISTORY = 40  # jumlah pesan (genap) yang dikirim sebagai konteks
MAX_INPUT_LEN = 8000
CANCEL_WORDS = {"batal", "cancel", "/cancel", "/batal"}
YES = {"y", "ya", "yes", "iya"}
NO = {"n", "no", "tidak", "t"}

HELP_TEXT = """Perintah LinuxAI:
/connect   Hubungkan provider AI (Cloud Mode) dan masukkan API key
/provider  Lihat atau ganti provider  (contoh: /provider 2)
/model     Lihat atau ganti model     (contoh: /model nama-model)
/mode      Pindah Local <-> Cloud     (/mode local | /mode cloud)
/settings  Pengaturan; hapus API key (/settings delete-key, /settings delete-all)
/clear     Bersihkan percakapan
/copy      Salin jawaban terakhir ke clipboard
/help      Tampilkan bantuan ini
/exit      Keluar (atau Ctrl+C)

Local Mode (default) memakai basis pengetahuan bawaan tanpa internet/API key.
Cloud Mode mengirim percakapan ke provider yang kamu pilih.
LinuxAI hanya chatbot: tidak menjalankan perintah di komputermu."""


@dataclass
class Reply:
    text: str
    kind: str = "assistant"  # user | assistant | system | error


@dataclass
class DialogSpec:
    """Deskripsi dialog pop-up untuk langkah wizard saat ini (dirender oleh UI)."""
    kind: str  # "choice" | "input"
    title: str
    options: List[Tuple[str, str]] = field(default_factory=list)  # (label, nilai)
    placeholder: str = ""
    password: bool = False
    hint: str = ""
    searchable: bool = False


@dataclass
class Outcome:
    replies: List[Reply] = field(default_factory=list)
    job: Optional[Callable[[], List[Reply]]] = None
    job_label: str = ""
    clear: bool = False
    exit: bool = False
    copy: Optional[str] = None


class Controller:
    def __init__(
        self,
        store: Optional[ConfigStore] = None,
        transport=None,
        get_transport=None,
        assistant: Optional[LocalAssistant] = None,
        start_mode: str = "local",
    ):
        self.store = store or ConfigStore()
        self.transport = transport
        self.get_transport = get_transport
        self.assistant = assistant or LocalAssistant()
        self.stored: StoredConfig = self.store.load()
        self.session_configs: Dict[str, ProviderConfig] = {}
        self.active_id: Optional[str] = self.stored.active_provider
        self.mode = "local"
        self.cloud_history: List[ChatMessage] = []
        self.last_reply: Optional[str] = None
        self._unsent: Optional[str] = None  # pesan cloud yang gagal terkirim, ikut dikirim lagi nanti
        self.echo_wizard = True  # UI dengan dialog mematikan echo jawaban wizard
        self._step: Optional[str] = None
        self._data: dict = {}
        self.startup_replies: List[Reply] = []
        if start_mode == "cloud":
            if self.active_config is not None:
                self.mode = "cloud"
            else:
                self.startup_replies.append(Reply(
                    "Cloud Mode belum dikonfigurasi, jadi LinuxAI dimulai di Local Mode. Ketik /connect untuk menghubungkan provider.",
                    "system"))

    # ------------------------------------------------------------ state
    def _configs(self) -> Dict[str, ProviderConfig]:
        merged = dict(self.stored.providers)
        merged.update(self.session_configs)
        return merged

    @property
    def active_config(self) -> Optional[ProviderConfig]:
        return self._configs().get(self.active_id) if self.active_id else None

    @property
    def secret_input(self) -> bool:
        return self._step == "key"

    @property
    def in_wizard(self) -> bool:
        return self._step is not None

    def dialog_spec(self) -> Optional[DialogSpec]:
        """Dialog yang harus tampil untuk langkah wizard saat ini (None jika tidak ada)."""
        step, d = self._step, self._data
        if step is None or step == "busy":
            return None
        if step == "provider":
            cfgs, opts = self._configs(), []
            for pid in provider_ids():
                label = PROVIDER_CLASSES[pid].label
                if pid == self.active_id:
                    label += "  (aktif)"
                elif pid in cfgs:
                    label += "  (terhubung)"
                opts.append((label, pid))
            return DialogSpec("choice", "Hubungkan provider", opts, searchable=True,
                              hint="Kamu memakai API key milikmu sendiri.")
        existing = self._configs().get(d.get("provider", ""))
        if step == "models_consent":
            cls = PROVIDER_CLASSES[d["provider"]]
            return DialogSpec("choice", f"Ambil daftar model dari {cls.label}?",
                              [("Ya, ambil daftar model", "y"), ("Ketik nama model manual", "n")],
                              hint="API key-mu dikirim ke provider ini hanya untuk meminta daftar model.")
        if step == "model_pick":
            opts = [("\u270e Ketik nama model manual", "__manual__")] + [(m, m) for m in d.get("models", [])]
            return DialogSpec("choice", "Pilih model", opts, searchable=True,
                              hint=f"{len(opts) - 1} model tersedia. Ketik untuk mencari.")
        if step == "model":
            cls = PROVIDER_CLASSES[d["provider"]]
            hint = f"Salin nama persis dari dokumentasi resmi:\n{cls.docs_url}"
            if existing:
                hint += f"\nKosongkan lalu Enter = tetap pakai '{existing.model}'."
            return DialogSpec("input", f"Nama model \u00b7 {cls.label}", placeholder="nama-model", hint=hint)
        if step == "base_url":
            cls = PROVIDER_CLASSES[d["provider"]]
            return DialogSpec("input", "Base URL API", placeholder=cls.default_base_url or "https://...",
                              hint="Kosongkan lalu Enter = pakai nilai default. Harus https:// (http:// hanya localhost).")
        if step == "key":
            hint = "Disembunyikan dan tidak ditampilkan lagi."
            if existing:
                hint += "\nKosongkan lalu Enter = tetap pakai key yang sudah ada."
            return DialogSpec("input", "API key", placeholder="API key", password=True, hint=hint)
        if step == "test_consent":
            return DialogSpec("choice", "Kirim permintaan uji ke provider?",
                              [("Ya, kirim tes sederhana", "y"), ("Lewati tes", "n")],
                              hint="Isinya satu kalimat tes tanpa data percakapan, tetapi dapat memakai kuota API-mu.")
        if step == "save_consent":
            return DialogSpec("choice", "Simpan konfigurasi?",
                              [("Simpan di disk (izin 0600, tidak terenkripsi)", "y"), ("Hanya untuk sesi ini", "n")],
                              hint=str(self.store.path))
        if step == "use_now":
            return DialogSpec("choice", "Pakai sekarang?", [("Cloud Mode", "1"), ("Tetap Local Mode", "2")])
        if step == "confirm":
            what = "semua konfigurasi dan API key" if d.get("action") == "delete-all" else "API key provider ini"
            return DialogSpec("choice", "Konfirmasi hapus", [("Ya, hapus", "ya"), ("Batal", "tidak")],
                              hint=f"Hapus {what}?")
        return None

    def status_line(self) -> str:
        if self.mode == "cloud" and self.active_config:
            cfg = self.active_config
            return f"CLOUD · {PROVIDER_CLASSES[cfg.provider].label} · {cfg.model}"
        return "LOCAL · tanpa internet"

    def prompt_hint(self) -> str:
        if self._step == "key":
            return "Tempel API key (tersembunyi) · Enter · 'batal' untuk membatalkan"
        if self._step:
            return "Jawab pertanyaan di atas · 'batal' untuk membatalkan"
        return "Tanya apa saja tentang Linux...  (/help untuk bantuan)"

    def _reload(self) -> None:
        self.stored = self.store.load()

    # ------------------------------------------------------------ entry
    def handle(self, text: str) -> Outcome:
        text = (text or "").strip()
        if self._step:
            return self._wizard_input(text)
        if not text:
            return Outcome()
        if len(text) > MAX_INPUT_LEN:
            return Outcome([Reply(f"Pesan terlalu panjang (maks. {MAX_INPUT_LEN} karakter).", "error")])
        if text.startswith("/"):
            return self._command(text)
        return self._chat(text)

    def _reset_context(self) -> None:
        """Kosongkan konteks cloud, termasuk pesan gagal-kirim yang tertunda."""
        self.cloud_history = []
        self._unsent = None

    def clear(self) -> Outcome:
        self._reset_context()
        return Outcome(clear=True)

    def cancel_wizard(self) -> Outcome:
        if not self._step or self._step == "busy":
            return Outcome()
        self._reset_wizard()
        return Outcome([Reply("Dibatalkan. Konfigurasi tidak diubah.", "system")])

    def abort_job(self) -> None:
        if self._step == "busy":
            self._reset_wizard()

    def _reset_wizard(self) -> None:
        self._step = None
        self._data = {}

    # ------------------------------------------------------------ chat
    def _chat(self, text: str) -> Outcome:
        user = Reply(text, "user")
        if self.mode == "local":
            answer = self.assistant.answer(text).text
            self.last_reply = answer
            return Outcome([user, Reply(answer, "assistant")])
        cfg = self.active_config
        if cfg is None:
            self.mode = "local"
            return Outcome([user, Reply("Cloud Mode belum dikonfigurasi. Ketik /connect.", "error")])
        pending = self._unsent
        content = text if (pending is None or pending == text) else pending + "\n\n" + text
        messages = self.cloud_history[-MAX_CLOUD_HISTORY:] + [ChatMessage("user", content)]
        client = CloudClient(self.transport, get_transport=self.get_transport)

        def job() -> List[Reply]:
            try:
                answer = client.send(cfg, messages)
            except ProviderError as err:
                self._unsent = content  # jangan hilangkan pesan yang gagal terkirim
                return [Reply(err.message + "\nPesanmu tidak hilang: akan ikut terkirim bersama pesan berikutnya.", "error")]
            self._unsent = None
            self.cloud_history += [ChatMessage("user", content), ChatMessage("assistant", answer)]
            self.cloud_history = self.cloud_history[-MAX_CLOUD_HISTORY:]
            self.last_reply = answer
            return [Reply(answer, "assistant")]

        return Outcome([user], job=job, job_label="Cloud AI sedang memproses...")

    # ------------------------------------------------------------ slash
    def _command(self, text: str) -> Outcome:
        name, _, arg = text.partition(" ")
        name, arg = name.lower(), arg.strip()
        table = {
            "/help": lambda: Outcome([Reply(HELP_TEXT, "system")]),
            "/exit": lambda: Outcome(exit=True),
            "/quit": lambda: Outcome(exit=True),
            "/clear": self.clear,
            "/copy": self._cmd_copy,
            "/connect": self._start_wizard,
            "/mode": lambda: self._cmd_mode(arg),
            "/provider": lambda: self._cmd_provider(arg),
            "/model": lambda: self._cmd_model(arg),
            "/settings": lambda: self._cmd_settings(arg),
            "/version": lambda: Outcome([Reply(f"LinuxAI {__version__}", "system")]),
        }
        handler = table.get(name)
        if handler is None:
            return Outcome([Reply(f"Perintah {name} tidak dikenal. Ketik /help.", "error")])
        return handler()

    def _sys(self, text: str, kind: str = "system") -> Outcome:
        return Outcome([Reply(text, kind)])

    def _cmd_copy(self) -> Outcome:
        if not self.last_reply:
            return self._sys("Belum ada jawaban untuk disalin.", "error")
        return Outcome([Reply("Jawaban terakhir disalin ke clipboard.", "system")], copy=self.last_reply)

    def _cmd_mode(self, arg: str) -> Outcome:
        arg = arg.lower()
        target = arg if arg in ("local", "cloud") else ("local" if self.mode == "cloud" else "cloud")
        if arg and arg not in ("local", "cloud"):
            return self._sys("Pakai: /mode local  atau  /mode cloud", "error")
        if target == "cloud":
            if self.active_config is None:
                return self._sys("Cloud Mode belum dikonfigurasi. Ketik /connect dulu.", "error")
            self.mode = "cloud"
            cfg = self.active_config
            return self._sys(f"Cloud Mode aktif ({PROVIDER_CLASSES[cfg.provider].label}, model {cfg.model}). "
                             "Pesanmu akan dikirim ke provider tersebut.")
        self.mode = "local"
        self._unsent = None  # pesan cloud yang tertunda tidak dibawa ke Local
        return self._sys("Local Mode aktif. Tidak ada data yang dikirim ke internet.")

    def _provider_list(self) -> str:
        cfgs = self._configs()
        lines = []
        for i, pid in enumerate(provider_ids(), 1):
            tags = []
            if pid in cfgs:
                tags.append(f"model: {cfgs[pid].model}")
            if pid == self.active_id:
                tags.append("AKTIF")
            lines.append(f"  {i}. {PROVIDER_CLASSES[pid].label} [{pid}]" + (f"  ({', '.join(tags)})" if tags else ""))
        return "\n".join(lines)

    def _resolve_provider(self, text: str) -> Optional[str]:
        ids = provider_ids()
        t = text.strip().lower()
        if t.isdigit() and 1 <= int(t) <= len(ids):
            return ids[int(t) - 1]
        return t if t in ids else None

    def _cmd_provider(self, arg: str) -> Outcome:
        if not arg:
            return self._sys("Provider:\n" + self._provider_list() +
                             "\n\nGanti: /provider <nomor|id> (harus sudah dikonfigurasi lewat /connect).")
        pid = self._resolve_provider(arg)
        if pid is None:
            return self._sys("Provider tidak dikenal. Ketik /provider untuk melihat daftar.", "error")
        if pid not in self._configs():
            return self._sys(f"{PROVIDER_CLASSES[pid].label} belum dikonfigurasi. Ketik /connect.", "error")
        if pid != self.active_id:
            self._reset_context()  # jangan bawa percakapan ke provider lain
        self.active_id = pid
        if pid in self.stored.providers:
            try:
                self.store.set_active(pid)
                self._reload()
            except OSError:
                pass
        return self._sys(f"Provider aktif: {PROVIDER_CLASSES[pid].label}. Riwayat percakapan cloud dikosongkan.")

    def _cmd_model(self, arg: str) -> Outcome:
        cfg = self.active_config
        if cfg is None:
            return self._sys("Belum ada provider aktif. Ketik /connect.", "error")
        if not arg:
            return self._sys(f"Model saat ini: {cfg.model} ({PROVIDER_CLASSES[cfg.provider].label}).\n"
                             f"Ganti: /model <nama-model>. Daftar model resmi: {PROVIDER_CLASSES[cfg.provider].docs_url}")
        try:
            model = validate_model(arg)
        except ValidationError as err:
            return self._sys(str(err), "error")
        updated = ProviderConfig(cfg.provider, model, cfg.api_key, cfg.base_url)
        persisted = False
        if cfg.provider in self.stored.providers:
            try:
                self.store.update_model(cfg.provider, model)
                self._reload()
                self.session_configs.pop(cfg.provider, None)
                persisted = True
            except OSError:
                pass
        if not persisted:
            self.session_configs[cfg.provider] = updated
        return self._sys(f"Model diganti ke: {model}")

    def _cmd_settings(self, arg: str) -> Outcome:
        sub, _, rest = arg.partition(" ")
        sub, rest = sub.lower(), rest.strip()
        if sub == "delete-key":
            pid = self._resolve_provider(rest) if rest else self.active_id
            if pid is None or pid not in self._configs():
                return self._sys("Tidak ada API key yang bisa dihapus untuk provider itu.", "error")
            self._step, self._data = "confirm", {"action": "delete-key", "provider": pid}
            return self._sys(f"Hapus API key {PROVIDER_CLASSES[pid].label}? Ketik 'ya' untuk konfirmasi.")
        if sub == "delete-all":
            self._step, self._data = "confirm", {"action": "delete-all"}
            return self._sys("Hapus SEMUA konfigurasi dan API key tersimpan? Ketik 'ya' untuk konfirmasi.")
        if sub:
            return self._sys("Pakai: /settings, /settings delete-key [provider], atau /settings delete-all", "error")
        cfg = self.active_config
        lines = [
            f"Mode: {self.mode.upper()}",
            f"Provider aktif: {PROVIDER_CLASSES[cfg.provider].label if cfg else '(belum ada)'}",
            f"Model: {cfg.model if cfg else '-'}",
            f"API key: {mask_key(cfg.api_key) if cfg else '-'}",
            f"Penyimpanan: {'tersimpan di ' + str(self.store.path) if (cfg and cfg.provider in self.stored.providers) else 'tidak tersimpan (hanya sesi ini)'}",
            "Riwayat percakapan: hanya di memori, tidak disimpan ke disk.",
            "",
            "Provider:", self._provider_list(), "",
            "Ganti key/provider: /connect · Hapus key: /settings delete-key · Hapus semua: /settings delete-all",
        ]
        return self._sys("\n".join(lines))

    # ------------------------------------------------------------ wizard
    def _start_wizard(self) -> Outcome:
        self._step, self._data = "provider", {}
        return self._sys("Hubungkan provider AI (ketik 'batal' kapan saja untuk membatalkan).\n\nPilih provider:\n"
                         + self._provider_list() + "\n\nKetik nomor atau id provider.")

    def _wizard_input(self, text: str) -> Outcome:
        step = self._step
        if step != "busy" and text.lower() in CANCEL_WORDS:
            return self.cancel_wizard()
        out = getattr(self, f"_w_{step}")(text)
        # Echo jawaban non-rahasia; API key TIDAK PERNAH di-echo.
        if self.echo_wizard:
            if step == "key":
                out.replies.insert(0, Reply("\u2022" * 8 + " (API key disembunyikan)", "user"))
            elif text:
                out.replies.insert(0, Reply(text, "user"))
        return out

    def _w_busy(self, text: str) -> Outcome:
        return self._sys("Tunggu sebentar, permintaan masih berjalan...")

    def _w_provider(self, text: str) -> Outcome:
        pid = self._resolve_provider(text)
        if pid is None:
            return self._sys("Pilihan tidak valid. Ketik nomor (1-3) atau id provider.", "error")
        self._data["provider"] = pid
        cls = PROVIDER_CLASSES[pid]
        if cls.needs_base_url:
            self._step = "base_url"
            return self._sys(f"{cls.label} dipilih.\nMasukkan base URL API (Enter = {cls.default_base_url}).")
        self._step = "key"
        return self._key_prompt(f"{cls.label} dipilih.\n")

    def _w_base_url(self, text: str) -> Outcome:
        cls = PROVIDER_CLASSES[self._data["provider"]]
        try:
            self._data["base_url"] = validate_base_url(text or cls.default_base_url or "")
        except ValidationError as err:
            return self._sys(f"{err} Coba lagi.", "error")
        self._step = "key"
        return self._key_prompt()

    def _key_prompt(self, prefix: str = "") -> Outcome:
        existing = self._configs().get(self._data["provider"])
        extra = " Enter kosong = tetap pakai key yang sudah ada." if existing else ""
        return self._sys(prefix + "Tempel API key milikmu sendiri. Karakter disembunyikan dan tidak ditampilkan lagi." + extra)

    def _w_key(self, text: str) -> Outcome:
        pid = self._data["provider"]
        existing = self._configs().get(pid)
        try:
            if not text and existing:
                key = existing.api_key
            else:
                key = validate_api_key(text)
        except ValidationError as err:
            return self._sys(f"{err} Coba lagi.", "error")
        self._data["api_key"] = key
        self._step = "models_consent"
        cls = PROVIDER_CLASSES[pid]
        return self._sys(f"API key diterima.\nAmbil daftar model dari {cls.label}? API key-mu dikirim ke provider ini "
                         "hanya untuk meminta daftar model. (y = ambil, n = ketik nama model manual)")

    def _manual_model_prompt(self) -> Outcome:
        pid = self._data["provider"]
        existing = self._configs().get(pid)
        cls = PROVIDER_CLASSES[pid]
        hint = f" Enter = tetap pakai '{existing.model}'." if existing else ""
        self._step = "model"
        return self._sys(f"Masukkan nama model persis seperti di dokumentasi resmi: {cls.docs_url}{hint}")

    def _w_models_consent(self, text: str) -> Outcome:
        answer = text.lower()
        if answer in NO:
            return self._manual_model_prompt()
        if answer not in YES:
            return self._sys("Jawab y atau n.", "error")
        d = self._data
        cfg = ProviderConfig(d["provider"], "-", d["api_key"], d.get("base_url"))
        client = CloudClient(self.transport, get_transport=self.get_transport)
        self._step = "busy"

        def job() -> List[Reply]:
            try:
                models = client.list_models(cfg)
            except ProviderError as err:
                if err.kind == ErrorKind.AUTH:
                    self._reset_wizard()
                    return [Reply(f"{err.message}\nKonfigurasi TIDAK disimpan. Ketik /connect untuk mencoba lagi.", "error")]
                out = self._manual_model_prompt()
                return [Reply(f"Gagal mengambil daftar model: {err.message}\nKetik nama model secara manual.", "error")] + out.replies
            self._data["models"] = models
            self._step = "model_pick"
            return [Reply(f"{len(models)} model ditemukan. Pilih salah satu.", "system")]

        return Outcome(job=job, job_label="Mengambil daftar model...")

    def _w_model_pick(self, text: str) -> Outcome:
        if text == "__manual__":
            return self._manual_model_prompt()
        return self._w_model(text)

    def _w_model(self, text: str) -> Outcome:
        pid = self._data["provider"]
        existing = self._configs().get(pid)
        if not text and existing:
            text = existing.model
        try:
            model = validate_model(text)
        except ValidationError as err:
            self._step = "model"
            return self._sys(f"{err} Coba lagi.", "error")
        self._data["model"] = model
        self._step = "test_consent"
        cls = PROVIDER_CLASSES[pid]
        return self._sys(f"Model: {model}.\nKirim permintaan uji sederhana ke {cls.label}? Isinya hanya satu "
                         "kalimat tes tanpa data percakapan, tetapi dapat memakai kuota API-mu. (y/n)")

    def _pending_config(self) -> ProviderConfig:
        d = self._data
        return ProviderConfig(d["provider"], d["model"], d["api_key"], d.get("base_url"))

    def _w_test_consent(self, text: str) -> Outcome:
        answer = text.lower()
        if answer in NO:
            self._step = "save_consent"
            return self._sys("Tes dilewati. " + self._save_prompt())
        if answer not in YES:
            return self._sys("Jawab y atau n.", "error")
        cfg = self._pending_config()
        client = CloudClient(self.transport, get_transport=self.get_transport)
        self._step = "busy"

        def job() -> List[Reply]:
            try:
                client.test(cfg)
            except ProviderError as err:
                self._reset_wizard()
                return [Reply(f"Tes koneksi gagal: {err.message}\nKonfigurasi TIDAK disimpan. Ketik /connect untuk mencoba lagi.", "error")]
            self._step = "save_consent"
            return [Reply("Koneksi berhasil.", "system"), Reply(self._save_prompt(), "system")]

        return Outcome(job=job, job_label="Menguji koneksi...")

    def _save_prompt(self) -> str:
        return (f"Simpan konfigurasi (termasuk API key) di {self.store.path}? "
                "File dibatasi izin 0600 tetapi tidak dienkripsi. (y = simpan, n = pakai hanya untuk sesi ini)")

    def _w_save_consent(self, text: str) -> Outcome:
        answer = text.lower()
        if answer not in YES and answer not in NO:
            return self._sys("Jawab y atau n.", "error")
        cfg = self._pending_config()
        saved = False
        note = ""
        if answer in YES:
            try:
                self.store.save_provider(cfg, make_active=True)
                self._reload()
                self.session_configs.pop(cfg.provider, None)
                saved = True
            except OSError:
                note = "\nGagal menyimpan ke disk; konfigurasi dipakai hanya untuk sesi ini."
        if not saved:
            self.session_configs[cfg.provider] = cfg
        if self.active_id != cfg.provider:
            self._reset_context()
        self.active_id = cfg.provider
        self._step = "use_now"
        where = "tersimpan" if saved else "hanya untuk sesi ini"
        label = PROVIDER_CLASSES[cfg.provider].label
        self._data["summary"] = f"Terhubung ke {label} (model {cfg.model}). API key {where}, disembunyikan.{note}"
        return self._sys(f"Terhubung ke {label} (model {cfg.model}). API key {where}, disembunyikan.{note}\n\n"
                         "Mau langsung memakai Cloud Mode? Ketik 1 untuk Cloud, 2 untuk tetap di Local.")

    def _w_use_now(self, text: str) -> Outcome:
        t = text.lower()
        summary = self._data.get("summary", "")
        pre = (summary + "\n") if summary else ""
        if t in ("1", "cloud", "c"):
            self._reset_wizard()
            self.mode = "cloud"
            return self._sys(pre + "Cloud Mode aktif. Pesanmu sekarang dikirim ke provider yang kamu pilih. Ketik /mode local untuk kembali.")
        if t in ("2", "local", "l", ""):
            self._reset_wizard()
            self.mode = "local"
            return self._sys(pre + "Tetap di Local Mode. Ketik /mode cloud kapan saja untuk beralih.")
        return self._sys("Ketik 1 (Cloud) atau 2 (Local).", "error")

    def _w_confirm(self, text: str) -> Outcome:
        data = self._data
        self._reset_wizard()
        if text.lower() not in YES:
            return self._sys("Dibatalkan. Tidak ada yang dihapus.")
        try:
            if data["action"] == "delete-all":
                self.store.delete_all()
                self.session_configs.clear()
                self.active_id = None
                msg = "Semua konfigurasi dan API key dihapus."
            else:
                pid = data["provider"]
                if pid in self.stored.providers:
                    self.store.remove_provider(pid)
                self.session_configs.pop(pid, None)
                if self.active_id == pid:
                    self.active_id = None
                msg = f"API key {PROVIDER_CLASSES[pid].label} dihapus."
        except OSError:
            return self._sys("Gagal menghapus konfigurasi dari disk.", "error")
        self._reload()
        self._reset_context()
        if self.active_config is None:
            self.mode = "local"
            msg += " Kembali ke Local Mode."
        return self._sys(msg)


def one_shot(question: str, mode: str, store: Optional[ConfigStore] = None, transport=None) -> Tuple[str, bool]:
    """Jawab satu pertanyaan (untuk `linuxai "pertanyaan"`). Mengembalikan (teks, berhasil)."""
    if mode == "local":
        return LocalAssistant().answer(question).text, True
    stored = (store or ConfigStore()).load()
    cfg = stored.providers.get(stored.active_provider) if stored.active_provider else None
    if cfg is None:
        return ("Cloud Mode belum dikonfigurasi. Jalankan `linuxai`, lalu ketik /connect.", False)
    try:
        return CloudClient(transport).send(cfg, [ChatMessage("user", question)]), True
    except ProviderError as err:
        return err.message, False
