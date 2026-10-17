# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Basis pengetahuan Local Mode: pesan error dan pemecahan masalah umum."""
from __future__ import annotations

from linuxai.local.entry import T

TROUBLE = [
    T("apt-unable-locate", "E: Unable to locate package", "unable to locate package|paket tidak ditemukan|e: unable to locate|package not found apt|apt install tidak ketemu|tidak bisa menemukan paket", """
Penyebab umum:
1. Daftar paket belum diperbarui: `sudo apt update` lalu coba lagi.
2. Nama paket salah/berbeda: cari dengan `apt search kata`.
3. Repositori yang menyediakannya belum aktif (mis. `universe`/`multiverse` di Ubuntu: `sudo add-apt-repository universe`).
4. Versi distro sudah tidak didukung, sehingga repositori dihapus.
Sebutkan nama paket dan versi distro bila masih gagal."""),
    T("apt-gpg", "GPG error / NO_PUBKEY", "no_pubkey|gpg error|the following signatures couldn't be verified|kunci gpg|signature invalid|expkeysig|public key is not available|apt key", """
Error GPG/NO_PUBKEY berarti kunci tanda tangan repositori pihak ketiga tidak ada atau kedaluwarsa. Cara aman: ambil ulang kunci dari **situs resmi repositori itu** (ikuti petunjuk instalasinya), jangan dari sumber acak.
Jika repositori itu sudah tidak dipakai, hapus file di `/etc/apt/sources.list.d/` yang bersangkutan, lalu `sudo apt update`. Jangan menjalankan perintah `apt-key` dari tutorial lama tanpa memahaminya."""),
    T("apt-404", "apt update: 404 Not Found / Release file", "404 not found apt|does not have a release file|release file|failed to fetch apt|repository is no longer signed|repositori tidak punya release|err:|gagal fetch apt|hash sum mismatch", """
'404 Not Found' atau 'does not have a Release file' biasanya karena repositori (sering PPA) tidak mendukung versi distro-mu atau sudah dihapus. Langkah:
1. Lihat baris yang bermasalah di output `sudo apt update`.
2. Hapus/nonaktifkan repositori itu (Software & Updates → Other Software, atau hapus file di `/etc/apt/sources.list.d/`).
3. `sudo apt update` lagi.
'Hash Sum mismatch': coba lagi beberapa saat kemudian atau `sudo rm -rf /var/lib/apt/lists/*` lalu `sudo apt update` (mirror sedang sinkron)."""),
    T("apt-broken", "Paket rusak / dependency error", "broken packages|held broken packages|unmet dependencies|fix-broken|dpkg error processing|paket rusak|dependensi rusak|e: sub-process|dpkg: error processing", """
Urutan perbaikan yang aman:
```
sudo apt update
sudo apt --fix-broken install
sudo dpkg --configure -a
sudo apt autoremove
```
Pastikan tidak ada proses apt lain yang berjalan. Jika masih gagal, kirim pesan error lengkapnya (terutama baris 'dpkg: error processing package ...'). Jangan menghapus file di `/var/lib/dpkg` secara manual."""),
    T("snap-problem", "Masalah Snap", "snap tidak bisa dibuka|snap lambat|snap error|snap tidak jalan|snapd|remove snap|hapus snap|snap tidak muncul|firefox snap lambat", """
- Aplikasi Snap pertama kali dibuka bisa terasa lambat (proses mount).
- Lihat status: `snap list`, `snap changes`, `systemctl status snapd`.
- Perbarui: `sudo snap refresh`. Hapus: `sudo snap remove nama`.
- Jika tidak suka Snap, banyak aplikasi tersedia sebagai Flatpak atau paket apt. Linux Mint tidak memakai Snap secara default."""),
    T("app-not-in-menu", "Aplikasi tidak muncul di menu", "aplikasi tidak muncul di menu|tidak ada di menu aplikasi|sudah install tapi tidak muncul|icon aplikasi tidak muncul|aplikasi hilang dari menu|tidak ketemu setelah instal", """
- Cari lewat menu (Super lalu ketik nama). Flatpak/Snap kadang butuh **logout/login** agar ikon muncul.
- Cek apakah terpasang: `apt list --installed | grep nama`, `flatpak list`, `snap list`.
- Jalankan dari terminal untuk melihat error: `nama-aplikasi`.
- AppImage/aplikasi unduhan tidak masuk menu otomatis: buat launcher (tanya 'membuat launcher .desktop')."""),
    T("bad-interpreter", "bad interpreter / ^M / CRLF", "bad interpreter|^m|cr lf|crlf|\\r|required file not found|syntax error unexpected end of file|akhir baris windows|dos2unix|line ending|skrip dari windows tidak jalan|no such file or directory skrip", """
Skrip yang dibuat/diedit di Windows memakai akhir baris **CRLF**, sedangkan Linux butuh **LF**. Gejala: `bad interpreter: /bin/bash^M`, `required file not found`, atau `syntax error: unexpected end of file`.
Perbaiki:
```
sudo apt install dos2unix
dos2unix nama-skrip.sh
```
Atau di editor (VS Code: klik 'CRLF' di bar bawah → pilih LF). Di Git: `git config --global core.autocrlf input`."""),
    T("no-such-file", "No such file or directory", "no such file or directory|file atau direktori tidak ada|tidak ada berkas atau direktori|no such file|path tidak ditemukan|file tidak ketemu", """
Artinya path yang kamu ketik tidak ada. Cek:
1. Salah ketik atau **huruf besar/kecil** (Linux case-sensitive).
2. Posisi folder saat ini: `pwd`, isi folder: `ls`.
3. Spasi di nama: pakai tanda kutip (`cd "Folder Saya"`) atau backslash.
4. Untuk skrip: bisa karena shebang salah atau CRLF (tanya 'bad interpreter').
Tab melengkapi nama otomatis dan mengurangi salah ketik."""),
    T("is-a-directory", "Is a directory / not a directory", "is a directory|not a directory|omitting directory|cp -r|folder bukan file|cannot copy directory|cp omitting directory", """
Perintah yang dipakai untuk file tetapi targetnya folder (atau sebaliknya).
- Menyalin folder: `cp -r folder tujuan/` (wajib -r).
- Menghapus folder: `rm -r folder` (hati-hati) atau `rmdir` untuk folder kosong.
- 'Not a directory': bagian path-mu ternyata file, bukan folder."""),
    T("segfault", "Segmentation fault", "segmentation fault|segfault|core dumped|aplikasi crash|aplikasi keluar sendiri|program crash|crash terus|force close", """
Segmentation fault: program mengakses memori yang tidak boleh. Biasanya bug di aplikasi atau pustaka/driver yang tidak cocok.
- Update sistem dan aplikasinya, lalu jalankan ulang.
- Jalankan dari terminal untuk melihat pesan sebelum crash.
- Coba versi lain (Flatpak/AppImage) atau hapus konfigurasi aplikasi di `~/.config/nama` (cadangkan dulu).
- Pada game/aplikasi grafis, periksa driver GPU. Laporkan bug dengan log ke pengembang."""),
    T("read-only-fs", "Read-only file system", "read-only file system|read only file system|disk read-only|tidak bisa menulis ke disk|filesystem hanya baca|remounted read-only|write protected", """
Disk dipasang hanya-baca. Penyebab: filesystem rusak dan otomatis dikunci, disk NTFS dari Windows yang hibernasi, flashdisk dengan saklar write-protect, atau disk yang mulai rusak.
- Disk Windows: matikan Fast Startup di Windows dan Shut down penuh (tanya 'ntfs').
- Cek: `dmesg | tail -30` dan `lsblk -f`. Untuk perbaikan, unmount lalu `sudo fsck /dev/sdXN` (nama partisi benar!).
- Salin data penting segera jika dmesg menunjukkan error I/O: itu tanda disk bermasalah."""),
    T("device-busy", "Device or resource busy", "device or resource busy|target is busy|umount gagal|tidak bisa eject|tidak bisa unmount|cannot unmount|usb tidak bisa dicabut|eject gagal", """
Ada proses yang masih memakai disk/folder itu. Cari dan tutup:
```
lsof +f -- /media/namamu/NAMA-DISK     # siapa yang memakai
cd ~                                   # pastikan terminalmu tidak sedang berada di dalamnya
sudo umount /media/namamu/NAMA-DISK
```
Tutup file manager/aplikasi yang membuka isinya. Tunggu proses penyalinan selesai sebelum mencabut."""),
    T("connection-refused", "Connection refused / timed out", "connection refused|connection timed out|koneksi ditolak|connection reset|no route to host|network is unreachable|tidak bisa konek server|ssh connection refused|timed out", """
- **Connection refused**: host terjangkau tetapi tidak ada layanan yang mendengarkan di port itu (layanan mati, port salah, atau firewall menolak).
- **Timed out**: paket tidak sampai (firewall menjatuhkan, alamat salah, jaringan putus).
- **No route to host / unreachable**: masalah rute/jaringan lokal.
Cek: `ping -c 3 alamat`, `ss -tulpn` (di server), `sudo ufw status`. Untuk SSH pastikan layanan berjalan (`systemctl status ssh`) dan port benar."""),
    T("host-key-verification", "Host key verification failed", "host key verification failed|remote host identification has changed|warning: remote host identification|known_hosts|ssh-keygen -r|ssh fingerprint berubah", """
SSH mendeteksi kunci server berbeda dari yang tersimpan. Bisa wajar (server diinstal ulang) atau tanda pencegatan. **Pastikan dulu alasannya.** Jika sah, hapus entri lama:
```
ssh-keygen -R alamat-server
```
Lalu sambung lagi dan verifikasi fingerprint baru dengan pemilik server."""),
    T("not-in-sudoers", "user is not in the sudoers file", "is not in the sudoers file|not in the sudoers|tidak ada di sudoers|sudoers file|tidak bisa sudo|user tidak punya sudo|this incident will be reported", """
Akunmu belum berhak memakai `sudo`. Dari akun administrator lain:
```
sudo usermod -aG sudo namauser      # Ubuntu/Mint/Debian (Fedora/Arch: wheel)
```
Lalu logout/login. Jika tidak ada akun admin, perlu recovery mode/live USB (beri tahu distro-mu). 'This incident will be reported' hanya pesan standar; di PC pribadi tidak dikirim ke siapa pun."""),
    T("resolve-host", "unable to resolve host / name resolution", "unable to resolve host|temporary failure in name resolution|could not resolve host|name or service not known|dns error|nama host tidak bisa diresolusi|tidak bisa resolve|dns tidak jalan", """
Masalah DNS/hostname.
- `sudo: unable to resolve host nama`: nama komputer belum ada di `/etc/hosts`. Tambahkan baris `127.0.1.1 nama-komputer` (lihat nama dengan `hostname`).
- 'Temporary failure in name resolution': DNS tidak berfungsi. Tes `ping -c 3 8.8.8.8`; jika berhasil tapi domain gagal, ganti DNS (tanya 'ganti dns') dan cek `resolvectl status`.
- Jika ping IP pun gagal, masalahnya di koneksi jaringan (tanya 'wifi tidak muncul')."""),
    T("black-screen", "Layar hitam setelah login / update", "layar hitam|black screen|layar hitam setelah login|stuck di logo|stuck di login|login loop|kembali ke login|tidak bisa masuk desktop|desktop tidak muncul|hanya kursor|cursor saja", """
Langkah aman:
1. Tekan **Ctrl+Alt+F3** untuk masuk TTY, login, lalu `df -h` (disk penuh sering penyebab login loop) dan `journalctl -b -p err | tail -50`.
2. Penyebab umum: disk/home penuh, file `~/.Xauthority` atau izin folder home salah (`ls -ld ~`), driver GPU bermasalah setelah update, atau kernel baru.
3. Coba pilih kernel lama di GRUB (Advanced options) atau sesi Xorg di layar login.
4. Setelah bisa masuk TTY: `sudo apt update && sudo apt --fix-broken install`.
Jangan format dulu; data biasanya aman. Sebutkan distro, GPU, dan apa yang berubah sebelum masalah muncul."""),
    T("freeze-hang", "Komputer hang / membeku", "komputer hang|laptop hang|sistem membeku|layar beku|freeze total|tidak bisa digerakkan|mouse tidak gerak|laptop macet|hang total|reisub", """
- Coba **Ctrl+Alt+F3** untuk ke TTY dan matikan proses berat (`top`, lalu `kill PID`).
- Jika total beku: tekan Alt+SysRq (PrtSc) lalu ketik perlahan **R E I S U B** untuk restart bersih (butuh SysRq aktif).
- Sebab umum: RAM habis, overheat, driver GPU, disk rusak. Cek `journalctl -b -1 -p err` setelah restart dan `sensors` untuk suhu."""),
    T("fan-heat", "Kipas berisik / laptop panas", "kipas berisik|kipas kencang|laptop panas|overheat|suhu tinggi|cpu panas|kipas terus nyala|laptop cepat panas|fan noise", """
1. Lihat siapa yang memakai CPU: `top`/System Monitor (proses 'tracker', Chrome banyak tab, atau proses macet).
2. Pasang manajemen daya: `sudo apt install tlp` dan (Intel) `thermald`.
3. Cek suhu: `sudo apt install lm-sensors` lalu `sensors`.
4. Pastikan driver GPU benar; bersihkan debu dan pertimbangkan mengganti pasta termal.
Di laptop dengan GPU NVIDIA, pastikan mode hybrid memakai GPU Intel/AMD untuk pekerjaan ringan."""),
    T("bt-headset", "Kualitas audio headset Bluetooth", "headset bluetooth kualitas|suara bluetooth jelek|bluetooth putus putus|a2dp|hsp|hfp|mic bluetooth|earbuds bluetooth|bluetooth audio buruk|airpods linux|suara headset kecil", """
Suara headset jelek biasanya karena profil berpindah ke **HSP/HFP** (mode telepon) saat mic dipakai. Di Settings → Sound, pilih profil **A2DP (High Fidelity Playback)**. Jika tidak muncul: restart audio (`systemctl --user restart pipewire pipewire-pulse wireplumber`) dan pasangkan ulang. Putus-putus: dekatkan perangkat, hindari WiFi 2.4 GHz padat, update sistem."""),
    T("kernel-panic", "Kernel panic / gagal boot", "kernel panic|not syncing|unable to mount root fs|initramfs|gagal boot|boot berhenti di initramfs|dropped to a shell|emergency mode|grub rescue|error: no such partition", """
- **initramfs/emergency**: sering karena filesystem rusak atau UUID di `/etc/fstab` salah. Dari live USB: `sudo fsck -f /dev/sdXN` pada partisi root (nama benar!).
- **grub rescue / no such partition**: GRUB kehilangan partisi (sering setelah mengubah partisi atau update Windows). Perbaiki dari live USB memakai Boot-Repair atau `grub-install`/`update-grub` lewat chroot.
- **Kernel panic setelah update**: pilih kernel lama di GRUB Advanced options.
Catat pesan error dan distro agar saran bisa lebih spesifik. Data biasanya aman; jangan format dulu."""),
    T("slow-boot", "Boot / login lambat", "boot lambat|startup lambat|nyalain lama|lama saat booting|systemd-analyze|blame|login lama|booting lambat|komputer lama nyala", """
Lihat penyebabnya:
```
systemd-analyze
systemd-analyze blame | head -15
systemd-analyze critical-chain
```
Layanan yang lama (misalnya menunggu jaringan atau disk) bisa dinonaktifkan hati-hati. Kurangi aplikasi startup (tanya 'startup applications'), pasang SSD, dan periksa disk (`sudo smartctl -a /dev/sda` dari paket smartmontools)."""),
    T("tracker-cpu", "Proses 'tracker' / indexer memakan CPU", "tracker-miner|tracker miner|localsearch|baloo|baloo_file|proses indexing|indexing|snapd cpu|kswapd|kswapd0|cpu 100", """
Proses pengindeksan file (tracker/localsearch di GNOME, baloo di KDE) bisa memakai CPU tinggi sementara setelah banyak file baru; biasanya reda sendiri. Jika terus-menerus: matikan pengindeksan di Settings → Search/Search Locations (GNOME) atau `balooctl disable` (KDE). `kswapd0` tinggi berarti RAM habis dan sistem sibuk swap; kurangi aplikasi atau tambah RAM/zram."""),
    T("ssh-permission", "SSH: Permission denied (publickey)", "permission denied (publickey)|publickey|ssh permission denied|ssh key tidak jalan|ssh minta password terus|git permission denied publickey|unprotected private key|bad permissions", """
Penyebab umum:
1. Kunci publik belum terpasang di server/GitHub (`cat ~/.ssh/id_ed25519.pub` lalu tambahkan di sana).
2. Izin file salah: `chmod 700 ~/.ssh` dan `chmod 600 ~/.ssh/id_ed25519`.
3. Agen SSH belum memuat kunci: `ssh-add ~/.ssh/id_ed25519`.
4. Nama user atau host salah. Debug: `ssh -v user@host`.
Tes GitHub: `ssh -T git@github.com`."""),
    T("flatpak-problem", "Masalah Flatpak", "flatpak tidak jalan|flatpak error|flatpak tidak ketemu|flatpak remote|flathub tidak ada|install flatpak|aktifkan flatpak|flatpak permission", """
- Pasang dan aktifkan Flathub (jika belum): `sudo apt install flatpak` lalu `flatpak remote-add --if-not-exists flathub https://dns.flathub.org/repo/flathub.flatpakrepo`, lalu logout/login.
- Jalankan: `flatpak run nama.aplikasi`. Perbarui: `flatpak update`.
- Aplikasi Flatpak berjalan dalam sandbox; izin akses file/perangkat diatur dengan Flatseal."""),
    T("nvidia-black", "Masalah NVIDIA umum", "nvidia layar hitam|nvidia driver error|nvidia-smi gagal|nvidia tidak terdeteksi|secure boot nvidia|mok enrollment|nouveau|optimus|hybrid gpu|prime-select|gpu diskrit tidak dipakai", """
- `nvidia-smi` gagal: driver belum aktif; install lewat Driver Manager/Additional Drivers lalu restart. Jika **Secure Boot** aktif, driver tidak bisa dimuat sampai kamu mendaftarkan kunci (MOK) saat boot setelah instalasi, atau matikan Secure Boot.
- Laptop hybrid: `prime-select query` / `sudo prime-select on-demand` (Ubuntu) dan jalankan aplikasi dengan GPU NVIDIA lewat menu klik kanan.
- Layar hitam setelah instalasi: boot kernel lama atau tambahkan parameter `nomodeset` sementara dari GRUB.
Sebutkan tipe GPU dan distro untuk langkah lebih tepat."""),
    T("login-password-wrong", "Password login ditolak", "password salah|incorrect password|authentication failure|login gagal|tidak bisa login|password login tidak bisa|keyboard layout saat login|capslock login|lupa password login", """
Cek dulu: Caps Lock/Num Lock, dan **layout keyboard** di layar login (kadang berbeda dari yang kamu kira, terutama simbol). Password tidak tampil saat mengetik itu normal. Jika benar-benar lupa: perlu langkah recovery (recovery mode atau live USB) yang bergantung pada distro; jangan format, data aman. Beri tahu distro dan apakah disk dienkripsi."""),
    T("time-sync-error", "Error sertifikat / jam salah", "ssl certificate problem|certificate is not yet valid|certificate has expired|sertifikat tidak valid|apt jam salah|date wrong|clock wrong|tls error|self-signed", """
Error sertifikat sering muncul karena **jam sistem salah**. Cek `timedatectl` dan sinkronkan: `sudo timedatectl set-ntp true`. Jika jam benar, mungkin repositori/server memang bermasalah; jangan menonaktifkan verifikasi sertifikat (`--no-check-certificate`, `-k`) kecuali kamu paham risikonya."""),
]
