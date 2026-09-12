"""
02_resolver.py — Multi-strategy Google News URL Resolver
GRAK 2026 · Sprint 3

MASALAH:
  Google News RSS memberikan URL dalam format:
    https://news.google.com/rss/articles/CBMi...
  
  URL ini adalah encoded redirect. Untuk mendapatkan URL berita asli,
  kita perlu "decode" atau "resolve" URL tersebut.

STRATEGI (waterfall — coba satu per satu sampai berhasil):
  1. googlenewsdecoder library
  2. HTTP HEAD follow redirect
  3. HTTP GET follow redirect  
  4. HTML meta-refresh tag parse

CARA PAKAI:
  python3 02_resolver.py
  python3 02_resolver.py --limit 5   # Smoke test mode

INPUT:
  → data/discovery_articles.csv (dari 01_discovery.py)

OUTPUT:
  → data/resolved_urls.csv (URL asli + domain + method resolver)
  → data/resolve_failed.csv (URL yang tetap gagal setelah semua strategi)

PRASYARAT:
  pip install googlenewsdecoder requests beautifulsoup4 pandas tqdm
"""

import os
import sys
import re
import time
import argparse
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, DISCOVERY_CSV
from lib.http_client import RateLimitedClient
from lib.logger import get_logger

# Output files
RESOLVED_CSV = os.path.join(DATA_DIR, "resolved_urls.csv")
RESOLVE_FAILED_CSV = os.path.join(DATA_DIR, "resolve_failed.csv")

# Logger
log = get_logger("02_resolver")

# HTTP Client (shared, thread-safe)
http = RateLimitedClient(timeout=15, max_retries=2)

# Import googlenewsdecoder (opsional)
try:
    from googlenewsdecoder import gnewsdecoder
    HAS_GNEWS = True
except ImportError:
    HAS_GNEWS = False
    log.warning("googlenewsdecoder not installed, skipping strategy 1")


def is_google_news_url(url: str) -> bool:
    """Cek apakah URL masih link Google News yang perlu di-resolve."""
    return "news.google.com" in url


def extract_domain(url: str) -> str:
    """Ambil nama domain bersih dari URL."""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return "unknown"


def strategy_1_gnewsdecoder(url: str) -> str | None:
    """
    Strategy 1: Pakai googlenewsdecoder library.
    Paling cepat tapi sering gagal.
    """
    if not HAS_GNEWS:
        return None
    try:
        result = gnewsdecoder(url)
        if result.get("status") and result.get("decoded_url"):
            decoded = result["decoded_url"]
            if not is_google_news_url(decoded):
                return decoded
    except Exception:
        pass
    return None


def strategy_2_head_redirect(url: str) -> str | None:
    """
    Strategy 2: HTTP HEAD dan follow redirect chain.
    Lebih cepat dari GET karena tidak download body.
    """
    try:
        response = http.head(url, allow_redirects=True)
        if response and not is_google_news_url(response.url):
            return response.url
    except Exception:
        pass
    return None


def strategy_3_get_redirect(url: str) -> str | None:
    """
    Strategy 3: HTTP GET dan follow redirect chain.
    Download full body tapi lebih reliable dari HEAD.
    """
    try:
        response = http.get(url, allow_redirects=True)
        if response and not is_google_news_url(response.url):
            return response.url
    except Exception:
        pass
    return None


