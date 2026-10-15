# Keamanan

## Batasan "hanya chatbot" (ditegakkan lewat arsitektur)
LinuxAI hanya menghasilkan dan menampilkan teks. Di kode **tidak ada**: eksekusi shell/script, `subprocess`, `os.system`,
`eval/exec`, tool/function calling, MCP/plugin, akses filesystem untuk diagnosis, atau kontrol keyboard/mouse/browser.
System prompt hanya instruksi perilaku, bukan mekanisme keamanan.

Penegakan:
- Payload ke provider tidak pernah memuat `tools`; permintaan tool dari model diabaikan (`TOOL_IGNORED`).
- Teks dari model dibersihkan dari escape sequence terminal dan karakter kontrol, dan dirender sebagai teks literal (bukan markup).
- `python -m linuxai.safety.scanner` memindai seluruh source dengan AST dan gagal jika menemukan mekanisme eksekusi,
  kode dinamis, kontrol perangkat, tool calling, atau akses filesystem di luar `config/` (penyimpanan konfigurasi) dan
  `safety/` (pemindai itu sendiri, alat pengembangan). Tes otomatis menjalankannya.

## API key
- Disimpan hanya jika kamu setuju, di `~/.config/linuxai/config.json`; direktori `0700`, file `0600`, ditulis atomik.
- Input key disembunyikan; key tidak pernah di-echo, ditampilkan penuh, atau dicatat. Aplikasi tidak memakai logging.
- Pesan error tidak memuat respons mentah provider; jika model memantulkan key, bagian itu disamarkan.
- Key hanya dikirim ke provider yang kamu konfigurasi; redirect ditolak; base URL OpenRouter dikunci; `http://` hanya localhost.
- Tidak ada key bawaan di source code atau repository (`.gitignore` mengecualikan `config.json` dan `.env`).

### Batasan penyimpanan (jujur)
Key disimpan sebagai **teks biasa** di file ber-izin 0600. Siapa pun yang bisa masuk sebagai akunmu (atau membaca disk
yang tidak terenkripsi, atau memakai `sudo`) bisa membacanya. Untuk perlindungan lebih baik: pakai enkripsi disk/home,
pilih "hanya sesi ini" saat `/connect`, buat key dengan batas kuota/izin minimum di sisi provider, dan cabut key
jika perangkat hilang. Hapus kapan saja dengan `/settings delete-key` atau `/settings delete-all`.

## Privasi
Saat `/connect`, permintaan daftar model dan tes koneksi hanya dikirim setelah kamu setuju, dan hanya ke provider pilihanmu.
Cloud Mode mengirim percakapan sesi cloud ke provider pilihanmu. Local Mode tidak mengirim apa pun. Percakapan
yang terjadi di Local Mode tidak ikut terkirim saat kamu beralih ke Cloud. Berganti provider mengosongkan konteks cloud.
Jangan menempelkan password, key, atau data sensitif ke chat cloud.

## Melaporkan masalah
Jika menemukan jalur yang melanggar batasan di atas, anggap itu bug keamanan.
