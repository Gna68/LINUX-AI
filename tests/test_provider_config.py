import unittest

from linuxai.config.validation import ValidationError, validate_api_key, validate_base_url, validate_model
from tests.helpers import KEY, MockTransport, TmpConfigCase, connect, gemini_ok, run
from linuxai.utils.http import HttpResult


class ValidationTests(unittest.TestCase):
    def test_model(self):
        self.assertEqual(validate_model(" a/b-c.d:1 "), "a/b-c.d:1")
        for bad in ("", "has space", "../x", "x;rm", "x" * 300, "-lead"):
            with self.assertRaises(ValidationError):
                validate_model(bad)

    def test_key(self):
        self.assertEqual(validate_api_key(" " + KEY + " "), KEY)
        for bad in ("", "short", "has space in it 123", "kunci\u00e9" * 3, "x" * 600):
            with self.assertRaises(ValidationError) as ctx:
                validate_api_key(bad)
            if len(bad.strip()) > 3:
                self.assertNotIn(bad.strip(), str(ctx.exception))

    def test_base_url(self):
        self.assertEqual(validate_base_url("https://api.example.com/v1/"), "https://api.example.com/v1")
        self.assertEqual(validate_base_url("http://localhost:8080/v1"), "http://localhost:8080/v1")
        for bad in ("http://example.com/v1", "ftp://x", "https://u:p@x.com", "https://x.com/v1?k=1", "nothing", ""):
            with self.assertRaises(ValidationError):
                validate_base_url(bad)


class StoreTests(TmpConfigCase):
    def test_add_change_delete_provider(self):
        from linuxai.config.models import ProviderConfig
        self.store.save_provider(ProviderConfig("gemini", "m1", KEY))
        self.store.save_provider(ProviderConfig("openrouter", "m2", KEY + "2"), make_active=False)
        loaded = self.store.load()
        self.assertEqual(set(loaded.providers), {"gemini", "openrouter"})
        self.assertEqual(loaded.active_provider, "gemini")
        self.store.set_active("openrouter")
        self.store.update_model("openrouter", "m3")
        loaded = self.store.load()
        self.assertEqual((loaded.active_provider, loaded.providers["openrouter"].model), ("openrouter", "m3"))
        self.store.remove_provider("openrouter")
        loaded = self.store.load()
        self.assertEqual(set(loaded.providers), {"gemini"})
        self.assertEqual(loaded.active_provider, None)
        self.store.delete_all()
        self.assertFalse(self.store.exists())

    def test_corrupt_file_does_not_crash(self):
        self.store.directory.mkdir(parents=True)
        self.store.path.write_text("{ bukan json")
        self.assertEqual(self.store.load().providers, {})
        self.store.path.write_text('{"providers": {"x": 5, "gemini": {"model": 1}}}')
        self.assertEqual(self.store.load().providers, {})


class WizardTests(TmpConfigCase):
    def test_full_flow_saves_and_activates(self):
        c = self.controller()
        connect(c, provider="2", model="vendor/model", save="y", use="1")
        self.assertEqual(c.mode, "cloud")
        self.assertEqual(c.active_id, "openrouter")
        self.assertEqual(self.store.load().providers["openrouter"].model, "vendor/model")

    def test_connection_test_runs_only_after_consent(self):
        c = self.controller()
        run(c, "/connect"); run(c, "1"); run(c, KEY); run(c, "n"); run(c, "m")
        self.assertEqual(self.transport.calls, [])  # belum ada persetujuan
        run(c, "y")  # setuju tes
        self.assertEqual(len(self.transport.calls), 1)
        self.assertEqual(len(str(self.transport.calls[0]["payload"])) < 600, True)

    def test_declining_test_sends_nothing(self):
        connect(self.controller(), test="n", save="y")
        self.assertEqual(self.transport.calls, [])

    def test_failed_test_saves_nothing_and_stays_local(self):
        self.transport.result = HttpResult(401, {})
        c = self.controller()
        replies = connect(c, test="y", save="y")
        self.assertTrue(any("Autentikasi" in r.text for r in replies))
        self.assertFalse(self.store.exists())
        self.assertIsNone(c.active_config)
        self.assertFalse(c.in_wizard)
        self.assertEqual(c.mode, "local")

    def test_successful_test_then_save(self):
        c = self.controller()
        connect(c, test="y", save="y", use="2")
        self.assertTrue(self.store.exists())
        self.assertEqual(c.mode, "local")  # memilih tetap Local

    def test_decline_save_is_session_only(self):
        c = self.controller()
        connect(c, save="n", use="1")
        self.assertFalse(self.store.exists())
        self.assertIsNotNone(c.active_config)
        self.assertEqual(c.mode, "cloud")

    def test_cancel_leaves_existing_config_untouched(self):
        c = self.controller()
        connect(c, save="y", use="2")
        before = self.store.path.read_text()
        run(c, "/connect"); run(c, "2"); run(c, KEY + "Z"); run(c, "n")
        replies = run(c, "batal")
        self.assertIn("Dibatalkan", replies[-1].text)
        self.assertEqual(self.store.path.read_text(), before)
        self.assertEqual(c.active_id, "gemini")
        self.assertFalse(c.in_wizard)

    def test_invalid_inputs_reprompt_without_advancing(self):
        c = self.controller()
        run(c, "/connect")
        self.assertEqual(run(c, "99")[-1].kind, "error")
        run(c, "1")
        self.assertTrue(c.secret_input)
        self.assertEqual(run(c, "short")[-1].kind, "error")
        self.assertTrue(c.secret_input)
        run(c, KEY); run(c, "n")
        self.assertEqual(run(c, "bad model!")[-1].kind, "error")
        self.assertEqual(c.dialog_spec().kind, "input")  # tetap di langkah model

    def test_openai_compatible_asks_base_url_and_rejects_plain_http(self):
        c = self.controller()
        run(c, "/connect"); run(c, "3")
        self.assertEqual(run(c, "http://example.com/v1")[-1].kind, "error")
        run(c, "")  # Enter = default
        self.assertTrue(c.secret_input)

    def test_provider_and_model_switching(self):
        c = self.controller()
        connect(c, provider="1", model="g1", save="y", use="2")
        connect(c, provider="2", model="o1", key=KEY + "B", save="y", use="2")
        self.assertEqual(c.active_id, "openrouter")
        run(c, "/provider 1")
        self.assertEqual(self.store.load().active_provider, "gemini")
        run(c, "/model g2")
        self.assertEqual(self.store.load().providers["gemini"].model, "g2")
        self.assertEqual(c.active_config.model, "g2")
        self.assertEqual(run(c, "/model bad model!")[-1].kind, "error")
        self.assertEqual(run(c, "/provider 3")[-1].kind, "error")  # belum dikonfigurasi

    def test_delete_key_and_delete_all(self):
        c = self.controller()
        connect(c, save="y", use="1")
        run(c, "/settings delete-key")
        self.assertTrue(c.in_wizard)
        run(c, "tidak")
        self.assertIn("gemini", self.store.load().providers)  # dibatalkan
        run(c, "/settings delete-key"); run(c, "ya")
        self.assertEqual(self.store.load().providers, {})
        self.assertEqual((c.mode, c.active_config), ("local", None))
        connect(c, save="y", use="1")
        run(c, "/settings delete-all"); run(c, "ya")
        self.assertFalse(self.store.exists())
        self.assertEqual(c.mode, "local")


