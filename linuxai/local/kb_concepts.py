# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Basis pengetahuan Local Mode: konsep dasar dan istilah Linux."""
from __future__ import annotations

from linuxai.local.entry import T

CONCEPTS = [
    T("what-is-linux", "Apa itu Linux", "linux|apa itu linux|linux itu apa|apa sih linux|tentang linux|sejarah linux|linux adalah", """
Linux adalah **kernel** (inti sistem operasi) buatan Linus Torvalds sejak 1991. Dalam obrolan sehari-hari, "Linux" biasanya berarti sistem operasi lengkap yang dibangun di atas kernel itu, yang disebut **distro** (Ubuntu, Linux Mint, Fedora, dll.).

- Gratis dan open source: kodenya terbuka, boleh dipakai dan diubah.
- Dipakai di server, superkomputer, ponsel Android (kernelnya Linux), dan desktop.
- Banyak pilihan: distro dan tampilan (desktop environment) bisa dipilih sesuai selera.

Tanya lanjut: 'apa itu distro', 'apa beda Windows dan Linux', atau 'distro apa untuk pemula'.""", short=True),
    T("kernel", "Apa itu kernel", "kernel|apa itu kernel|kernel linux|versi kernel linux", """
Kernel adalah inti sistem operasi: penghubung antara aplikasi dan perangkat keras (CPU, RAM, disk, jaringan, driver).
Linux sebenarnya hanya kernel; distro menambahkan aplikasi, pengelola paket, dan tampilan di atasnya.

Cek versi kernel: `uname -r`. Kernel diperbarui lewat update sistem dan baru aktif setelah restart.""", short=True),
    T("distro-def", "Apa itu distro", "distro|distribusi linux|apa itu distro|distro itu apa", """
Distro (distribusi) Linux adalah paket lengkap: kernel Linux + aplikasi + pengelola paket + desktop + pengaturan bawaan.
Contoh: Ubuntu, Linux Mint, Debian, Fedora, Arch, openSUSE.

Distro berbeda dalam: cara instal aplikasi (apt, dnf, pacman), jadwal update, tingkat kemudahan, dan target pengguna.
Untuk pemula, Linux Mint atau Ubuntu paling sering disarankan. Tanya: 'distro apa untuk pemula'.""", short=True),
    T("open-source", "Open source dan gratis", "open source|opensource|linux gratis|linux gratis atau berbayar|apakah linux gratis|gratis", """
Open source berarti kode sumbernya terbuka: siapa pun boleh melihat, memakai, mengubah, dan membagikannya sesuai lisensi (misalnya GPL atau MIT).
Mayoritas distro dan aplikasi Linux gratis. Ada juga layanan dukungan berbayar dari perusahaan (misalnya untuk server).
"Gratis" bukan berarti tanpa aturan: setiap lisensi punya syarat, misalnya wajib mencantumkan nama pembuat.""", short=True),
    T("gnu", "GNU dan GPL", "gnu|gpl|gnu linux|gnu/linux|lisensi gpl", """
GNU adalah proyek perangkat lunak bebas (Richard Stallman) yang menyediakan banyak alat dasar (bash, gcc, coreutils seperti `ls` dan `cp`). Digabung dengan kernel Linux, jadilah sistem GNU/Linux.
GPL adalah lisensi 'copyleft': turunan dari kode GPL harus tetap terbuka dengan lisensi yang sama.""", short=True),
    T("why-linux", "Kelebihan dan kekurangan Linux", "kelebihan linux|kekurangan linux|kenapa pakai linux|kenapa harus linux|untung rugi linux|alasan pakai linux|linux bagus|linux lebih baik", """
**Kelebihan:** gratis dan open source; ringan di perangkat lama; privasi lebih terkendali; update bisa diatur; tidak ada iklan atau bloatware bawaan; sangat bisa dikustomisasi; bagus untuk belajar pemrograman dan server.
**Kekurangan:** sebagian aplikasi (Adobe, beberapa game dengan anti-cheat, aplikasi kantor tertentu) tidak punya versi Linux; dukungan perangkat keras tertentu bisa kurang; ada kurva belajar.
Sebelum pindah, cek apakah aplikasi yang kamu butuhkan punya versi atau pengganti di Linux. Coba dulu lewat live USB."""),
    T("linux-safe", "Apakah Linux aman", "linux aman|keamanan linux apakah aman|linux anti virus|linux kebal virus|linux bisa kena virus", """
Linux desktop umumnya lebih jarang diserang malware dan punya model izin yang ketat, tetapi **tidak kebal**.
Kebiasaan aman: pasang aplikasi dari repositori resmi, update rutin, jangan menjalankan skrip asing (`curl ... | sudo bash`), pakai password kuat dan enkripsi disk untuk laptop, dan jangan memberi `sudo` sembarangan."""),
    T("ubuntu", "Apa itu Ubuntu", "ubuntu|apa itu ubuntu|ubuntu itu apa", """
Ubuntu adalah distro berbasis Debian buatan Canonical, sangat populer dan ramah pemula. Desktop bawaan: GNOME. Rilis LTS (Long Term Support) keluar tiap 2 tahun dan didukung bertahun-tahun.
Variannya: Kubuntu (KDE), Xubuntu (Xfce), Lubuntu (ringan), Ubuntu MATE. Software Center memakai Snap secara default.""", short=True),
    T("mint", "Apa itu Linux Mint", "linux mint|mint|apa itu linux mint|apa itu mint", """
Linux Mint adalah distro berbasis Ubuntu yang menekankan kemudahan. Edisi Cinnamon tampilannya mirip Windows klasik; ada juga MATE dan Xfce (lebih ringan).
Sudah punya Update Manager, Software Manager, Timeshift (snapshot sistem), dan Driver Manager. Tidak memakai Snap secara default.""", short=True),
    T("debian", "Apa itu Debian", "debian|apa itu debian", """
Debian adalah distro tertua dan sangat stabil; menjadi dasar Ubuntu dan Linux Mint. Paketnya diinstal dengan `apt` dan berformat .deb.
Rilis stabilnya konservatif (paket tidak terlalu baru tapi andal), cocok untuk server dan pengguna yang menginginkan stabilitas.""", short=True),
    T("arch", "Apa itu Arch Linux", "arch|arch linux|apa itu arch|pacman|aur|yay|manjaro|endeavouros", """
Arch Linux adalah distro **rolling release** yang minimalis: kamu membangun sistem sendiri dari dasar. Pengelola paket: `pacman`; repositori komunitas: **AUR** (dipakai lewat helper seperti `yay`).
Pembaruan selalu terbaru tetapi butuh perawatan; cocok untuk yang mau belajar mendalam. Turunan yang lebih mudah: EndeavourOS dan Manjaro.
```
sudo pacman -Syu          # update seluruh sistem
sudo pacman -S nama       # pasang paket
sudo pacman -Rns nama     # hapus paket beserta dependensi
```""", short=True),
    T("fedora", "Apa itu Fedora", "fedora|dnf|rpm|apa itu fedora|red hat|rhel|centos|rocky", """
Fedora adalah distro yang disponsori Red Hat dengan paket relatif baru dan GNOME murni. Pengelola paket: `dnf` (format .rpm).
```
sudo dnf upgrade          # update sistem
sudo dnf install nama     # pasang paket
sudo dnf remove nama      # hapus paket
```
RHEL, CentOS Stream, Rocky, dan AlmaLinux adalah keluarga yang sama, banyak dipakai di server.""", short=True),
    T("opensuse", "Apa itu openSUSE", "opensuse|suse|zypper|tumbleweed|leap", """
openSUSE ada dua jalur: **Leap** (stabil) dan **Tumbleweed** (rolling). Pengelola paket: `zypper`; alat konfigurasi grafis: YaST. Bagus untuk yang mau stabilitas dengan Btrfs dan snapshot bawaan.""", short=True),
    T("lts-rolling", "LTS dan rolling release", "lts|rolling release|rolling|point release|versi lts|apa itu lts|apa itu rolling", """
- **LTS / point release**: versi dirilis berkala dan didukung lama (contoh Ubuntu LTS). Stabil dan terprediksi.
- **Rolling release**: tidak ada versi besar; paket diperbarui terus-menerus (Arch, Tumbleweed). Selalu terbaru, tetapi lebih sering berubah dan perlu perawatan.
Pemula umumnya lebih nyaman di rilis LTS atau Linux Mint.""", short=True),
    T("repo-def", "Repositori dan PPA", "repository|repositori|repo|ppa|add-apt-repository|apa itu repository|apa itu ppa|tambah repository", """
Repositori adalah 'gudang paket' resmi tempat `apt` mengunduh aplikasi. Distro sudah menyertakan daftar repositori bawaan (`/etc/apt/sources.list` dan `/etc/apt/sources.list.d/`).
**PPA** adalah repositori tambahan milik pihak ketiga di Ubuntu:
```
sudo add-apt-repository ppa:nama/ppa
sudo apt update
```
Hati-hati: PPA bukan buatan distro; hanya tambah dari sumber yang kamu percaya, dan hapus jika tidak dipakai (`sudo add-apt-repository --remove ppa:nama/ppa`).""", short=True),
    T("dependency", "Dependensi paket", "dependency|dependensi|apa itu dependency|dependencies|ketergantungan paket", """
Dependensi adalah paket lain yang dibutuhkan sebuah aplikasi agar berjalan. Pengelola paket (apt, dnf, pacman) menginstalnya otomatis. Kalau ada konflik atau kerusakan:
```
sudo apt --fix-broken install
```
Lihat dependensi sebuah paket: `apt depends nama`.""", short=True),
    T("systemd-def", "Apa itu systemd dan service", "systemd|daemon|service linux|apa itu systemd|apa itu daemon|apa itu service|unit file", """
systemd adalah sistem init yang menjalankan layanan (service/daemon) saat boot, mengelola log (journald), timer, dan lainnya. Layanan = program latar belakang seperti ssh, bluetooth, NetworkManager.
Kontrol layanan: `systemctl status|start|stop|restart|enable|disable nama`. Log: `journalctl -u nama`. (Tanya 'systemctl' atau 'journalctl' untuk contoh.)""", short=True),
    T("process-def", "Proses dan PID", "proses|process|pid|apa itu proses|apa itu pid|background process|proses latar belakang", """
Proses adalah program yang sedang berjalan; setiap proses punya nomor unik **PID**. Lihat dengan `ps aux` atau `top`/`htop`. Hentikan dengan `kill PID`.
Menjalankan perintah di latar belakang: tambahkan `&` di akhir (`perintah &`), lihat dengan `jobs`, bawa kembali dengan `fg`.""", short=True),
    T("wayland-x11", "Wayland vs X11", "wayland|x11|xorg|wayland vs x11|x11 vs wayland|apa itu wayland|apa itu x11|apa itu xorg", """
X11 (Xorg) adalah sistem tampilan grafis lama; **Wayland** adalah penggantinya yang lebih modern dan aman. Banyak distro (Ubuntu GNOME, Fedora) kini memakai Wayland secara default.
Perbedaan yang terasa pengguna: Wayland lebih mulus dan aman, tetapi beberapa aplikasi lama (screen sharing, remote desktop, alat yang mengontrol keyboard/mouse global) kadang bermasalah. Di layar login biasanya ada opsi memilih sesi 'Xorg'.
Cek sesi aktif: `echo $XDG_SESSION_TYPE`.""", short=True),
    T("de-vs-wm", "Window manager dan tiling", "window manager|tiling|tiling window manager|i3|sway|hyprland|hyperland|awesome wm|bspwm|dwm|apa itu window manager|apa itu tiling|apa itu hyprland|rice|ricing", """
**Desktop environment** (GNOME, KDE, Cinnamon) = paket lengkap: panel, menu, pengaturan, jendela. **Window manager** hanya mengatur jendela; sisanya kamu pasang sendiri.
**Tiling WM** (i3, Sway, bspwm, **Hyprland**) menyusun jendela otomatis tanpa tumpang-tindih, dikendalikan dengan keyboard dan file konfigurasi teks. Hyprland berjalan di Wayland dan terkenal dengan animasi dan kustomisasi tinggi. 'Rice' = mempercantik tampilan.
Cocok untuk yang mau kustomisasi mendalam, tetapi butuh waktu belajar. Pemula sebaiknya mulai dari Cinnamon/GNOME/KDE dulu; kamu bisa memasang WM tambahan dan memilihnya di layar login.""", short=True),
    T("grub-uefi", "GRUB, BIOS, UEFI", "bootloader|apa itu grub|uefi|bios|secure boot|apa itu uefi|apa itu bios|apa itu bootloader|legacy boot", """
- **BIOS/UEFI**: firmware di mesin yang berjalan pertama saat dinyalakan. UEFI adalah versi modern (boot dari partisi EFI). Masuk dengan tombol F2/F12/Del/Esc (beda merek).
- **Bootloader (GRUB)**: program yang memilih dan memuat OS (menu pilihan Linux/Windows).
- **Secure Boot**: fitur UEFI yang hanya mengizinkan bootloader bertanda tangan; Ubuntu dan Mint umumnya kompatibel, tetapi driver pihak ketiga (misal NVIDIA) mungkin butuh langkah tambahan.""", short=True),
    T("swap-zram", "Swap dan zram", "swap|zram|swapfile|apa itu swap|memori virtual|ram habis swap|tambah swap", """
Swap adalah ruang di disk yang dipakai sebagai 'RAM cadangan' saat RAM penuh (mirip pagefile Windows). **zram** menyimpan swap terkompresi di RAM sehingga lebih cepat.
Lihat: `swapon --show` dan `free -h`. Swap yang terpakai sedikit itu normal; kalau sering penuh, RAM-mu kurang atau ada aplikasi yang boros.""", short=True),
    T("filesystems", "Sistem berkas: ext4, NTFS, exFAT", "ext4|btrfs|fat32|exfat|xfs|filesystem|sistem berkas|format disk apa|apa itu ext4|apa itu ntfs|apa itu exfat|apa itu btrfs", """
- **ext4**: standar Linux, stabil dan cepat. Cocok untuk partisi sistem.
- **Btrfs**: fitur snapshot dan kompresi (default Fedora/openSUSE).
- **NTFS**: format Windows; Linux bisa baca-tulis tetapi izin file tidak dipetakan penuh.
- **exFAT**: aman dibaca di Windows, Linux, dan macOS; cocok untuk flashdisk dan disk eksternal berbagi OS.
- **FAT32**: kompatibel luas tapi satu file maksimal 4 GB.
Untuk disk yang dipakai bergantian dengan Windows pakai exFAT atau NTFS; untuk Linux saja pakai ext4.""", short=True),
    T("mount-def", "Mount dan mount point", "mount|mount point|titik mount|apa itu mount|mount disk|umount|unmount|cara mount|cara umount", """
Mount = 'menempelkan' disk/partisi ke sebuah folder agar isinya bisa diakses. Di desktop biasanya otomatis (muncul di sidebar file manager, di `/media/namamu/`).
Manual:
```
lsblk -f                           # cari nama partisi, mis. sdb1
sudo mkdir -p /mnt/data
sudo mount /dev/sdb1 /mnt/data     # tempelkan
sudo umount /mnt/data              # lepas sebelum cabut
```
Pastikan nama partisi benar; salah partisi bisa berbahaya.""", short=True),
    T("symlink", "Symlink dan hard link", "symlink|symbolic link|soft link|hard link|shortcut linux|ln -s|apa itu symlink|buat shortcut|membuat shortcut", """
Symlink (symbolic link) adalah 'shortcut' di Linux: file kecil yang menunjuk ke file/folder lain.
```
ln -s /path/asli /path/shortcut     # buat symlink
ls -l                                # symlink tampil dengan tanda ->
```
Hard link (`ln` tanpa -s) adalah nama kedua untuk data yang sama; jarang dipakai pemula."""),
    T("pipe-redirect", "Pipe dan redirect", "pipe|redirect|redirection|stdout|stderr|stdin|apa itu pipe|tanda pipe|alihkan output|simpan output ke file", """
- `|` (pipe): menyambung output satu perintah jadi input perintah berikutnya. Contoh: `ls | wc -l` (hitung file).
- `>`: tulis output ke file (**menimpa** isinya). Contoh: `ls > daftar.txt`
- `>>`: tambahkan ke akhir file. Contoh: `echo catatan >> log.txt`
- `2>&1`: gabungkan pesan error ke output biasa. Contoh: `perintah > hasil.txt 2>&1`
- `<`: ambil input dari file. Contoh: `sort < data.txt`""", cmd=True),
    T("dotfiles", "Dotfiles dan file tersembunyi", "dotfiles|dotfile|file tersembunyi|hidden file|file titik|ctrl+h|tampilkan file tersembunyi|lihat file tersembunyi", """
File/folder yang namanya diawali titik (`.bashrc`, `.config`, `.ssh`) disembunyikan secara default; itu biasanya konfigurasi pribadi ('dotfiles').
Menampilkan: di file manager tekan **Ctrl+H**; di terminal `ls -a`.""", cmd=True),
    T("tty", "TTY dan konsol teks", "tty|konsol teks|ctrl+alt+f3|ctrl alt f3|virtual console|layar teks|keluar dari gui", """
TTY adalah konsol teks murni tanpa tampilan grafis. Berpindah: **Ctrl+Alt+F3** (atau F2–F6) untuk TTY; kembali ke desktop dengan Ctrl+Alt+F1 atau F2 (tergantung distro).
Berguna saat desktop macet: login di TTY lalu perbaiki (`sudo apt update`, restart layanan, lihat log). Tulis password tidak terlihat itu normal."""),
    T("compile-source", "Kompilasi dari source", "compile|kompilasi|build from source|install dari source|make install|configure make|cmake|build-essential|gcc|g++|make|apa itu compile", """
Beberapa program hanya tersedia sebagai kode sumber. Pola umum:
```
sudo apt install build-essential       # compiler dan alat dasar
./configure && make                    # atau: cmake -B build && cmake --build build
sudo make install                      # pasang (sebaiknya lewat checkinstall/paket jika bisa)
```
Selalu baca README proyek. Utamakan paket dari repositori, Flatpak, atau AppImage dulu; kompilasi manual sulit dibersihkan.""", cmd=True),
    T("gui-cli", "GUI dan CLI", "gui|cli|command line|commandline|apa itu cli|apa itu gui|baris perintah|antarmuka grafis|apa itu command line", """
GUI = antarmuka grafis (jendela, mouse). CLI = antarmuka baris perintah (terminal, ketik teks). Hampir semua hal di Linux bisa dilakukan lewat GUI, tetapi CLI sering lebih cepat, bisa diulang lewat skrip, dan standar untuk server serta tutorial.
Kamu tidak wajib jago terminal untuk memakai Linux harian; pelajari bertahap mulai dari `ls`, `cd`, `cp`, `apt`.""", short=True),
    T("sudoers-su", "sudoers dan su", "sudoers|su|apa itu sudoers|grup sudo|tambah user ke sudo|user tidak bisa sudo|jadi root|login root|su -", """
- Akun yang boleh memakai `sudo` adalah anggota grup `sudo` (Ubuntu/Mint/Debian) atau `wheel` (Fedora/Arch).
- Menambahkan user ke grup sudo (dari akun yang sudah admin): `sudo usermod -aG sudo namauser`, lalu logout/login ulang.
- `su -` berpindah menjadi root dengan password root; umumnya tidak perlu dipakai di Ubuntu/Mint (root dikunci). Gunakan `sudo` untuk satu perintah. Mengedit aturan sudo harus lewat `sudo visudo`; salah edit bisa mengunci sudo.""", cmd=True),
    T("cron", "Jadwal tugas (cron)", "cron|crontab|jadwal otomatis|jadwalkan tugas|scheduler|task scheduler|jalankan otomatis tiap|systemd timer", """
Cron menjalankan perintah sesuai jadwal (setara Task Scheduler Windows).
```
crontab -e          # edit jadwal milikmu
crontab -l          # lihat jadwal
```
Format: `menit jam tanggal bulan hari-minggu perintah`. Contoh tiap hari jam 02:30:
`30 2 * * * /home/namamu/backup.sh`
Gunakan path lengkap dan beri izin eksekusi skripnya. Alternatif modern: systemd timer.""", cmd=True),
    T("sandbox-intro", "Cara belajar Linux", "belajar linux|mulai belajar linux|roadmap linux|tips pemula linux|pemula linux|baru pakai linux|baru pindah linux|mulai dari mana", """
Saran urutan belajar untuk pemula:
1. Pakai desktop dulu (Mint/Ubuntu); biasakan Software Manager dan Settings.
2. Pelajari struktur folder (tanya 'struktur folder linux').
3. Terminal dasar: `pwd`, `ls`, `cd`, `cp`, `mv`, `rm`, `mkdir`, `cat`, `nano`.
4. Pengelola paket: `apt update`, `apt install`, `apt remove` dan konsep `sudo`.
5. Izin file (`chmod`, `chown`) dan pengguna.
6. Jaringan dan log: `ip a`, `ping`, `journalctl`.
7. Skrip bash, git, dan alat pengembangan.
Gunakan `man perintah` dan `perintah --help`, dan buat snapshot Timeshift sebelum bereksperimen.""", short=False),
]
