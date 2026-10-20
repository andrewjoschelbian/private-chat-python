# Chat Private — Server & Client

Chat room sederhana berbasis Python. Hanya orang yang **punya script ini + tahu password room** yang bisa masuk dan chat. Jalan di **Linux & Windows**, tanpa install apa pun (murni Python stdlib).

---

## File dalam paket ini

| File | Fungsi |
|---|---|
| `chat_server.py` | Server — dijalankan **sekali**, menunggu client masuk |
| `chat_client.py` | Client — dipakai oleh tiap orang yang mau chat |

---

## Cara Pakai

### A. Test di satu komputer (paling cepat)

**Terminal 1** — jalankan server:
```bash
python3 chat_server.py -p 5555 --password "Rahasia123"
```

**Terminal 2** — jalankan client:
```bash
python3 chat_client.py -s 127.0.0.1 -p 5555 -n andrew
```
> `127.0.0.1` artinya "komputer ini sendiri". Password akan ditanya saat join — ketik `Rahasia123` (tidak tampil di layar saat diketik, itu normal).

Buka terminal 3 untuk client kedua, dan seterusnya.

### B. Antar komputer dalam satu WiFi/jaringan

**Langkah 1 — di komputer server**, cari tahu IP lokalnya:

- **Linux**:
  ```bash
  hostname -I
  ```
- **Windows** (CMD):
  ```cmd
  ipconfig
  ```
  Lihat bagian `IPv4 Address`, misal hasilnya `192.168.1.10`.

**Langkah 2 — di komputer yang sama**, jalankan server:
```bash
python3 chat_server.py -p 5555 --password "Rahasia123"
```

**Langkah 3 — di komputer client lain**, sambung ke IP server:
```bash
python3 chat_client.py -s 192.168.1.10 -p 5555 -n budi
```
Ganti `192.168.1.10` dengan IP yang kamu dapat di Langkah 1.

---

## Perintah di Dalam Chat

Ketik di jendela client lalu Enter:

| Perintah | Hasil |
|---|---|
| `/who` | tampilkan daftar user yang online |
| `/me <aksi>` | pesan aksi — contoh: `/me ngantuk` muncul sebagai `* budi ngantuk` |
| `/quit` | keluar dari chat |

Semua teks biasa akan dikirim ke semua orang yang online.

---

## Semua Opsi Perintah

### Server (`chat_server.py`)
```bash
python3 chat_server.py                    # default: port 5555, bind 0.0.0.0
python3 chat_server.py -p 9000            # ganti port
python3 chat_server.py -b 127.0.0.1       # hanya terima koneksi dari komputer sendiri
python3 chat_server.py --password "kuat"  # GANTI password sebelum dipakai beneran!
```
| Opsi | Default | Fungsi |
|---|---|---|
| `-p` | `5555` | port listening |
| `-b` | `0.0.0.0` | alamat bind (`0.0.0.0` = terima dari jaringan mana pun) |
| `--password` | `RAHASIA123` | password room — **wajib diganti** |

### Client (`chat_client.py`)
```bash
python3 chat_client.py -s 192.168.1.10 -p 5555 -n andrew --password "Rahasia123"
```
| Opsi | Wajib? | Fungsi |
|---|---|---|
| `-s` | ya | IP/domain server |
| `-p` | tidak | port (default `5555`, harus sama dengan server) |
| `-n` | ya | nickname kamu (unik, tidak boleh sama dengan user lain) |
| `--password` | tidak | password room; kalau di-skip, client menanyakannya dengan aman |

---

## Aturan Main

- **Nickname unik** — kalau ada yang pakai nama sama, client baru ditolak.
- **Password salah = langsung ditolak** dan dicatat di log server.
- User keluar/join terlihat oleh semua orang (`* andrew keluar dari chat`).

---

## Cara Kerja Singkat (untuk belajar)

```
client ──"PASS <password> <nick>"──▶ server
         ◀──"OK ..." atau "REJECT ..."──
client ──────"[14:20] andrew: halo"─────▶ server ──broadcast──▶ semua client lain
```

Server memakai threading: setiap client ditangani thread sendiri, jadi satu orang disconnect tidak mengganggu yang lain.

---

## Troubleshooting

| Masalah | Penyebab & Solusi |
|---|---|
| `Gagal konek ke ...` | Server belum jalan, IP salah, atau beda jaringan. Pastikan server sudah nyala dulu, lalu cek IP-nya lagi |
| `Ditolak server: Password salah` | Password client berbeda dengan `--password` di server. Samakan keduanya |
| `Ditolak server: Nickname sudah dipakai` | Ganti `-n` dengan nama lain |
| Komputer lain tidak bisa connect | Firewall block port (coba matikan firewall sebentar untuk test), atau server bind `127.0.0.1` saja — pakai `-b 0.0.0.0` |
| `python3` tidak dikenal (Windows) | Coba `py` atau `python` |
| Password ketik tidak kelihatan | Memang sengaja (mode getpass), ketik saja lalu Enter |

---

## Keamanan

- Koneksi **plaintext** — jangan lewatkan data sensitif, dan **jangan expose ke internet** tanpa perlindungan. Untuk jarak jauh, pakai SSH tunnel atau Tailscale.
- Ganti password default sebelum dipakai, dan jangan pakai ulang password dari akun lain.
- Jangan pernah jalankan server chat dari sumber yang tidak kamu percaya tanpa baca kodenya dulu.

---

## Requirement

- Python 3.8+ — cek dengan `python3 --version`
- Tidak perlu `pip install` sama sekali.
