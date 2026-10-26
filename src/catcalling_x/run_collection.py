import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from .config import load_settings
from .query_builder import load_keywords, build_query
from .client import XCookieClient, XApiClient, tweet_to_dict
from .storage import append_jsonl, normalize_post, export_csv

async def collect_with_cookies(client: XCookieClient, query: str, limit: int, product: str, delay: float, raw_path, processed_path):
    print(f"\n[+] Memulai scraping menggunakan session cookie...")
    print(f"[*] Target: {limit} tweet/komentar")
    print(f"[*] Query : {query}")
    print(f"[*] Mode  : {product}")
    print("-" * 60)

    seen_ids = set()
    normalized_rows = []
    total_new = 0

    def on_batch(new_items, current_total):
        nonlocal total_new
        collected_at = datetime.now(timezone.utc).isoformat()
        for t in new_items:
            t_dict = tweet_to_dict(t)
            append_jsonl(raw_path, {
                "query": query,
                "collected_at_utc": collected_at,
                "tweet": t_dict,
            })
            norm = normalize_post(t_dict, query=query, collected_at=collected_at)
            normalized_rows.append(norm)
            total_new += 1
            
            # Print preview snippet
            snippet = norm["text_raw"].replace("\n", " ")[:65]
            ctype = norm["content_type"]
            user = f"@{norm['username']}" if norm['username'] else "anon"
            print(f"[{total_new:2d}/{limit}] [{ctype:13}] {user:15} : {snippet}...")

    await client.collect_tweets(
        query=query,
        target_count=limit,
        product=product,
        delay=delay,
        on_batch=on_batch,
    )

    print("-" * 60)
    print(f"[✓] Selesai scraping batch! Berhasil mengumpulkan {len(normalized_rows)} postingan/komentar.")
    export_csv(normalized_rows, processed_path, merge_existing=True)
    return len(normalized_rows)

def main():
    parser = argparse.ArgumentParser(
        description="Scraper tweet & komentar X terkait fenomena Catcalling untuk analisis sentimen."
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=50,
        help="Jumlah tweet/komentar yang ingin di-scrape (default: 50)"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Query pencarian khusus. Contoh: 'catcalling' atau 'catcalling filter:replies'"
    )
    parser.add_argument(
        "--replies-only",
        action="store_true",
        help="Hanya scrape komentar/balasan (menambahkan filter:replies)"
    )
    parser.add_argument(
        "--product",
        choices=["Latest", "Top"],
        default="Latest",
        help="Urutan pencarian: 'Latest' (terbaru, default) atau 'Top' (terpopuler)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Jeda waktu antar halaman dalam detik (default: 2.0)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Lokasi file CSV output (default: data/processed/posts.csv)"
    )

    args = parser.parse_args()

    settings = load_settings()
    root = settings["_root"]
    cfg = settings.get("collection", {})
    
    raw_path = root / settings["storage"]["raw_jsonl"]
    processed_path = Path(args.output) if args.output else root / settings["storage"]["processed_csv"]

    # Determine query
    if args.query:
        query_str = args.query
        if args.replies_only and "filter:replies" not in query_str:
            query_str = f"{query_str} filter:replies"
    else:
        # Load keywords from file
        keywords_file = root / cfg.get("keywords_file", "config/keywords.txt")
        if keywords_file.exists():
            keywords = load_keywords(keywords_file)
            primary_kw = keywords[0] if keywords else "catcalling"
        else:
            primary_kw = "catcalling"
        query_str = build_query(primary_kw, replies_only=args.replies_only)

    auth_token = settings.get("_auth_token")
    ct0 = settings.get("_ct0")

    if auth_token and ct0:
        client = XCookieClient(auth_token, ct0)
        asyncio.run(collect_with_cookies(
            client=client,
            query=query_str,
            limit=args.limit,
            product=args.product,
            delay=args.delay,
            raw_path=raw_path,
            processed_path=processed_path,
        ))
    elif settings.get("_bearer_token"):
        print("[!] Menggunakan X API v2 Bearer Token...")
        # Fallback to official API client if needed
        api_client = XApiClient(settings["_bearer_token"], cfg["endpoint"])
        # Official endpoint logic
        collected_at = datetime.now(timezone.utc).isoformat()
        payload = api_client.search_page(query=query_str, start_time="2025-01-01T00:00:00Z", end_time=collected_at, max_results=min(100, args.limit))
        posts = payload.get("data", [])
        norm_rows = [normalize_post(p, query=query_str, collected_at=collected_at) for p in posts]
        export_csv(norm_rows, processed_path, merge_existing=True)
    else:
        raise RuntimeError("Kredensial X tidak ditemukan di .env!")

if __name__ == "__main__":
    main()
