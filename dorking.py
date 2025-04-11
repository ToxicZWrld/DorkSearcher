#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import time
import sys
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import socks  # for SOCKS5 proxy support
except ImportError:
    print("[!] Missing 'requests[socks]'. Install with: pip install requests[socks] beautifulsoup4")
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

class Colors:
    RED = "\033[91m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def logger(file, data):
    with open(file, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def get_proxies_from_all_sources():
    print(f"{Colors.BLUE}[INFO] Collecting proxies from all sources...{Colors.RESET}")
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
    except Exception as e:
        print(f"{Colors.RED}[ERROR] GeoNode failed: {e}{Colors.RESET}")

    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            lines = res.text.strip().splitlines()
            for line in lines:
                line = line.strip()
                if not line or not re.match(r"^\d{1,3}(\.\d{1,3}){3}:\d+$", line.split('@')[-1]):
                    continue
                proto = "http"
                if "socks5" in url:
                    proto = "socks5"
                elif "https" in url:
                    proto = "https"
                proxies.add(f"{proto}://{line}")
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed fetching {url}: {e}{Colors.RESET}")
    print(f"{Colors.GREEN}[INFO] Total collected proxies: {len(proxies)}{Colors.RESET}")
    return list(proxies)

def validate_proxies(proxy_list, max_good=30, threads=50):
    print(f"{Colors.BLUE}[INFO] Validating proxies with {threads} threads...{Colors.RESET}")
    working = []

    def test_proxy(proxy):
        proxies = {"http": proxy, "https": proxy}
        try:
            r = requests.get("https://duckduckgo.com", headers=HEADERS, proxies=proxies, timeout=6)
            if r.status_code == 200:
                print(f"{Colors.GREEN}[VALID] {proxy}{Colors.RESET}")
                return proxy
        except:
            print(f"{Colors.RED}[BAD] {proxy}{Colors.RESET}")
        return None

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(test_proxy, p): p for p in proxy_list}
        for future in as_completed(futures):
            result = future.result()
            if result:
                working.append(result)
            if len(working) >= max_good:
                break

    print(f"{Colors.GREEN}[INFO] Working proxies: {len(working)}{Colors.RESET}")
    return working

def dork_search(query, pages, proxy_pool, save=False, filename="results.txt"):
    base_url = "https://html.duckduckgo.com/html/"
    total = 0
    session = requests.Session()

    for page in range(pages):
        proxy = random.choice(proxy_pool)
        print(f"{Colors.YELLOW}[INFO] Using proxy: {proxy}{Colors.RESET}")
        params = {"q": query, "s": str(page * 50)}

        try:
            r = session.post(base_url, data=params, headers=HEADERS, proxies={"http": proxy, "https": proxy}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a", {"class": "result__url"})

            if not links:
                print(f"{Colors.RED}[!] No results or blocked.{Colors.RESET}")
                continue

            for link in links:
                href = link.get("href")
                if href:
                    print(f"{Colors.GREEN}[+] {href}{Colors.RESET}")
                    if save:
                        logger(filename, href)
                    total += 1
            time.sleep(random.uniform(1.5, 3.5))
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Proxy failed: {e}{Colors.RESET}")
            continue
    print(f"{Colors.BLUE}\n[✔] Total dorks fetched: {total}{Colors.RESET}")

if __name__ == "__main__":
    print(f"{Colors.BLUE}[+] DORK SWARM - DuckDuckGo + Multi-Proxy + Threads{Colors.RESET}")
    query = input(f"{Colors.YELLOW}[?] Dork query: {Colors.RESET}")
    pages = int(input(f"{Colors.YELLOW}[?] Pages to search: {Colors.RESET}"))

    try:
        thread_count = int(input(f"{Colors.YELLOW}[?] Threads for proxy validation (50-200 recommended): {Colors.RESET}"))
    except:
        thread_count = 50

    save_opt = input(f"{Colors.YELLOW}[?] Save results to file? (y/n): {Colors.RESET}").lower()
    save = save_opt == "y"
    filename = "results.txt"
    if save:
        filename = input(f"{Colors.YELLOW}[?] Filename: {Colors.RESET}").strip()
        if not filename.endswith(".txt"):
            filename += ".txt"

    raw_proxies = get_proxies_from_all_sources()
    valid_proxies = validate_proxies(raw_proxies, threads=thread_count)

    if not valid_proxies:
        print(f"{Colors.RED}[FATAL] No working proxies found. Exiting.{Colors.RESET}")
        sys.exit(1)

    dork_search(query, pages, valid_proxies, save, filename)