class ModelListTests(TmpConfigCase):
    def start(self, provider="1", base_url=""):
        c = self.controller()
        run(c, "/connect"); run(c, provider)
        if provider == "3":
            run(c, base_url)
        run(c, KEY)
        return c

    def test_no_model_request_before_consent(self):
        c = self.start()
        self.assertEqual(self.get_transport.calls, [])
        run(c, "n")
        self.assertEqual(self.get_transport.calls, [])
        self.assertEqual(c.dialog_spec().kind, "input")  # ketik manual

    def test_fetch_then_pick_model(self):
        c = self.start()
        run(c, "y")
        self.assertEqual(len(self.get_transport.calls), 1)
        spec = c.dialog_spec()
        self.assertTrue(spec.searchable)
        self.assertEqual([v for _, v in spec.options], ["__manual__", "model-a", "model-b"])
        run(c, "model-b")
        self.assertEqual(c._data["model"], "model-b")
        self.assertEqual([v for _, v in c.dialog_spec().options], ["y", "n"])  # lanjut ke tes

    def test_pick_manual_entry_falls_back_to_typing(self):
        c = self.start()
        run(c, "y"); run(c, "__manual__")
        self.assertEqual(c.dialog_spec().kind, "input")

    def test_failed_fetch_falls_back_to_manual_input(self):
        self.get_transport.result = HttpResult(500, {})
        c = self.start()
        replies = run(c, "y")
        self.assertTrue(any("Gagal mengambil daftar model" in r.text for r in replies))
        self.assertEqual(c.dialog_spec().kind, "input")
        self.assertTrue(c.in_wizard)

    def test_auth_failure_on_fetch_aborts_without_saving(self):
        self.get_transport.result = HttpResult(401, {})
        c = self.start()
        replies = run(c, "y")
        self.assertTrue(any("Autentikasi" in r.text for r in replies))
        self.assertFalse(c.in_wizard)
        self.assertFalse(self.store.exists())
        self.assertIsNone(c.active_config)

    def test_key_only_goes_to_selected_provider(self):
        c = self.start(provider="2")
        run(c, "y")
        call = self.get_transport.calls[0]
        self.assertEqual(call["url"], "https://openrouter.ai/api/v1/models")
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {KEY}")
        self.assertNotIn(KEY, call["url"])

    def test_empty_list_falls_back(self):
        self.get_transport.result = HttpResult(200, {"data": []})
        c = self.start(provider="2")
        run(c, "y")
        self.assertEqual(c.dialog_spec().kind, "input")

    def test_provider_model_parsing(self):
        from linuxai.providers import get_provider
        from linuxai.config.models import ProviderConfig
        from tests.helpers import MockGetTransport, gemini_models_ok, openai_models_ok
        g = HttpResult(200, {"models": [
            {"name": "models/chat-1", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/embed-1", "supportedGenerationMethods": ["embedContent"]},
            {"name": "models/bad name!", "supportedGenerationMethods": ["generateContent"]}]})
        t = MockGetTransport(g)
        out = get_provider("gemini", get_transport=t).list_models(ProviderConfig("gemini", "-", KEY))
        self.assertEqual(out, ["chat-1"])  # embed disaring, nama tidak valid dibuang
        self.assertTrue(t.calls[0]["url"].startswith("https://generativelanguage.googleapis.com/v1beta/models"))
        self.assertEqual(t.calls[0]["headers"]["x-goog-api-key"], KEY)
        t = MockGetTransport(openai_models_ok(["b", "a", "a"]))
        out = get_provider("openai-compatible", get_transport=t).list_models(
            ProviderConfig("openai-compatible", "-", KEY, "http://localhost:8080/v1"))
        self.assertEqual(out, ["a", "b"])
        self.assertEqual(t.calls[0]["url"], "http://localhost:8080/v1/models")
