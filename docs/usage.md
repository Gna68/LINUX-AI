# Penggunaan

## Membuka
`linuxai` membuka TUI layar penuh. Tampilan awal: nama LinuxAI di tengah, tagline *Your Linux Companion*, mode aktif
(`LOCAL`/`CLOUD`), dan kolom input di bawah. Setelah chat dimulai, branding menjadi header ringkas.

## Keyboard
| Tombol | Fungsi |
|---|---|
| Enter | Kirim pesan |
| PgUp / PgDn | Scroll percakapan |
| Esc | Batalkan wizard `/connect` |
| Ctrl+L | Bersihkan percakapan |
| Ctrl+T | Ganti tema gelap/terang |
| `/` | Menu saran perintah; ↑/↓ pilih, Enter jalankan, Tab lengkapi, Esc tutup |
| Shift+drag, Ctrl+Shift+C | Pilih dan salin teks lewat terminal |
| Ctrl+C | Salin teks terpilih; jika tidak ada, keluar (atau `/exit`) |

## Satu pertanyaan dari shell
```bash
linuxai "apa fungsi perintah grep"        # Local Mode
linuxai --cloud "jelaskan pesan error ini" # Cloud Mode (perlu /connect sebelumnya, simpan konfigurasi)
```
Mode cloud via CLI hanya memakai konfigurasi yang **tersimpan**. Konfigurasi "hanya sesi ini" tidak tersedia di luar TUI.

## Menganalisis output terminal
Salin output/pesan error, tempel ke kolom input. Di Cloud Mode model akan menjelaskannya. Di Local Mode, kata kunci
seperti `permission denied` atau `command not found` akan dikenali.

## Slash commands
`/connect`, `/copy`, `/provider`, `/model`, `/mode`, `/settings`, `/clear`, `/help`, `/exit`. Lihat README untuk tabelnya.
