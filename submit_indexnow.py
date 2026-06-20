#!/usr/bin/env python3
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

HOST = "btwgame.com"
KEY_FILE = Path("indexnow_key.txt")
STATIC_DIR = Path("static_html")
SITEMAP_FILE = STATIC_DIR / "sitemap.xml"
BING_INDEXNOW_ENDPOINT = "https://www.bing.com/indexnow"
MAX_URLS_PER_REQUEST = 10000


def read_key():
    if not KEY_FILE.exists():
        raise FileNotFoundError(f"Missing {KEY_FILE}. Create it with a valid IndexNow key.")
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"{KEY_FILE} is empty.")
    return key


def write_key_location(key):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    key_location = STATIC_DIR / f"{key}.txt"
    key_location.write_text(key + "\n", encoding="utf-8")
    return key_location


def normalize_url(url):
    url = url.strip()
    if not url:
        return ""
    if url.startswith("/"):
        return f"https://{HOST}{url}"
    return url


def read_sitemap_urls(path):
    tree = ET.parse(path)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        loc.text.strip()
        for loc in tree.findall(".//sm:loc", namespace)
        if loc.text and loc.text.strip()
    ]
    if not urls:
        urls = [
            loc.text.strip()
            for loc in tree.findall(".//loc")
            if loc.text and loc.text.strip()
        ]
    return urls


def dedupe_urls(urls):
    seen = set()
    clean_urls = []
    for url in urls:
        normalized = normalize_url(url)
        if not normalized or normalized in seen:
            continue
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        if parsed.netloc != HOST:
            raise ValueError(f"URL host must be {HOST}: {url}")
        clean_urls.append(normalized)
        seen.add(normalized)
    return clean_urls


def chunked(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]


def submit_batch(urls, key, endpoint, timeout):
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "BTW-game-IndexNow/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


def main():
    parser = argparse.ArgumentParser(description="Submit BTW game URLs to Bing IndexNow.")
    parser.add_argument("--sitemap", default=str(SITEMAP_FILE), help="XML sitemap path to read URLs from.")
    parser.add_argument("--url", action="append", default=[], help="URL or path to submit. Repeat for multiple URLs.")
    parser.add_argument("--limit", type=int, help="Submit only the first N URLs, useful for smoke tests.")
    parser.add_argument("--endpoint", default=BING_INDEXNOW_ENDPOINT, help="IndexNow endpoint URL.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between batches.")
    parser.add_argument("--submit", action="store_true", help="Actually send requests. Without this, run in dry-run mode.")
    args = parser.parse_args()

    key = read_key()
    key_location = write_key_location(key)

    if args.url:
        urls = dedupe_urls(args.url)
    else:
        sitemap_path = Path(args.sitemap)
        if not sitemap_path.exists():
            raise FileNotFoundError(f"Missing sitemap file: {sitemap_path}")
        urls = dedupe_urls(read_sitemap_urls(sitemap_path))

    if args.limit is not None:
        urls = urls[:args.limit]

    print(f"IndexNow key file: {key_location}")
    print(f"Endpoint: {args.endpoint}")
    print(f"URLs: {len(urls)}")

    if not urls:
        print("No URLs to submit.")
        return 0

    if not args.submit:
        print("Dry run only. Add --submit to send to Bing IndexNow.")
        print("Sample URLs:")
        for url in urls[:10]:
            print(f"  {url}")
        return 0

    failed = []
    for batch_index, batch in enumerate(chunked(urls, MAX_URLS_PER_REQUEST), start=1):
        status, body = submit_batch(batch, key, args.endpoint, args.timeout)
        print(f"Batch {batch_index}: {len(batch)} URLs -> HTTP {status}")
        if body:
            print(body[:500])
        if status not in {200, 202}:
            failed.append((batch_index, status, body[:500]))
        if args.sleep and batch_index * MAX_URLS_PER_REQUEST < len(urls):
            time.sleep(args.sleep)

    if failed:
        print("IndexNow submission failed for one or more batches:", file=sys.stderr)
        for batch_index, status, body in failed:
            print(f"  batch={batch_index} status={status} body={body}", file=sys.stderr)
        return 1

    print("IndexNow submission completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
