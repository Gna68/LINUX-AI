import shutil
import tempfile
import unittest
from pathlib import Path

from linuxai.config.store import ConfigStore
from linuxai.core.controller import Controller
from linuxai.utils.http import HttpResult

KEY = "TESTKEY-1234567890-ABCDEF"


def gemini_ok(text="jawaban mock"):
    return HttpResult(200, {"candidates": [{"content": {"parts": [{"text": text}]}}]})


def openai_ok(text="jawaban mock"):
    return HttpResult(200, {"choices": [{"message": {"role": "assistant", "content": text}}]})


class MockTransport:
    """Transport palsu: mencatat panggilan, tanpa jaringan dan tanpa kuota API."""

    def __init__(self, result=None, exc=None):
        self.calls = []
        self.result = result if result is not None else gemini_ok()
        self.exc = exc

    def __call__(self, url, headers, payload, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "payload": payload, "timeout": timeout})
        if self.exc:
            raise self.exc
        return self.result(url, headers, payload) if callable(self.result) else self.result


class MockGetTransport:
    """GET palsu untuk daftar model: mencatat panggilan, tanpa jaringan."""

    def __init__(self, result=None, exc=None):
        self.calls = []
        self.result = result if result is not None else gemini_models_ok(["model-a", "model-b"])
        self.exc = exc

    def __call__(self, url, headers, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if self.exc:
            raise self.exc
        return self.result


def gemini_models_ok(names):
    return HttpResult(200, {"models": [{"name": f"models/{n}", "supportedGenerationMethods": ["generateContent"]} for n in names]})


def openai_models_ok(ids):
    return HttpResult(200, {"data": [{"id": i} for i in ids]})


class TmpConfigCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="linuxai-test-")
        self.store = ConfigStore(Path(self._tmp) / "linuxai")
        self.transport = MockTransport()
        self.get_transport = MockGetTransport()

    def tearDown(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def controller(self, **kw):
        return Controller(store=self.store, transport=self.transport, get_transport=self.get_transport, **kw)


def run(controller, text):
    """Kirim input; jalankan job cloud (jika ada) secara sinkron. Mengembalikan daftar Reply."""
    out = controller.handle(text)
    replies = list(out.replies)
    if out.job:
        replies += out.job()
    return replies


def connect(controller, provider="1", model="model-x", key=KEY, test="n", save="n", use="1", base_url="", models="n"):
    """Wizard /connect penuh. Urutan: provider, [base_url], key, daftar model?, model, tes?, simpan?, pakai?"""
    steps = ["/connect", provider]
    if provider in ("3", "openai-compatible"):
        steps.append(base_url)
    steps += [key, models, model, test, save, use]
    allr = []
    for s in steps:
        if s == "/connect" or controller.in_wizard:
            allr += run(controller, s)
    return allr
