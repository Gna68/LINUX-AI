import unittest

from linuxai.cloud.base import ChatMessage, ErrorKind, ProviderError
from linuxai.config.models import ProviderConfig
from linuxai.providers import get_provider
from linuxai.utils.http import HttpConnectionError, HttpResult, HttpTimeout
from tests.helpers import KEY, MockTransport, TmpConfigCase, connect, gemini_ok, openai_ok, run

MSGS = [ChatMessage("user", "halo")]


def cfg(provider, base_url=None):
    return ProviderConfig(provider, "model-x", KEY, base_url)


class ProviderRequestTests(unittest.TestCase):
    def test_gemini_request_and_response(self):
        t = MockTransport(gemini_ok("hai dari gemini"))
        text = get_provider("gemini", t).chat(cfg("gemini"), MSGS, "SYS")
        self.assertEqual(text, "hai dari gemini")
        call = t.calls[0]
        self.assertTrue(call["url"].endswith("/models/model-x:generateContent"))
        self.assertEqual(call["headers"]["x-goog-api-key"], KEY)
        self.assertNotIn(KEY, call["url"])
        self.assertEqual(call["payload"]["system_instruction"]["parts"][0]["text"], "SYS")
        self.assertEqual(call["payload"]["contents"][0]["role"], "user")

    def test_openrouter_url_is_locked(self):
        t = MockTransport(openai_ok("hai"))
        get_provider("openrouter", t).chat(cfg("openrouter", "https://evil.example/v1"), MSGS, "SYS")
        call = t.calls[0]
        self.assertEqual(call["url"], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {KEY}")

    def test_openai_compatible_uses_base_url(self):
        t = MockTransport(openai_ok("hai"))
        get_provider("openai-compatible", t).chat(cfg("openai-compatible", "http://localhost:8080/v1"), MSGS, "SYS")
        self.assertEqual(t.calls[0]["url"], "http://localhost:8080/v1/chat/completions")
        self.assertEqual(t.calls[0]["payload"]["messages"][0], {"role": "system", "content": "SYS"})

    def test_timeout_is_passed(self):
        t = MockTransport(openai_ok())
        get_provider("openrouter", t, timeout=7).chat(cfg("openrouter"), MSGS, "S")
        self.assertEqual(t.calls[0]["timeout"], 7)


class ProviderErrorTests(unittest.TestCase):
    STATUS = [(401, ErrorKind.AUTH), (403, ErrorKind.AUTH), (404, ErrorKind.MODEL_NOT_FOUND),
              (429, ErrorKind.RATE_LIMIT), (500, ErrorKind.SERVER), (503, ErrorKind.SERVER),
              (418, ErrorKind.BAD_REQUEST), (302, ErrorKind.BAD_RESPONSE)]

    def test_http_status_mapping_for_every_provider(self):
        body = {"error": {"message": f"secret detail {KEY}"}}
        for pid in ("gemini", "openrouter", "openai-compatible"):
            for status, kind in self.STATUS:
                with self.subTest(provider=pid, status=status):
                    t = MockTransport(HttpResult(status, body))
                    with self.assertRaises(ProviderError) as ctx:
                        get_provider(pid, t).chat(cfg(pid), MSGS, "S")
                    self.assertEqual(ctx.exception.kind, kind)
                    self.assertNotIn(KEY, ctx.exception.message)
                    self.assertNotIn("secret detail", ctx.exception.message)

    def test_gemini_invalid_key_400_is_auth(self):
        t = MockTransport(HttpResult(400, {"error": {"message": "API key not valid. Please pass a valid API key."}}))
        with self.assertRaises(ProviderError) as ctx:
            get_provider("gemini", t).chat(cfg("gemini"), MSGS, "S")
        self.assertEqual(ctx.exception.kind, ErrorKind.AUTH)

    def test_network_failures(self):
        for exc, kind in ((HttpTimeout(), ErrorKind.TIMEOUT), (HttpConnectionError(), ErrorKind.NETWORK)):
            with self.assertRaises(ProviderError) as ctx:
                get_provider("openrouter", MockTransport(exc=exc)).chat(cfg("openrouter"), MSGS, "S")
            self.assertEqual(ctx.exception.kind, kind)

    def test_garbage_responses_do_not_crash(self):
        garbage = [HttpResult(200, None), HttpResult(200, {}), HttpResult(200, {"choices": []}),
                   HttpResult(200, {"candidates": []}), HttpResult(200, {"choices": [{"message": {"content": ""}}]}),
                   HttpResult(200, {"candidates": [{"content": {"parts": "x"}}]}),
                   HttpResult(200, {"promptFeedback": {"blockReason": "SAFETY"}})]
        for pid in ("gemini", "openrouter"):
            for res in garbage:
                with self.subTest(provider=pid, res=res):
                    with self.assertRaises(ProviderError):
                        get_provider(pid, MockTransport(res)).chat(cfg(pid), MSGS, "S")

    def test_invalid_config_rejected_before_any_request(self):
        t = MockTransport()
        with self.assertRaises(ProviderError) as ctx:
            get_provider("gemini", t).chat(ProviderConfig("gemini", "bad model!", KEY), MSGS, "S")
        self.assertEqual(ctx.exception.kind, ErrorKind.CONFIG)
        self.assertEqual(t.calls, [])


class CloudSessionTests(TmpConfigCase):
    def cloud_controller(self, transport=None):
        if transport is not None:
            self.transport = transport
        c = self.controller()
        connect(c, save="y", use="1")
        self.transport.calls.clear()
        return c

    def test_cloud_chat_keeps_context(self):
        c = self.cloud_controller()
        self.assertEqual(c.mode, "cloud")
        run(c, "pertanyaan satu")
        replies = run(c, "pertanyaan dua")
        self.assertEqual(replies[-1].text, "jawaban mock")
        contents = self.transport.calls[1]["payload"]["contents"]
        self.assertEqual([x["role"] for x in contents], ["user", "model", "user"])

    def test_job_is_deferred_so_ui_does_not_block(self):
        c = self.cloud_controller()
        out = c.handle("halo")
        self.assertIsNotNone(out.job)
        self.assertEqual(self.transport.calls, [])
        out.job()
        self.assertEqual(len(self.transport.calls), 1)

    def test_failure_returns_error_reply_and_keeps_history_clean(self):
        c = self.cloud_controller(MockTransport(HttpResult(429, {})))
        replies = run(c, "halo")
        self.assertEqual(replies[-1].kind, "error")
        self.assertEqual(c.cloud_history, [])
        self.transport.result = gemini_ok("ok")
        run(c, "coba lagi")
        self.assertEqual(len(c.cloud_history), 2)

    def test_failed_message_is_not_lost_and_goes_with_next_one(self):
        c = self.cloud_controller(MockTransport(HttpResult(500, {})))
        replies = run(c, "bisa membuat gambar?")
        self.assertIn("tidak hilang", replies[-1].text)
        self.transport.result = gemini_ok("ok")
        run(c, "bagaimana?")
        sent = self.transport.calls[-1]["payload"]["contents"]
        self.assertEqual(len(sent), 1)  # satu giliran user (digabung) agar peran tetap bergantian
        text = sent[0]["parts"][0]["text"]
        self.assertIn("bisa membuat gambar?", text)
        self.assertIn("bagaimana?", text)
        self.assertEqual(c.cloud_history[0].content, text)
        run(c, "lanjut")  # sudah terkirim sukses: tidak dikirim ulang
        self.assertNotIn("bisa membuat gambar?", str(self.transport.calls[-1]["payload"]["contents"][-1]))

    def test_retrying_same_text_is_not_duplicated(self):
        c = self.cloud_controller(MockTransport(HttpResult(500, {})))
        run(c, "pertanyaan saya")
        self.transport.result = gemini_ok("ok")
        run(c, "pertanyaan saya")
        self.assertEqual(self.transport.calls[-1]["payload"]["contents"][0]["parts"][0]["text"], "pertanyaan saya")

    def test_pending_message_dropped_on_clear_and_local_switch(self):
        for action in ("/clear", "/mode local"):
            c = self.cloud_controller(MockTransport(HttpResult(500, {})))
            run(c, "pesan rahasia gagal")
            run(c, action)
            run(c, "/mode cloud")
            self.transport.result = gemini_ok("ok")
            run(c, "pesan baru")
            self.assertNotIn("rahasia", str(self.transport.calls[-1]["payload"]))

    def test_local_mode_never_sends_conversation_to_provider(self):
        c = self.cloud_controller()
        run(c, "/mode local")
        run(c, "apa itu sudo")
        run(c, "/help")
        self.assertEqual(self.transport.calls, [])

    def test_local_messages_are_not_leaked_when_returning_to_cloud(self):
        c = self.cloud_controller()
        run(c, "/mode local")
        run(c, "rahasia lokal 123")
        run(c, "/mode cloud")
        run(c, "pertanyaan cloud")
        sent = str(self.transport.calls[0]["payload"])
        self.assertNotIn("rahasia lokal", sent)

    def test_slash_commands_are_never_sent_to_model(self):
        c = self.cloud_controller()
        for cmd in ("/help", "/settings", "/provider", "/model", "/clear", "/mode cloud", "/unknown"):
            run(c, cmd)
        self.assertEqual(self.transport.calls, [])

    def test_switching_modes_keeps_saved_config(self):
        c = self.cloud_controller()
        run(c, "/mode local")
        run(c, "/mode cloud")
        self.assertEqual(c.mode, "cloud")
        self.assertIn("gemini", self.store.load().providers)
        self.assertEqual(c.active_config.api_key, self.store.load().providers["gemini"].api_key)

    def test_cloud_mode_without_config_is_refused(self):
        c = self.controller()
        replies = run(c, "/mode cloud")
        self.assertEqual(replies[-1].kind, "error")
        self.assertEqual(c.mode, "local")
