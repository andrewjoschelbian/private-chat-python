#!/usr/bin/env python3
"""
chat_client.py — Client chat private (Linux/Windows).
Hanya bisa masuk jika tahu password room + pakai script ini.

Usage:
  python3 chat_client.py -s <IP_SERVER> [-p 5555] -n Nickname
  python3 chat_client.py -s 192.168.1.5 -n andrew
"""

import argparse
import socket
import sys
import threading


def receiver(conn):
    """Thread terpisah: baca pesan dari server, tampilkan ke layar."""
    while True:
        try:
            data = conn.recv(4096)
        except OSError:
            break
        if not data:
            print("\n[!] Terputus dari server.")
            break
        sys.stdout.write("\r" + data.decode(errors="replace"))
        sys.stdout.write("> ")
        sys.stdout.flush()
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--server", required=True, help="IP/domain server")
    ap.add_argument("-p", "--port", type=int, default=5555)
    ap.add_argument("-n", "--nick", required=True, help="nickname kamu")
    ap.add_argument("--password", default=None,
                    help="password room (kalau tidak diisi akan ditanya)")
    args = ap.parse_args()

    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("Password room: ")

    try:
        conn = socket.create_connection((args.server, args.port), timeout=10)
    except OSError as e:
        print(f"[!] Gagal konek ke {args.server}:{args.port} — {e}")
        sys.exit(1)

    # handshake: kirim PASS <password> <nick>
    conn.sendall(f"PASS {password} {args.nick}\n".encode())
    resp = conn.recv(512).decode(errors="replace")
    if resp.startswith("REJECT"):
        print(f"[!] Ditolak server: {resp[7:].strip()}")
        conn.close()
        sys.exit(1)
    print(resp[3:].strip())

    threading.Thread(target=receiver, args=(conn,), daemon=True).start()

    print("Ketik pesan lalu Enter. Perintah: /who  /me <aksi>  /quit\n")
    try:
        while True:
            msg = input("> ").strip()
            if msg:
                conn.sendall((msg + "\n").encode())
                if msg == "/quit":
                    break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        conn.close()


if __name__ == "__main__":
    main()
