"""
scraper.py — General-purpose web scraper with scheduled runs
Author: Atharva (@thragg-codes)
Project 4 / 10 — 30 Days Portfolio Challenge
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib
from datetime import datetime


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str, timeout: int = 10) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None


def extract(soup: BeautifulSoup, selectors: dict) -> dict:
    result = {}
    for field, selector in selectors.items():
        elements = soup.select(selector)
        values = [el.get_text(strip=True) for el in elements]
        result[field] = values if len(values) != 1 else values[0]
    return result


def scrape(url: str, selectors: dict) -> dict:
    print(f"  [SCRAPE] {url}")
    soup = fetch_page(url)
    if not soup:
        return {"url": url, "error": "fetch_failed", "timestamp": datetime.now().isoformat()}
    data = extract(soup, selectors)
    return {"url": url, "timestamp": datetime.now().isoformat(), "data": data}


def save_json(record: dict, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    url_hash = hashlib.md5(record["url"].encode()).hexdigest()[:8]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"{url_hash}_{ts}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"  [SAVED]  {filepath}")
    return filepath


def run_once(jobs: list, output_dir: str = "output") -> list:
    results = []
    for job in jobs:
        record = scrape(job["url"], job["selectors"])
        save_json(record, output_dir)
        results.append(record)
    return results


def run_scheduled(jobs: list, interval: int, output_dir: str = "output"):
    run = 1
    try:
        while True:
            print(f"\n{'='*50}")
            print(f"  Run #{run} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            run_once(jobs, output_dir)
            print(f"\n  [WAIT] Next run in {interval}s — Ctrl+C to stop.")
            time.sleep(interval)
            run += 1
    except KeyboardInterrupt:
        print("\n\n  [STOPPED] Scheduler interrupted by user.")
