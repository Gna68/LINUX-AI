# Instalasi

## Persyaratan
- Linux Mint 21+ atau Ubuntu 22.04+ (Python 3.10+).
- Terminal. Internet hanya untuk memasang paket dan untuk Cloud Mode.

## Mengunduh
```bash
git clone https://github.com/Gna68/LINUX-AI.git
```
Atau ekstrak zip proyek lalu masuk ke foldernya.

## Opsi A — pipx (disarankan, tidak mengotori Python sistem)
```bash
sudo apt update
sudo apt install python3 python3-venv pipx
pipx ensurepath
# tutup lalu buka terminal baru
cd LINUX-AI
pipx install .
linuxai --version
```

## Opsi B — virtual environment
```bash
cd LINUX-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
linuxai
```
Setiap membuka terminal baru, aktifkan lagi dengan `source .venv/bin/activate` di folder proyek.

## Untuk pengembangan
```bash
pip install -e ".[dev]"
pytest
```

## Update / uninstall
```bash
cd LINUX-AI && pipx install --force .
pipx uninstall linuxai
```
Konfigurasi ada di `~/.config/linuxai/`; hapus manual jika ingin membersihkan.

## Catatan
LinuxAI tidak memasang paket sistem, tidak butuh `sudo` untuk berjalan, dan tidak membuat layanan latar belakang.
Perintah `sudo apt ...` di atas dijalankan olehmu sendiri hanya untuk memasang Python/pipx.
