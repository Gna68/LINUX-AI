# Troubleshooting

**`linuxai: command not found`** — pipx: jalankan `pipx ensurepath` lalu buka terminal baru. venv: `source .venv/bin/activate`.

**"Antarmuka layar penuh membutuhkan paket 'textual'"** — pasang ulang: `pipx install --force .` atau `pip install textual`.

**`error: externally-managed-environment` saat `pip install`** — jangan pakai `--break-system-packages`. Gunakan pipx atau venv (lihat installation.md).

**`python3 -m venv` gagal** — `sudo apt install python3-venv`.

**Tampilan berantakan / warna aneh** — gunakan terminal modern (GNOME Terminal, Xfce Terminal, Konsole), perbesar jendela,
tekan Ctrl+T untuk mengganti tema gelap/terang. Pastikan locale UTF-8 (`echo $LANG`).

**Tidak bisa menyalin teks** — TUI menangkap mouse. Tahan Shift sambil menyeret mouse lalu Ctrl+Shift+C, atau ketik `/copy` untuk menyalin jawaban terakhir.

**Ctrl+C tidak keluar** — ketik `/exit`.

**"Autentikasi gagal"** — key salah/dicabut/belum aktif. Jalankan `/connect` lagi.

**"Model tidak ditemukan"** — nama model salah atau tidak tersedia untuk akunmu. Salin dari dokumentasi resmi, ganti dengan `/model`.

**"Batas permintaan atau kuota tercapai"** — kuota (termasuk kuota gratis) habis atau terlalu sering. Tunggu atau cek akun provider.

**"Tidak dapat terhubung"/timeout** — cek internet/proxy/firewall. Local Mode tetap berfungsi (`/mode local`).

**`linuxai --cloud` bilang belum dikonfigurasi** — mode CLI memakai konfigurasi tersimpan. Jalankan `linuxai`, `/connect`, dan pilih simpan.

**Jawaban Local Mode "belum punya jawaban"** — normal; Local Mode bukan AI generatif. Tulis ulang dengan kata kunci lebih jelas atau pakai Cloud Mode.

**Menghapus semua data LinuxAI** — `/settings delete-all` lalu `pipx uninstall linuxai`.
