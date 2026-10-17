# Copyright (c) 2026 Muhammad Ghana Rizqi Pratama
# SPDX-License-Identifier: MIT
"""Basis pengetahuan Local Mode: panduan aplikasi, desktop, perangkat keras, jaringan, dan file."""
from __future__ import annotations

from linuxai.local.entry import T

HOWTO = [
    # ------------------------------------------------------------ aplikasi
    T("app-browser", "Memasang browser (Chrome, Firefox, Brave)", "install chrome|install google chrome|chrome linux|install brave|brave linux|install firefox|install chromium|browser linux|pasang chrome|download chrome|chrome untuk linux", """
- **Firefox**: biasanya sudah terpasang (Mint: paket apt; Ubuntu: Snap).
- **Google Chrome**: unduh paket .deb dari situs resmi Google, lalu `sudo apt install ./google-chrome-stable_current_amd64.deb` (atau klik dua kali dan pilih Software Install).
- **Brave**: ikuti petunjuk resmi di brave.com/linux (menambah repositori sendiri).
- **Chromium**: di Ubuntu berupa Snap; di Mint lewat Software Manager atau Flatpak.
Selalu ambil dari situs resmi."""),
    T("app-vscode", "Memasang VS Code", "install vscode|install vs code|visual studio code linux|vscode linux|pasang vscode|code editor linux|install code editor", """
Beberapa cara resmi:
- Unduh .deb dari code.visualstudio.com lalu `sudo apt install ./namafile.deb` (menambah repositori Microsoft agar ikut update).
- Snap: `sudo snap install code --classic`
- Flatpak: `flatpak install flathub com.visualstudio.code`
Alternatif open source murni: VSCodium atau editor lain seperti Neovim."""),
    T("app-social", "Discord, Telegram, WhatsApp, Spotify, Zoom", "install discord|install telegram|install whatsapp|whatsapp linux|install spotify|install zoom|zoom linux|discord linux|spotify linux|telegram linux|aplikasi chat linux", """
- **Discord**: .deb dari discord.com atau Flatpak `com.discordapp.Discord`.
- **Telegram**: `sudo apt install telegram-desktop` atau Flatpak `org.telegram.desktop`.
- **WhatsApp**: tidak ada klien resmi untuk Linux; gunakan web.whatsapp.com di browser (atau aplikasi pihak ketiga dengan risiko sendiri).
- **Spotify**: Flatpak `com.spotify.Client` atau Snap.
- **Zoom**: .deb dari zoom.us atau Flatpak `us.zoom.Zoom`. Berbagi layar di Wayland kadang butuh sesi Xorg (tanya 'screen sharing wayland').
Cari juga di Software Manager."""),
    T("app-media", "VLC, OBS, codec multimedia", "install vlc|vlc linux|install obs|obs linux|codec|codec multimedia|ubuntu-restricted-extras|video tidak bisa diputar|mp3 tidak bisa diputar|mp4 tidak bisa|tidak bisa putar video|format tidak didukung", """
- **VLC**: `sudo apt install vlc` (memutar hampir semua format).
- **OBS Studio** (rekam layar/streaming): `sudo apt install obs-studio` atau Flatpak `com.obsproject.Studio`.
- **Codec**: Ubuntu: `sudo apt install ubuntu-restricted-extras`. Linux Mint: menu → 'Install Multimedia Codecs' (atau saat instalasi centang codec).
Banyak masalah 'video tidak bisa diputar' selesai dengan memasang codec atau memakai VLC."""),
    T("app-office", "Microsoft Office di Linux", "microsoft office linux|office 365 linux|word excel linux|install libreoffice|libreoffice|buka docx|buka file docx|onlyoffice|office online|ms office|word linux", """
Microsoft Office desktop tidak punya versi Linux resmi. Pilihan:
- **LibreOffice** (biasanya sudah terpasang) membuka dan menyimpan .docx/.xlsx/.pptx dengan kompatibilitas cukup baik untuk dokumen biasa.
- **OnlyOffice**: tampilan lebih mirip Office, kompatibilitas format sangat baik.
- **Office di web** (office.com) lewat browser, gratis dengan akun Microsoft.
Dokumen dengan makro atau format rumit bisa tampil sedikit berbeda; periksa sebelum mengirim."""),
    T("fonts", "Font (termasuk font Windows)", "install font|pasang font|font windows|font microsoft|ttf-mscorefonts|font times new roman|font arial|font tidak ada|tambah font|fc-cache", """
- Font Microsoft (Arial, Times New Roman, dll.): `sudo apt install ttf-mscorefonts-installer` (terima lisensi).
- Font sendiri: salin file .ttf/.otf ke folder `~/.local/share/fonts/` lalu jalankan:
```
fc-cache -f
```
Mulai ulang aplikasi agar font terbaca. Untuk dokumen dengan font berbeda, LibreOffice akan mengganti font yang tidak ada."""),
    T("virtualization", "Mesin virtual (VirtualBox, KVM)", "virtualbox|virtual box|install virtualbox|virtual machine|mesin virtual|vm|kvm|virt-manager|vmware|jalankan windows di linux|windows di virtual machine|qemu|gnome boxes", """
Menjalankan OS lain di dalam jendela:
- **VirtualBox**: `sudo apt install virtualbox` (mudah untuk pemula).
- **GNOME Boxes** atau **virt-manager (KVM/QEMU)**: lebih ringan dan cepat; butuh virtualisasi aktif di BIOS (Intel VT-x / AMD-V).
Alokasikan RAM/CPU secukupnya (jangan lebih dari setengah milikmu). Untuk menjalankan Windows, kamu butuh lisensi/ISO sendiri.""", cmd=True),
    T("remote-desktop", "Remote desktop", "remote desktop|rdp|vnc|anydesk|teamviewer|rustdesk|remmina|akses komputer jarak jauh|kendali jarak jauh|akses pc dari jauh", """
- **Mengakses Windows dari Linux (RDP)**: Remmina (`sudo apt install remmina remmina-plugin-rdp`).
- **AnyDesk/TeamViewer/RustDesk**: tersedia untuk Linux, tetapi berbagi layar di sesi **Wayland** sering bermasalah; di layar login pilih sesi **Xorg** jika perlu.
- **SSH** untuk akses terminal (`ssh user@host`).
Hanya buka akses jarak jauh jika perlu, pakai password kuat, dan jangan membuka port ke internet tanpa firewall/VPN."""),
    T("vpn", "VPN", "vpn|wireguard|openvpn|protonvpn|mullvad|install vpn|vpn linux|nordvpn|vpn gratis", """
- Banyak penyedia VPN punya aplikasi/panduan Linux (Proton VPN, Mullvad, dll.).
- Manual: **OpenVPN** atau **WireGuard** lewat NetworkManager (Settings → Network → VPN → +) dengan file konfigurasi dari penyedia.
Pilih penyedia tepercaya; VPN gratis sering menjual data. VPN tidak membuatmu anonim sepenuhnya."""),
    T("android", "Aplikasi Android, mirroring HP", "aplikasi android|waydroid|scrcpy|kdeconnect|kde connect|mirroring hp|layar hp ke laptop|android emulator|jalankan apk|install apk|apk di linux", """
- **Mirror/kontrol HP**: `scrcpy` (`sudo apt install scrcpy`, aktifkan USB debugging di HP).
- **KDE Connect**: kirim file, notifikasi, clipboard antara HP dan laptop.
- **Waydroid**: menjalankan aplikasi Android di Linux (butuh sesi Wayland dan setup tambahan).
Menjalankan .apk dari sumber tidak dikenal berisiko."""),
    T("screen-record", "Merekam layar", "rekam layar|screen record|screen recording|record layar|screencast|simple screen recorder|kooha|merekam layar", """
- GNOME: tekan **Ctrl+Shift+Alt+R** untuk mulai/berhenti merekam (video di folder Videos).
- **OBS Studio** untuk rekaman lengkap (`sudo apt install obs-studio`).
- Di Wayland pilih alat yang mendukungnya (OBS, Kooha); SimpleScreenRecorder cocok di Xorg."""),
    T("screen-share", "Berbagi layar di Wayland", "screen sharing wayland|berbagi layar|share screen|share layar|zoom tidak bisa share|teams share screen|google meet share|layar hitam saat share", """
Berbagi layar di Wayland memakai portal PipeWire. Jika layar hitam atau tidak ada pilihan layar:
1. Pastikan terpasang: `sudo apt install pipewire xdg-desktop-portal xdg-desktop-portal-gnome` (KDE: `xdg-desktop-portal-kde`).
2. Gunakan browser (Chrome/Firefox) versi terbaru; aplikasi Electron lama bisa bermasalah.
3. Alternatif: login dengan sesi **Xorg** (pilih di layar login) lalu coba lagi."""),
    T("webcam", "Webcam", "webcam|kamera|kamera tidak terdeteksi|webcam tidak muncul|cheese|kamera laptop|camera tidak|webcam tidak berfungsi", """
Cek apakah terdeteksi:
```
ls /dev/video*
lsusb
```
Uji dengan aplikasi Cheese (`sudo apt install cheese`). Di browser, pastikan izin kamera diberikan untuk situsnya. Jika tidak terdeteksi, periksa tombol Fn/privacy shutter dan pengaturan BIOS."""),
    # ------------------------------------------------------------ desktop
    T("win-shortcuts", "Pintasan keyboard Windows → Linux", "shortcut windows di linux|pintasan windows|win+d|alt+f4|ctrl+alt+del|tombol super|super+l|snap window|jendela setengah layar|alt tab", """
Padanan umum (bisa beda sedikit antar desktop):
- **Super** (tombol Windows): membuka menu/Activities.
- **Alt+Tab**: pindah aplikasi. **Alt+F4**: tutup jendela.
- **Super+L**: kunci layar. **Super+D**: tampilkan desktop (Cinnamon/KDE; di GNOME bisa diatur).
- **Super+←/→**: tempel jendela ke setengah layar.
- **Ctrl+Alt+T**: terminal. **Ctrl+Alt+Del**: menu logout/matikan (GNOME/Cinnamon).
- **PrtSc**: screenshot. Semua bisa diubah di Settings → Keyboard → Shortcuts."""),
    T("appearance", "Tema, wallpaper, mode gelap", "ganti wallpaper|ganti tema|mode gelap|dark mode|tema gelap|ganti ikon|icon theme|ganti background|ganti tampilan desktop|theme linux|cursor theme", """
- **Wallpaper**: klik kanan desktop → Change Background (atau Settings → Appearance).
- **Mode gelap**: Settings → Appearance (Mint: Themes → Mode).
- **Tema/ikon**: Mint: Themes; GNOME: pasang 'GNOME Tweaks' (`sudo apt install gnome-tweaks`); KDE: System Settings → Appearance.
- Tema manual disimpan di `~/.themes` dan `~/.icons`. Pasang dari sumber tepercaya (gnome-look.org, store.kde.org)."""),
    T("keyboard-lang", "Bahasa dan layout keyboard", "ganti bahasa|bahasa indonesia|ganti keyboard|layout keyboard|keyboard layout|keyboard us|input method|locale|bahasa sistem|ubah bahasa linux|language pack", """
- **Bahasa sistem**: Settings → Region & Language (Mint: Languages). Ubuntu mungkin minta memasang language pack (`sudo apt install language-pack-id`).
- **Layout keyboard**: Settings → Keyboard → Input Sources (tambah US, Indonesia, dll.) dan ganti dengan Super+Space.
Mulai ulang sesi (logout/login) agar bahasa sistem berubah."""),
    T("multi-monitor", "Monitor ganda dan resolusi", "dual monitor|monitor kedua|multi monitor|layar kedua|layar tambahan|hdmi tidak terdeteksi|monitor external|monitor eksternal|proyektor|duplikat layar|extend layar", """
Settings → **Displays**: atur monitor sebagai Join/Extend atau Mirror, urutan posisi, resolusi, dan refresh rate. Layar eksternal tidak terdeteksi? Coba kabel/port lain, cabut-pasang, dan pasang driver GPU yang benar (tanya 'driver nvidia'). Di laptop hybrid GPU, port HDMI kadang tersambung ke GPU diskrit."""),
    T("hidpi", "Skala layar (HiDPI)", "skala layar|display scaling|hidpi|teks terlalu kecil|teks kecil|layar 4k|fractional scaling|layar terlalu kecil|ukuran teks", """
Settings → Displays → **Scale** (100%, 125%, 150%, 200%). Di GNOME, skala pecahan (fractional) bisa perlu diaktifkan. Ukuran font saja: Settings → Accessibility → Large Text, atau Tweaks → Font scaling. Aplikasi lama (X11) bisa tampak buram pada skala pecahan."""),
    T("touchpad", "Touchpad", "touchpad|tap to click|natural scrolling|gesture touchpad|touchpad tidak berfungsi|touchpad tidak jalan|scroll terbalik|klik touchpad|trackpad", """
Settings → **Mouse & Touchpad**: aktifkan Tap to Click, Natural Scrolling, Two-finger scroll. Gestur 3-4 jari tersedia di GNOME Wayland; di desktop lain bisa dengan Touchegg. Jika touchpad mati total, cek tombol Fn untuk menyalakannya dan lihat `libinput list-devices` (paket `libinput-tools`)."""),
    T("battery", "Baterai dan daya laptop", "baterai boros|baterai cepat habis|hemat baterai|tlp|powertop|battery life|baterai laptop|thermald|umur baterai|batasi pengisian", """
Tips menghemat baterai:
```
sudo apt install tlp tlp-rdw        # manajemen daya otomatis
sudo systemctl enable --now tlp
sudo apt install powertop           # analisis konsumsi (jalankan: sudo powertop)
```
Di laptop Intel, `thermald` membantu suhu. Turunkan kecerahan layar, matikan Bluetooth yang tidak dipakai, dan periksa aplikasi yang boros di System Monitor. Pastikan driver GPU benar."""),
    T("suspend", "Sleep, hibernate, tutup laptop", "suspend|hibernate|sleep|tutup laptop|lid close|laptop tidak bisa sleep|tidak bangun dari sleep|resume gagal|hibernasi|layar tidak menyala setelah sleep", """
- Sleep dari menu daya atau `systemctl suspend`. Perilaku tutup laptop: Settings → Power.
- **Hibernate** butuh swap sedikitnya sebesar RAM dan konfigurasi resume; tidak aktif otomatis di semua distro.
- Jika gagal bangun dari sleep: update sistem/kernel dan driver GPU, coba kernel lain di GRUB, dan cek `journalctl -b -1 -p err`.
Sebutkan merek laptop dan distro untuk saran yang lebih tepat."""),
    T("autostart", "Aplikasi saat startup", "startup applications|aplikasi startup|autostart|jalankan saat login|jalankan saat boot|program otomatis jalan|hapus startup|tambah startup|jalankan skrip saat startup", """
- Mint: **Startup Applications**. GNOME: pasang 'GNOME Tweaks' → Startup Applications. KDE: System Settings → Autostart.
- Manual: letakkan file `.desktop` di `~/.config/autostart/`.
- Untuk layanan latar belakang: gunakan systemd (`systemctl enable nama`) atau `@reboot` di crontab.
Mengurangi aplikasi startup mempercepat login."""),
    T("desktop-entry", "Membuat launcher aplikasi (.desktop)", "buat launcher|membuat launcher|desktop entry|.desktop|shortcut aplikasi|tambah aplikasi ke menu|shortcut di desktop|buat shortcut aplikasi|appimage ke menu", """
Buat file `~/.local/share/applications/nama.desktop`:
```
[Desktop Entry]
Type=Application
Name=Nama Aplikasi
Exec=/path/lengkap/ke/aplikasi
Icon=/path/ke/ikon.png
Terminal=false
Categories=Utility;
```
Beri izin eksekusi (`chmod +x`), lalu aplikasi muncul di menu. Berguna untuk AppImage dan program hasil unduhan."""),
    T("default-apps", "Aplikasi default", "aplikasi default|default browser|browser default|ganti browser default|buka dengan|default app|set default|xdg-mime|file dibuka dengan", """
Settings → **Default Applications** (Mint/GNOME/KDE) untuk browser, email, pemutar media. Untuk satu file: klik kanan → Properties/Open With → pilih aplikasi → 'Set as default'. Lewat terminal: `xdg-mime default nama.desktop tipe/mime`."""),
    T("datetime", "Tanggal, jam, zona waktu", "ganti timezone|set timezone|zona waktu indonesia|wib|jam otomatis|sinkron jam|ntp|ubah jam|atur tanggal|ganti jam", """
Settings → **Date & Time** (aktifkan Automatic Date & Time). Terminal:
```
timedatectl
sudo timedatectl set-timezone Asia/Jakarta     # WIB; Asia/Makassar = WITA; Asia/Jayapura = WIT
sudo timedatectl set-ntp true
```
Jam berbeda di dual boot dengan Windows: tanya 'jam salah di dual boot'."""),
    T("lock-login", "Kunci layar, auto login", "kunci layar|lock screen|auto login|autologin|login otomatis|ganti layar login|lupa kunci layar|screen lock|timeout layar|layar mati sendiri", """
- Kunci layar: **Super+L**. Waktu layar mati dan kunci otomatis: Settings → Power dan Privacy/Screen Lock.
- Login otomatis: Settings → Users → Automatic Login (Mint: Login Window). Hindari di laptop yang dibawa-bawa."""),
    # ------------------------------------------------------------ jaringan
    T("hotspot", "Hotspot WiFi", "hotspot|tethering|bagikan internet|wifi hotspot|jadikan hotspot|share internet|tethering usb|tethering hp", """
- **Hotspot dari laptop**: Settings → Wi-Fi → menu ⋮ → Turn On Wi-Fi Hotspot. Butuh adapter yang mendukung mode AP.
- **Memakai internet HP lewat kabel USB**: aktifkan USB tethering di HP; biasanya langsung muncul sebagai koneksi kabel baru.
Berguna untuk memasang driver WiFi saat belum ada internet."""),
    T("static-ip-dns", "IP statis dan DNS", "ip statis|static ip|ganti dns|dns google|dns cloudflare|1.1.1.1|8.8.8.8|atur ip manual|ubah dns|dns lambat|ganti alamat ip", """
Settings → Network → ikon gear di koneksi → tab **IPv4**: pilih Manual untuk IP statis atau isi kolom DNS (misalnya 1.1.1.1 atau 8.8.8.8). Terminal:
```
nmcli connection show
nmcli connection modify "NamaKoneksi" ipv4.dns "1.1.1.1 8.8.8.8"
nmcli connection up "NamaKoneksi"
```
Salah IP manual bisa memutus internet; catat pengaturan lama dulu."""),
    T("samba", "Berbagi file dengan Windows (Samba)", "samba|smb|berbagi folder|share folder|akses folder windows|network share|folder sharing|share file ke windows|akses komputer windows|smb://", """
- **Mengakses folder Windows**: di file manager tekan Ctrl+L dan ketik `smb://IP-WINDOWS/NamaShare`.
- **Berbagi folder dari Linux**: `sudo apt install samba`, lalu klik kanan folder → Sharing Options (Nemo/Nautilus) dan beri izin; atau edit `/etc/samba/smb.conf` dan buat user Samba (`sudo smbpasswd -a namamu`).
Jika tidak terlihat: pastikan satu jaringan, firewall mengizinkan Samba, dan Windows memakai berbagi file yang aktif."""),
    T("hosts-proxy", "File hosts dan proxy", "file hosts|etc/hosts|edit hosts|proxy|setting proxy|proxy linux|blokir situs|http_proxy", """
- File hosts memetakan nama domain ke IP secara lokal: `sudo nano /etc/hosts` (contoh baris: `127.0.0.1 contoh.test`).
- Proxy: Settings → Network → Network Proxy; untuk terminal atur variabel `http_proxy`/`https_proxy`.
Hati-hati saat mengedit /etc/hosts; salah isi bisa membuat situs tertentu tidak bisa dibuka."""),
    # ------------------------------------------------------------ disk & file
    T("format-usb", "Memformat flashdisk", "format flashdisk|format usb|format flash disk|hapus isi usb|format disk|gnome disks|disks utility|format hardisk|format flashdisk exfat", """
Cara aman: aplikasi **Disks** (gnome-disks) atau klik kanan perangkat di file manager → Format.
1. Pilih perangkat yang benar (cek ukuran dan nama).
2. Pilih sistem berkas: **exFAT** (kompatibel Windows/Linux/macOS), FAT32 (maks. 4 GB per file), NTFS, atau ext4 (khusus Linux).
3. Konfirmasi. **Semua data akan terhapus.**
Salah memilih disk bisa menghapus data penting; cabut disk lain yang tidak perlu dulu."""),
    T("recover-files", "Mengembalikan file terhapus", "file terhapus|recover file|kembalikan file|data hilang|testdisk|photorec|undelete|recovery data|tidak sengaja hapus|trash|tempat sampah|recycle bin", """
- File yang dihapus lewat file manager ada di **Trash** (`~/.local/share/Trash/files`); klik kanan → Restore.
- `rm` menghapus permanen. **Segera berhenti memakai disk** agar data tidak tertimpa, lalu coba `testdisk`/`photorec` (`sudo apt install testdisk`), idealnya dari live USB atau disk lain.
Tidak ada jaminan berhasil. Karena itu buat backup rutin (tanya 'backup')."""),
    T("file-manager", "Tips file manager", "file manager|nautilus|nemo|dolphin|ganti nama file lewat gui|buka lokasi|ctrl+l|new document|template dokumen baru|klik kanan file baru", """
- **F2**: ganti nama. **Ctrl+H**: tampilkan file tersembunyi. **Ctrl+L**: ketik path manual. **Ctrl+Shift+N**: folder baru.
- Menu klik kanan 'New Document' kosong? Taruh file template di folder `~/Templates` (Nautilus/Nemo).
- Klik kanan folder → Open in Terminal untuk membuka terminal di lokasi itu.
Nama file manager: Nemo (Mint Cinnamon), Files/Nautilus (Ubuntu), Dolphin (KDE)."""),
    T("compress-gui", "Kompres dan ekstrak lewat GUI", "kompres file|ekstrak file|extract here|buat zip|compress zip|zip folder|ekstrak zip lewat gui|ekstrak arsip", """
Di file manager: klik kanan → **Compress** untuk membuat .zip/.tar.gz, atau **Extract Here** untuk mengekstrak. Untuk .rar dan .7z pasang `sudo apt install p7zip-full unrar`. Di terminal: tanya 'tar' atau 'zip'."""),
    T("run-script", "Menjalankan skrip .sh", "jalankan skrip|jalankan script|file sh|skrip bash|script.sh|jalankan sh|bash script|menjalankan file sh|buat skrip bash|membuat skrip", """
```
nano halo.sh                 # isi: baris pertama  #!/bin/bash  lalu  echo "Halo"
chmod +x halo.sh             # beri izin eksekusi
./halo.sh                    # jalankan (perhatikan ./)
bash halo.sh                 # alternatif tanpa chmod
```
Skrip dari Windows bisa bermasalah karena akhir baris CRLF (tanya 'bad interpreter' atau '^M'). Baca isi skrip sebelum menjalankannya, terutama yang meminta sudo."""),
    T("installed-apps", "Daftar aplikasi terpasang", "daftar aplikasi terpasang|aplikasi yang terinstal|apt list installed|lihat paket terpasang|cek versi aplikasi|versi paket|list installed|flatpak list|snap list", """
```
apt list --installed | less        # paket apt
apt policy nama-paket              # versi terpasang dan tersedia
flatpak list                       # aplikasi Flatpak
snap list                          # aplikasi Snap
nama-aplikasi --version            # versi program tertentu
```"""),
    T("cleanup", "Membersihkan sistem", "bersihkan sistem|bersihkan cache|bersihin linux|hapus cache|apt clean|hapus paket tidak terpakai|bleachbit|jurnal besar|vacuum|bebaskan ruang", """
```
sudo apt autoremove              # hapus dependensi tak terpakai
sudo apt clean                   # hapus cache paket
sudo journalctl --vacuum-time=7d # batasi log lama
flatpak uninstall --unused       # bersihkan runtime Flatpak
```
Cari penyebab ruang penuh dengan 'Disk Usage Analyzer' atau `du -h --max-depth=1 ~ | sort -h`. Hindari alat pembersih yang menghapus file sistem tanpa kamu pahami."""),
    T("upgrade-distro", "Upgrade versi distro", "upgrade versi|naik versi|upgrade ubuntu|upgrade mint|do-release-upgrade|upgrade ke versi baru|update ke ubuntu terbaru|upgrade linux mint|release upgrade", """
Naik versi besar sebaiknya setelah **backup** dan membuat snapshot Timeshift.
- **Ubuntu**: Software Updater akan menawarkan versi baru, atau `sudo do-release-upgrade`.
- **Linux Mint**: Update Manager → Edit → 'Upgrade to Linux Mint X'. Pantau pengumuman resmi di blog Mint.
- Pastikan semua update biasa sudah terpasang, ruang disk cukup, dan koneksi stabil.
Sebagian orang memilih instal bersih agar sistem lebih rapi; keduanya valid."""),
    T("kernel-change", "Ganti kernel", "ganti kernel|kernel lama|kernel baru|pilih kernel|boot kernel lama|kernel update|hapus kernel lama|downgrade kernel|install kernel", """
- Pilih kernel lama saat boot: di menu GRUB buka **Advanced options** dan pilih versi sebelumnya (berguna jika update kernel menimbulkan masalah).
- Linux Mint: Update Manager → View → Linux Kernels untuk memasang/menghapus kernel.
- Cek versi aktif: `uname -r`. Sisakan minimal satu kernel lama yang berfungsi sebagai cadangan."""),
    T("gparted", "Mengatur partisi (GParted)", "gparted|partisi disk|resize partisi|ubah ukuran partisi|buat partisi|gabung partisi|partition manager|partisi baru|kecilkan partisi|perbesar partisi", """
`sudo apt install gparted` lalu jalankan dari menu. Bisa mengubah ukuran, membuat, dan memformat partisi.
**Risiko:** salah langkah bisa menghapus data atau membuat OS tidak boot. Backup dulu, jangan putus listrik saat proses, dan jangan mengubah partisi yang sedang terpakai (gunakan live USB). Windows dengan BitLocker perlu dinonaktifkan dulu."""),
    T("zsh-shell", "Mengganti shell (zsh, fish)", "zsh|fish shell|oh my zsh|ohmyzsh|ganti shell|chsh|shell default|starship|prompt terminal|ganti prompt|powerlevel10k", """
Shell default biasanya bash. Mencoba shell lain:
```
sudo apt install zsh              # atau: fish
chsh -s $(which zsh)              # ganti shell default (logout/login ulang)
```
Framework seperti Oh My Zsh atau prompt Starship mempercantik terminal, tetapi memasangnya sering lewat skrip `curl | sh`; baca skripnya dulu dari situs resmi. Kembali ke bash: `chsh -s /bin/bash`."""),
    T("clipboard-cli", "Clipboard dari terminal", "xclip|wl-copy|wl-paste|xsel|salin ke clipboard|clipboard terminal|copy ke clipboard terminal|pbcopy", """
```
sudo apt install xclip wl-clipboard
cat file.txt | xclip -selection clipboard     # Xorg
cat file.txt | wl-copy                         # Wayland
wl-paste                                       # tempel isi clipboard
```"""),
    T("scanner", "Scanner", "scanner|pindai dokumen|simple-scan|sane|scan dokumen|pemindai", """
Pasang `sudo apt install simple-scan` (Document Scanner). Banyak scanner didukung lewat SANE; cek daftar di sane-project.org. Scanner multifungsi merek tertentu (HP: `hplip`, Epson: paket `iscan`/`epsonscan2`) membutuhkan driver dari produsen."""),
    T("old-laptop", "Laptop lama / spesifikasi rendah", "laptop lama|komputer lama|pc jadul|spesifikasi rendah|ram 2gb|ram 4gb|distro ringan|linux ringan|lubuntu|antix|laptop tua|menghidupkan laptop lama", """
Untuk perangkat lama pilih distro ringan: **Linux Mint Xfce**, **Lubuntu**, **Xubuntu**, atau antiX. Tips: pasang SSD jika masih memakai HDD, tambah RAM, pakai browser dengan sedikit tab, kurangi aplikasi startup, dan aktifkan zram. Cek spesifikasi dengan `lscpu` dan `free -h`."""),
    T("password-policy", "Password dan keamanan akun", "password kuat|ganti password sudo|password login|enkripsi disk|luks|enkripsi laptop|encrypt home|keamanan laptop|2fa|keyring", """
- Ganti password: `passwd`. Gunakan password panjang dan unik; pertimbangkan pengelola password (Bitwarden, KeePassXC).
- Enkripsi disk (LUKS) paling mudah dipilih **saat instalasi**; menambah belakangan lebih rumit. Melindungi data jika laptop hilang.
- Update rutin dan jangan menjalankan perintah/skrip tak dikenal sebagai root."""),
]
