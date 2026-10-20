#!/usr/bin/env python3
"""
chat_server.py — Server chat private (Linux/Windows).
Hanya client yang punya PASSWORD room yang bisa masuk.

Usage:
  python3 chat_server.py                 # default port 5555
  python3 chat_server.py -p 9000         # port custom
  python3 chat_server.py -b 0.0.0.0      # akses dari LAN/internet
"""

import argparse
import socket
import threading
import time

clients = {}          # socket -> {"nick": str, "addr": tuple}
lock = threading.Lock()

def broadcast(msg, sender=None):
    with lock:
        targets = [s for s in clients if s is not sender]
    dead = []
    for s in targets:
        try:
            s.sendall(msg.encode())
        except OSError:
            dead.append(s)
    for s in dead:
        remove_client(s)

def remove_client(s):
    with lock:
        info = clients.pop(s, None)
    if info:
        print(f"[-] {info['nick']} ({info['addr'][0]}) keluar")
        broadcast(f"* {info['nick']} keluar dari chat\n")

def handle_client(conn, addr, password):
    try:
        conn.settimeout(30)
        # handshake: PASS <password> <nick>
        raw = conn.recv(512).decode(errors="replace").strip()
        parts = raw.split(" ", 2)
        if len(parts) < 3 or parts[0] != "PASS" or parts[1] != password:
            conn.sendall(b"REJECT Password salah atau format salah.\n")
            conn.close()
            print(f"[!] Koneksi ditolak dari {addr[0]} (auth gagal)")
            return
        nick = parts[2][:20] or "anon"
        with lock:
            if any(v["nick"] == nick for v in clients.values()):
                conn.sendall(b"REJECT Nickname sudah dipakai.\n")
                conn.close()
                return
            clients[conn] = {"nick": nick, "addr": addr}
        conn.settimeout(None)
        conn.sendall(f"OK Selamat datang, {nick}! ({len(clients)} user online)\n".encode())
        print(f"[+] {nick} join dari {addr[0]} ({len(clients)} online)")
        broadcast(f"* {nick} bergabung ({len(clients)} online)\n", sender=conn)
        buf = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode(errors="replace").strip()
                if not text:
                    continue
                if text.startswith("/"):
                    cmd = text.split(" ", 1)[0]
                    if cmd == "/quit":
                        raise ConnectionResetError
                    elif cmd == "/who":
                        with lock:
                            nicks = ", ".join(v["nick"] for v in clients.values())
                        conn.sendall(f"* Online: {nicks}\n".encode())
                    elif cmd == "/me":
                        act = text[4:].strip()
                        if act:
                            broadcast(f"* {nick} {act}\n")
                    else:
                        conn.sendall(b"* Perintah: /who /me <aksi> /quit\n")
                else:
                    stamp = time.strftime("%H:%M")
                    broadcast(f"[{stamp}] {nick}: {text}\n")
    except (ConnectionResetError, OSError):
        pass
    finally:
        remove_client(conn)
        conn.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", type=int, default=5555)
    ap.add_argument("-b", "--bind", default="0.0.0.0")
    ap.add_argument("--password", default="RAHASIA123",
                    help="password room — GANTI sebelum dipakai!")
    args = ap.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.bind, args.port))
    srv.listen(20)
    print(rf"""
  ___  _   _ _   _ ____  _____
 / __|| | | | \ | |  _ \| ____|
| |   | |_| |  \| | | | |  _|
| |___|  _  | |\  | |_| | |___
 \____|_| |_|_| \_|____/|_____|
 chat_server v1.0 — private room
[*] Listening di {args.bind}:{args.port}
[*] Password room : {args.password}
[*] Ctrl+C untuk stop.
""")

    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client, args=(conn, addr, args.password), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[*] Server dihentikan.")
        srv.close()

if __name__ == "__main__":
    main()
