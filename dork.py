#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import time
import sys
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import socks
except ImportError:
    print("\033[91m[!] Missing 'requests[socks]'. Install with: pip install requests[socks] beautifulsoup4\033[0m")
    sys.exit(1)

Vermelho = '\033[91m'
Verde = '\033[92m'
Amarelo = '\033[93m'
Azul = '\033[94m'
Reset = '\033[0m'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def logger(file, data):
    with open(file, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def get_proxies_from_all_sources():
    urls = [
        "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text",
        "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
        "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/All_proxies.txt",
        "https://vakhov.github.io/fresh-proxy-list/https.txt",
        "https://vakhov.github.io/fresh-proxy-list/socks5.txt"
    ]
    proxies = set()
    try:
        geo = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc").json()
        for p in geo.get("data", []):
            ip = p.get("ip")
            port = p.get("port")
            proto = p.get("protocols", ["http"])[0]
            if ip and port:
                proxies.add(f"{proto}://{ip}:{port}")
    except: pass
    for url in urls:
        try:
            res = requests.get(url, timeout=8)
            lines = res.text.strip().splitlines()
            for line in lines:
                line = line.strip()
                if not line or not re.match(r"^\d{1,3}(\.\d{1,3}){3}:\d+$", line.split('@')[-1]):
                    continue
                proto = "http"
                if "socks5" in url: proto = "socks5"
                elif "https" in url: proto = "https"
                proxies.add(f"{proto}://{line}")
        except: pass
    return list(proxies)

def validate_proxies(proxy_list, max_good=30, threads=50):
    working = []
    def test_proxy(proxy):
        proxies = {"http": proxy, "https": proxy}
        try:
            r = requests.get("https://duckduckgo.com", headers=HEADERS, proxies=proxies, timeout=5)
            if r.status_code == 200:
                return proxy
        except: pass
        return None
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(test_proxy, p): p for p in proxy_list}
        for future in as_completed(futures):
            result = future.result()
            if result:
                working.append(result)
            if len(working) >= max_good:
                break
    return working

def dork_search(query, pages, proxy_pool, save=False, filename="results.txt"):
    base_url = "https://html.duckduckgo.com/html/"
    session = requests.Session()
    seen_links = set()
    proxy_index = 0
    for page in range(pages):
        proxy = proxy_pool[proxy_index % len(proxy_pool)]
        proxy_index += 1
        params = {"q": query, "s": str(page * 50)}
        try:
            response = session.post(base_url, data=params, headers=HEADERS, proxies={"http": proxy, "https": proxy}, timeout=4)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="result__url")
            for link in links:
                href = link.get("href")
                if href and href not in seen_links:
                    seen_links.add(href)
                    print(f"{Verde}[+]{Reset} {href}")
                    if save:
                        logger(filename, href)
            time.sleep(random.uniform(0.4, 1.0))
        except Exception:
            continue

if __name__ == "__main__":
    mode = input(f"{Azul}[?]{Reset} Modo (1 = dork única | 2 = arquivo de dorks): ")
    dorks = []
    if mode == "1":
        query = input(f"{Azul}[?]{Reset} Digite sua dork: ")
        dorks.append(query)
    elif mode == "2":
        file_path = input(f"{Azul}[?]{Reset} Nome do arquivo de dorks (.txt): ").strip()
        if Path(file_path).is_file():
            with open(file_path, "r", encoding="utf-8") as f:
                dorks = [line.strip() for line in f if line.strip()]
        else:
            print(f"{Vermelho}[!] Arquivo não encontrado: {file_path}{Reset}")
            sys.exit(1)
    else:
        print(f"{Vermelho}[!] Modo inválido.{Reset}")
        sys.exit(1)

    pages = int(input(f"{Azul}[?]{Reset} Quantas páginas por dork? "))
    threads = int(input(f"{Azul}[?]{Reset} Threads para verificação de proxies: "))
    save = input(f"{Azul}[?]{Reset} Deseja salvar os resultados? (s/n): ").lower() == "s"
    filename = "results.txt"
    if save:
        filename = input(f"{Azul}[?]{Reset} Nome do arquivo de saída: ")
        if not filename.endswith(".txt"):
            filename += ".txt"

    print(f"{Amarelo}[*]{Reset} Coletando proxies...")
    raw_proxies = get_proxies_from_all_sources()
    print(f"{Amarelo}[*]{Reset} Verificando proxies válidos...")
    valid_proxies = validate_proxies(raw_proxies, threads=threads)

    if not valid_proxies:
        print(f"{Vermelho}[!] Nenhum proxy válido encontrado.{Reset}")
        sys.exit(1)

    for dork in dorks:
        print(f"{Azul}[*]{Reset} Buscando: {dork}")
        dork_search(dork, pages, valid_proxies, save, filename)

