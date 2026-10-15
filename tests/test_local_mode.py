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