def strategy_4_meta_refresh(url: str) -> str | None:
    """
    Strategy 4: Parse HTML body untuk cari <meta http-equiv="refresh">.
    Beberapa redirect Google News pakai meta refresh tag.
    
    Contoh:
    <meta http-equiv="refresh" content="0;url=https://real-news.com/article/123">
    """
    try:
        response = http.get(url, allow_redirects=False)
        if response is None:
            return None
        
        html = response.text[:5000]  # Hanya parse awal, hemat memory
        
        # Cari meta refresh
        match = re.search(
            r'<meta[^>]*http-equiv=["\']?refresh["\']?[^>]*content=["\']?\d+;\s*url=([^"\'>\s]+)',
            html,
            re.IGNORECASE
        )
        if match:
            target_url = match.group(1)
            if not is_google_news_url(target_url):
                return target_url
        
        # Cari JavaScript redirect
        match = re.search(
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        if match:
            target_url = match.group(1)
            if not is_google_news_url(target_url) and target_url.startswith("http"):
                return target_url
                
    except Exception:
        pass
    return None


def resolve_single_url(row: dict) -> dict:
    """
    Resolve satu URL melalui 4 strategi waterfall.
    
    Args:
        row: dict dari DataFrame discovery (harus punya key 'url')
    
    Returns:
        dict dengan key tambahan: resolved_url, resolved_domain, resolver_method, resolve_status
    """
    raw_url = row["url"]
    result = dict(row)  # Copy semua field asli
    
    # Jika bukan Google News URL, langsung return (sudah resolved)
    if not is_google_news_url(raw_url):
        result["resolved_url"] = raw_url
        result["resolved_domain"] = extract_domain(raw_url)
        result["resolver_method"] = "already_resolved"
        result["resolve_status"] = "success"
        return result
    
    # Coba 4 strategi berurutan
    strategies = [
        ("gnewsdecoder", strategy_1_gnewsdecoder),
        ("head_redirect", strategy_2_head_redirect),
        ("get_redirect", strategy_3_get_redirect),
        ("meta_refresh", strategy_4_meta_refresh),
    ]
    
    for method_name, strategy_fn in strategies:
        resolved = strategy_fn(raw_url)
        if resolved:
            result["resolved_url"] = resolved
            result["resolved_domain"] = extract_domain(resolved)
            result["resolver_method"] = method_name
            result["resolve_status"] = "success"
            log.debug(
                f"Resolved via {method_name}",
                raw_url=raw_url[:80],
                resolved=resolved[:80],
            )
            return result
    
    # Semua strategi gagal
    result["resolved_url"] = raw_url  # Tetap simpan URL asli
    result["resolved_domain"] = "news.google.com"
    result["resolver_method"] = "none"
    result["resolve_status"] = "failed"
    log.warning("All strategies failed", raw_url=raw_url[:80])
    return result


def main():
    parser = argparse.ArgumentParser(description="Multi-strategy Google News URL Resolver")
    parser.add_argument("--limit", type=int, default=None, help="Limit jumlah URL yang diproses (misal untuk smoke test)")
    parser.add_argument("--workers", type=int, default=5, help="Jumlah thread paralel (default: 5)")
    parser.add_argument("--input", type=str, default=DISCOVERY_CSV, help="File input discovery CSV")
    parser.add_argument("--output", type=str, default=RESOLVED_CSV, help="File output resolved CSV")
    args, _ = parser.parse_known_args()

    input_csv = args.input
    output_resolved_csv = args.output
    output_failed_csv = RESOLVE_FAILED_CSV if output_resolved_csv == RESOLVED_CSV else os.path.join(os.path.dirname(output_resolved_csv), "resolve_failed.csv")

    # ===== Load Discovery CSV =====
    if not os.path.exists(input_csv):
        print(f"❌ File tidak ditemukan: {input_csv}")
        print("   Jalankan 01_discovery.py terlebih dahulu!")
        return
    
    df = pd.read_csv(input_csv)
    if args.limit and args.limit > 0:
        df = df.head(args.limit).copy()

    total = len(df)
    
    # Hitung berapa yang perlu di-resolve
    needs_resolve = df["url"].apply(is_google_news_url).sum()
    already_ok = total - needs_resolve
    
    print("=" * 65)
    print("🔗 URL RESOLVER — Multi-Strategy Google News URL Decoder")
    print(f"   • Total URL           : {total}")
    print(f"   • Perlu resolve       : {needs_resolve} (Google News URLs)")
    print(f"   • Sudah OK            : {already_ok} (URL langsung)")
    print(f"   • Google News Decoder : {'✅ AKTIF' if HAS_GNEWS else '⚠️ TIDAK ADA'}")
    print(f"   • Max workers         : {args.workers} threads")
    if args.limit:
        print(f"   • Mode                : 🧪 Smoke test / Limited ({args.limit} URLs)")
    print("=" * 65)
    print()
    
    log.info(
        "Starting URL resolution",
        total=total,
        needs_resolve=needs_resolve,
    )
    
    # ===== Resolve URLs dengan ThreadPoolExecutor =====
    items = df.to_dict(orient="records")
    results = []
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(resolve_single_url, item): item for item in items}
        
        with tqdm(total=total, desc="Resolving URLs", unit="url", ncols=85) as pbar:
            success_count = 0
            fail_count = 0
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["resolve_status"] == "success":
                        success_count += 1
                    else:
                        fail_count += 1
                        
                except Exception as e:
                    original = futures[future]
                    results.append({
                        **original,
                        "resolved_url": original["url"],
                        "resolved_domain": "error",
                        "resolver_method": "exception",
                        "resolve_status": "failed",
                    })
                    fail_count += 1
                
                pbar.set_postfix({"✅": success_count, "❌": fail_count})
                pbar.update(1)
    
    elapsed = time.time() - start_time
    
    # ===== Simpan Hasil =====
    df_results = pd.DataFrame(results)
    
    # Split: sukses dan gagal
    df_success = df_results[df_results["resolve_status"] == "success"].copy()
    df_failed = df_results[df_results["resolve_status"] == "failed"].copy()
    
    # Deduplicate berdasarkan resolved_url
    before_dedup = len(df_success)
    df_success = df_success.drop_duplicates(subset=["resolved_url"], keep="first")
    after_dedup = len(df_success)
    
    # Simpan
    os.makedirs(os.path.dirname(output_resolved_csv), exist_ok=True)
    df_success.to_csv(output_resolved_csv, index=False, encoding="utf-8-sig")
    if len(df_failed) > 0:
        df_failed.to_csv(output_failed_csv, index=False, encoding="utf-8-sig")
    
    # ===== Ringkasan =====
    print()
    print("=" * 65)
    print("✅ URL RESOLUTION SELESAI!")
    print(f"   • Waktu             : {elapsed:.1f} detik ({elapsed/60:.1f} menit)")
    print(f"   • Berhasil resolve  : {len(df_success)} URL")
    print(f"   • Gagal resolve     : {len(df_failed)} URL")
    print(f"   • Duplikat dihapus  : {before_dedup - after_dedup}")
    print("=" * 65)
    print()
    
    # Breakdown per resolver method
    print("📊 Breakdown per metode resolver:")
    method_counts = df_success["resolver_method"].value_counts()
    for method, count in method_counts.items():
        print(f"   {method}: {count}")
    print()
    
    # Breakdown per domain (top 15)
    print("📊 Breakdown per domain (top 15):")
    domain_counts = df_success["resolved_domain"].value_counts()
    for domain, count in domain_counts.head(15).items():
        print(f"   {domain}: {count}")
    print()
    
    print(f"📁 Resolved URLs : {output_resolved_csv}")
    if len(df_failed) > 0:
        print(f"📁 Failed URLs   : {output_failed_csv}")
    print()
    print("▶️  Langkah selanjutnya: jalankan 'python3 03_extraction.py'")
    print("=" * 65)
    
    log.info(
        "Resolution completed",
        success=len(df_success),
        failed=len(df_failed),
        elapsed_sec=round(elapsed, 1),
    )


if __name__ == "__main__":
    main()
