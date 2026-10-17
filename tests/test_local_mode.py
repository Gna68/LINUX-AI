import socket
import unittest
from unittest import mock

from linuxai.local.assistant import LocalAssistant
from linuxai.local.knowledge import ENTRIES
from tests.helpers import TmpConfigCase, run


class LocalModeTests(unittest.TestCase):
    def setUp(self):
        self.a = LocalAssistant()

    def test_known_questions_map_to_expected_entries(self):
        cases = {
            "apa itu sudo": "sudo",
            "halo": "greeting",
            "apa fungsi perintah grep?": "cmd-grep",
            "wifi tidak muncul di laptop saya": "wifi",
            "Permission denied": "permission-denied",
            "apa beda Windows dan Linux": "win-vs-linux",
            "cara install aplikasi di linux": "install-app",
            "rm -rf /": "rm-rf",
            "bagaimana cara menjalankan file exe": "wine",
            "sudo apt update": "update-system",
            "bash: foo: command not found": "command-not-found",
            "Could not get lock /var/lib/dpkg/lock-frontend": "dpkg-lock",
            "error externally-managed-environment saat pip install": "pip-externally-managed",
            "flashdisk ntfs hibernated read-only": "ntfs",
            "pengganti photoshop di linux": "equivalents",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(self.a.answer(question).entry_id, expected)

    def test_unknown_question_is_honest(self):
        ans = self.a.answer("kapan indonesia merdeka")
        self.assertFalse(ans.matched)
        self.assertIn("belum punya jawaban", ans.text)
        self.assertIn("/connect", ans.text)
        self.assertIn("bukan AI generatif", ans.text)

    def test_no_false_positive_on_ambiguous_command_words(self):
        q = "my cat is cute and I like to find things on the top of the hill when I walk"
        self.assertFalse(self.a.answer(q).matched)

    def test_blank_and_huge_input_do_not_crash(self):
        self.assertFalse(self.a.answer("").matched)
        self.assertFalse(self.a.answer("   ").matched)
        self.a.answer("sudo " * 50000)

    def test_every_entry_is_reachable_and_nonempty(self):
        for entry in ENTRIES:
            with self.subTest(entry=entry.id):
                self.assertTrue(entry.answer.strip())
                self.assertIsNotNone(self.a.find(entry.keys[0]))

    def test_answers_never_claim_to_execute(self):
        for entry in ENTRIES:
            lowered = entry.answer.lower()
            self.assertNotIn("saya telah menjalankan", lowered)
            self.assertNotIn("sudah kujalankan", lowered)


class KnowledgeBaseTests(unittest.TestCase):
    """Cakupan luas, pencocokan tahan variasi bahasa, dan kualitas data basis pengetahuan."""

    @classmethod
    def setUpClass(cls):
        cls.a = LocalAssistant()

    def test_entry_ids_are_unique_and_base_is_broad(self):
        ids = [e.id for e in ENTRIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 200)

    def test_every_key_resolves_to_its_own_entry(self):
        """Tidak ada kunci yang 'dicuri' entri lain (bentrok kata kunci)."""
        conflicts = []
        for e in ENTRIES:
            for key in e.keys:
                got = self.a.find(key)
                if got is None or got.id != e.id:
                    conflicts.append((e.id, key, got.id if got else None))
        self.assertEqual(conflicts, [])

    def test_basic_questions_that_used_to_fail(self):
        cases = {
            "apa itu linux": "what-is-linux",
            "linux itu apa": "what-is-linux",
            "pengertian linux": "what-is-linux",
            "apa itu kernel": "kernel",
            "apa itu distro": "distro-def",
            "apa itu npm": "cmd-node/npm",
            "install nodejs": "cmd-node/npm",
            "hyprland itu apa": "de-vs-wm",
            "apa itu wayland": "wayland-x11",
            "caranya copy paste file gimana": "cmd-cp",
            "cara hapus file": "cmd-rm",
            "bikin folder baru": "cmd-mkdir",
            "cara keluar dari vim": "cmd-vim",
            "apa itu git": "cmd-git",
            "linux gratis ga": "open-source",
            "aku mau install vscode": "app-vscode",
            "gimana cara ganti wallpaper": "appearance",
            "unable to locate package htop": "apt-unable-locate",
            "bash: ./x.sh: bad interpreter: /bin/bash^M": "bad-interpreter",
            "komputer saya panas kipas berisik": "fan-heat",
            "cara nambahin user ke grup docker": "cmd-useradd/usermod",
            "apa itu repository": "repo-def",
            "gak bisa konek wifi": "wifi",
            "layar hitam setelah login": "black-screen",
            "externally-managed-environment": "pip-externally-managed",
        }
        for q, expected in cases.items():
            with self.subTest(q=q):
                self.assertEqual(self.a.answer(q).entry_id, expected)

    def test_word_order_and_filler_words_do_not_matter(self):
        for q in ("copy paste file caranya gimana", "tolong dong salin file gimana ya", "file mau di copy gimana"):
            with self.subTest(q=q):
                self.assertEqual(self.a.answer(q).entry_id, "cmd-cp")

    def test_slang_and_informal_spelling(self):
        for q, exp in (("gimana cara nginstall chrome", "app-browser"), ("nyalin file gimana", "cmd-cp"),
                       ("ngapus folder gimana", "cmd-rm"), ("gabisa konek wifi", "wifi")):
            with self.subTest(q=q):
                self.assertEqual(self.a.answer(q).entry_id, exp)

    def test_typos_are_corrected(self):
        for q, exp in (("hyperland", "de-vs-wm"), ("apa itu wayand", "wayland-x11"), ("linuks", "what-is-linux"),
                       ("instal virtuall box", "virtualization")):
            with self.subTest(q=q):
                self.assertEqual(self.a.answer(q).entry_id, exp)

    def test_off_topic_is_still_unknown(self):
        for q in ("kamu tau dota 2 ga", "resep nasi goreng enak", "siapa presiden indonesia", "qwertyuiop asdfgh"):
            with self.subTest(q=q):
                ans = self.a.answer(q)
                self.assertFalse(ans.matched)
                self.assertIn("bukan AI generatif", ans.text)
                self.assertIn("/connect", ans.text)

    def test_unknown_offers_related_topics(self):
        ans = self.a.answer("cara mengatur bluetooth headset kualitas jelek di ruangan")
        text = ans.text
        self.assertIn("belum punya jawaban", text) if not ans.matched else None
        sugg = self.a.suggest("masalah suara headset rusak")
        self.assertTrue(sugg)
        self.assertTrue(all(hasattr(s, "title") for s in sugg))

    def test_definition_entries_do_not_hijack_long_questions(self):
        ans = self.a.answer("bagaimana cara mengganti wallpaper linux saya yang sekarang jadi gambar pemandangan")
        self.assertNotEqual(ans.entry_id, "what-is-linux")

    def test_code_blocks_are_balanced_in_all_answers(self):
        for e in ENTRIES:
            with self.subTest(entry=e.id):
                self.assertEqual(e.answer.count("```") % 2, 0)

    def test_dangerous_commands_carry_warnings(self):
        for entry_id in ("cmd-dd", "rm-rf", "cmd-rm", "gparted"):
            ans = next(e for e in ENTRIES if e.id == entry_id).answer.lower()
            self.assertTrue(any(w in ans for w in ("berbahaya", "hati-hati", "permanen", "risiko", "backup")), entry_id)


class LocalModeOfflineTests(TmpConfigCase):
    def test_works_with_all_network_access_blocked(self):
        def boom(*a, **k):
            raise AssertionError("Local Mode tidak boleh memakai jaringan")

        with mock.patch.object(socket.socket, "connect", boom), \
             mock.patch("socket.getaddrinfo", boom), \
             mock.patch("socket.create_connection", boom):
            c = self.controller()
            self.assertEqual(c.mode, "local")
            replies = run(c, "apa itu sudo")
        self.assertEqual(replies[-1].kind, "assistant")
        self.assertIn("sudo", replies[-1].text)
        self.assertEqual(self.transport.calls, [])

    def test_starts_without_any_config_or_key(self):
        c = self.controller()
        self.assertIsNone(c.active_config)
        self.assertFalse(self.store.exists())
        self.assertEqual(c.status_line().split()[0], "LOCAL")

