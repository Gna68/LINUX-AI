# Provider Cloud

Kamu memakai **API key milikmu sendiri**. LinuxAI tidak menyediakan key atau layanan.
Ketersediaan model, harga, dan kuota (termasuk kuota gratis) ditentukan provider dan **dapat berubah**;
jangan menganggap semuanya gratis. Selalu cek dokumentasi resmi.

| Provider | Id | Dokumentasi |
|---|---|---|
| Google Gemini API | `gemini` | https://ai.google.dev/gemini-api/docs |
| OpenRouter | `openrouter` | https://openrouter.ai/docs |
| Kompatibel OpenAI API | `openai-compatible` | https://platform.openai.com/docs (atau dokumentasi server pilihanmu) |

## Nama model
LinuxAI **tidak** menyertakan daftar model bawaan karena nama model berubah dan berbeda per akun.
Saat `/connect`, setelah API key dimasukkan dan kamu setuju, LinuxAI meminta daftar model langsung ke provider
(`GET`, API key hanya dikirim ke provider yang kamu pilih) lalu menampilkannya sebagai daftar yang bisa dicari.
Jika pengambilan gagal atau kamu menolak, ketik nama model manual (salin dari dokumentasi resmi).
Format yang diterima: huruf, angka, `.`, `:`, `/`, `-`, `_` (maks. 200 karakter).

## Detail teknis
- **Daftar model**: Gemini `GET .../v1beta/models` (hanya model yang mendukung `generateContent`); OpenRouter dan OpenAI-compatible `GET {base_url}/models`.
- **Gemini**: `POST .../v1beta/models/{model}:generateContent`, key lewat header `x-goog-api-key`, system prompt lewat `system_instruction`.
- **OpenRouter**: `POST https://openrouter.ai/api/v1/chat/completions`, `Authorization: Bearer`. Base URL dikunci.
- **OpenAI-compatible**: `POST {base_url}/chat/completions`. Base URL default `https://api.openai.com/v1`; harus `https://`
  (`http://` hanya untuk localhost, mis. server model lokal milikmu sendiri).
- Permintaan **tidak pernah** memuat `tools`/function calling. Jika model membalas dengan permintaan tool, itu diabaikan.
- Redirect HTTP ditolak agar key tidak terkirim ke host lain. Timeout default 30 detik.

## Kesalahan yang ditangani
Autentikasi (401/403 dan "API key not valid" pada Gemini), model tidak ditemukan (404), rate limit/kuota (429),
timeout, gangguan jaringan, error server (5xx), respons kosong/diblokir/tidak terbaca. Pesan error sengaja ringkas dan
tidak menampilkan isi respons mentah.

## Menambah provider
Buat kelas turunan `Provider` di `linuxai/providers/` (implementasikan `build_request` dan `extract_text`),
lalu daftarkan di `linuxai/providers/__init__.py`.

## Status validasi
Format request mengikuti dokumentasi resmi sepengetahuan penulis, tetapi dites hanya dengan mock. Pengembangan awal
dilakukan tanpa akses internet sehingga belum divalidasi terhadap layanan sungguhan. Jika ada ketidakcocokan,
laporkan atau sesuaikan di file provider terkait.
