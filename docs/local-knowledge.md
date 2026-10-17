# Basis pengetahuan Local Mode

Local Mode **bukan AI**. Ia mencocokkan pertanyaan dengan entri yang sudah ditulis manusia. Semuanya data Python biasa di folder `linuxai/local/`.

## Isi (±220 topik)
| File | Isi |
|---|---|
| `knowledge.py` | Entri awal (perintah dasar, topik migrasi Windows → Linux) dan penggabung semua modul |
| `kb_concepts.py` | Konsep dan istilah: Linux, kernel, distro (Ubuntu, Mint, Arch, Fedora…), Wayland vs X11, tiling WM/Hyprland, GRUB/UEFI, swap, filesystem, mount, pipe, cron, dll. |
| `kb_commands.py` | Perintah tambahan: `sort`, `awk`, `sed`, `rsync`, `ss`, `nmcli`, `vim`, `git`, `docker`, `python/pip`, `npm`, `ufw`, `ssh-keygen`, dll. |
| `kb_howto.py` | Panduan: memasang aplikasi, font, VPN, tema, monitor ganda, baterai, hotspot, Samba, format flashdisk, recovery file, dll. |
| `kb_trouble.py` | Pesan error dan solusi: `Unable to locate package`, GPG/NO_PUBKEY, `bad interpreter ^M`, `Read-only file system`, layar hitam, kernel panic, SSH, dll. |
| `entry.py` | Bentuk satu entri (`Entry`) dan pembuat ringkas `T(...)` |
| `assistant.py` | Pencocok pertanyaan |

## Cara pencocokan
1. **Normalisasi**: huruf kecil, sinonim dan bahasa gaul dibakukan (`copy/salin/nyalin` → satu bentuk, `nginstall` → `install`), kata penghubung dibuang (`apa`, `itu`, `gimana`, `dong`, …).
2. **Koreksi typo**: salah ketik satu huruf dan ejaan umum dikoreksi terhadap kosakata basis pengetahuan (`hyperland` → `hyprland`).
3. **Skor**: frasa persis lebih tinggi daripada kumpulan kata kunci tanpa urutan. Entri terbaik menang.
4. **Tidak cocok**: LinuxAI jujur mengatakan belum tahu, menawarkan 'topik terdekat' bila ada, dan menyarankan Cloud Mode.

Entri berflag `cmd=True` (perintah satu kata yang ambigu) dan `short=True` (definisi) tidak mencuri pertanyaan panjang yang tidak berhubungan.

## Menambah topik
Tambahkan satu `T(...)` pada daftar di modul yang sesuai:

```python
T("nama-id-unik", "Judul topik",
  "kata kunci 1|kata kunci 2|apa itu x|cara pakai x",   # pisahkan dengan |
  """Jawaban. Perintah ditulis di blok kode:
```
sudo apt install x
```
""")
```

Pedoman:
- Beri **banyak variasi kunci** (formal, gaul, singkat). Tidak perlu semua kombinasi; sinonim dan urutan kata sudah dibantu pencocok.
- Jangan memakai kunci yang sama dengan entri lain; tes akan menandai bentrok.
- Untuk perintah berbahaya (`dd`, `rm -rf`, partisi), tulis peringatan jelas.
- Jangan mengklaim sesuatu yang bergantung distro tanpa menyebut distronya.

## Menguji
```bash
python -m unittest tests.test_local_mode -v
```
Tes memeriksa: id unik, tidak ada kunci yang bentrok, pertanyaan umum menuju entri yang benar, typo/gaul, pertanyaan di luar topik tetap 'tidak tahu', blok kode seimbang, dan perintah berbahaya memuat peringatan.

## Batas
Basis pengetahuan tidak bisa menalar atau menjawab hal baru. Untuk itu gunakan Cloud Mode (`/connect`), termasuk model lokal lewat Ollama (provider kompatibel OpenAI).
