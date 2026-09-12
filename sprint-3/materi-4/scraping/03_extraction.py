"""
03_extraction.py — Mengambil konten artikel dengan RateLimitedClient & Checkpoint/Resume
GRAK 2026 · Sprint 3 · Materi 4

FITUR UTAMA:
  1. Input Resolved URLs  → Menggunakan resolved_urls.csv dari 02_resolver.py
  2. Anti-Ban HTTP        → RateLimitedClient (rotating UA, delay per-domain, retry)
  3. Resume Engine        → Cek articles_database.csv, skip yang sudah ada, ID auto-increment
  4. Resilient Fallbacks  → Antara Parser → newspaper3k → BeautifulSoup generic
  5. Structured Logging   → Log tersimpan di logs/scraping_YYYY-MM-DD.jsonl

CARA PAKAI:
  python3 03_extraction.py
  python3 03_extraction.py --limit 5   # Smoke test mode

PRASYARAT:
  → Sudah jalankan 02_resolver.py (file resolved_urls.csv harus ada)

HASIL:
  → data/articles_database.csv   (1 baris = 1 artikel utuh — REFERENSI)
  → data/paragraphs_raw.csv      (1 baris = 1 paragraf — DATASET MENTAH)
  → data/failed_urls.csv         (URL yang gagal di-extract)
  → data/progress.json           (Status tracking live)
"""

import os
import sys
import json
import time
import argparse
import threading
import pandas as pd
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

# Import config & shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DATA_DIR, RESOLVED_CSV,
    ARTICLES_DB_CSV, PARAGRAPHS_RAW_CSV, FAILED_URLS_CSV,
    ANTARA_CONTENT_SELECTOR, MIN_PARAGRAPH_LENGTH,
    BOILERPLATE_PATTERNS, REQUEST_TIMEOUT,
)
from lib.http_client import RateLimitedClient
from lib.logger import get_logger

PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
MAX_WORKERS = 8  # 8 worker threads paralel dengan per-domain rate limit

# Logger
log = get_logger("03_extraction")

# HTTP Client (shared, thread-safe, rate-limited)
http = RateLimitedClient(timeout=REQUEST_TIMEOUT, max_retries=3)

# Import newspaper3k
try:
    from newspaper import Article as NewsArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False
    log.warning("newspaper3k not installed, skipping newspaper strategy")

# Lock untuk thread-safe update progress JSON
progress_lock = threading.Lock()


def update_progress(script_name: str, step: str, current: int, total: int, detail: str = ""):
    """Simpan status progress ke file JSON secara thread-safe."""
    with progress_lock:
        try:
            data = {
                "script": script_name,
                "step": step,
                "current": current,
                "total": total,
                "percent": round((current / total * 100) if total > 0 else 0, 1),
                "detail": detail[:120],
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


def get_domain(url: str) -> str:
    """Ambil nama domain bersih dari URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return "unknown"


def is_boilerplate(text: str) -> bool:
    """Cek apakah text adalah boilerplate / iklan."""
    text_lower = text.lower().strip()
    for pattern in BOILERPLATE_PATTERNS:
        if pattern in text_lower:
            return True
    return False


def extract_antara(url: str) -> dict | None:
    """Parser khusus antaranews.com."""
    try:
        response = http.get(url)
        if response is None or response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
        
        date_meta = soup.find("meta", {"property": "article:published_time"})
        publish_date = ""
        if date_meta and date_meta.get("content"):
            publish_date = date_meta["content"][:10]
        
        author_meta = soup.find("meta", {"name": "author"})
        author = author_meta["content"] if author_meta and author_meta.get("content") else ""
        
        content_div = soup.select_one(ANTARA_CONTENT_SELECTOR)
        if not content_div:
            return None
        
        all_paragraphs = content_div.find_all("p")
        clean_paragraphs = []
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if len(text) >= MIN_PARAGRAPH_LENGTH and not is_boilerplate(text):
                clean_paragraphs.append(text)
        
        if not clean_paragraphs:
            return None
        
        return {
            "title": title,
            "publish_date": publish_date,
            "author": author,
            "full_text": "\n\n".join(clean_paragraphs),
            "paragraphs": clean_paragraphs,
            "total_paragraphs_found": len(all_paragraphs),
            "relevant_paragraphs": len(clean_paragraphs),
            "extraction_method": "antara_parser",
        }
    except Exception:
        return None


def extract_newspaper3k(url: str) -> dict | None:
    """Parser universal menggunakan newspaper3k."""
    if not HAS_NEWSPAPER:
        return None
    try:
        article = NewsArticle(url, language="id", request_timeout=REQUEST_TIMEOUT)
        article.download()
        article.parse()
        
        if not article.text or len(article.text) < 100:
            return None
        
        raw_paragraphs = article.text.split("\n")
        clean_paragraphs = [
            p.strip() for p in raw_paragraphs 
            if len(p.strip()) >= MIN_PARAGRAPH_LENGTH and not is_boilerplate(p)
        ]
        
        if not clean_paragraphs:
            return None
        
        publish_date = ""
        if article.publish_date:
            try:
                publish_date = article.publish_date.strftime("%Y-%m-%d")
            except Exception:
                publish_date = str(article.publish_date)[:10]
        
        return {
            "title": article.title or "",
            "publish_date": publish_date,
            "author": ", ".join(article.authors) if article.authors else "",
            "full_text": "\n\n".join(clean_paragraphs),
            "paragraphs": clean_paragraphs,
            "total_paragraphs_found": len(raw_paragraphs),
            "relevant_paragraphs": len(clean_paragraphs),
            "extraction_method": "newspaper3k",
        }
    except Exception:
        return None


def extract_fallback(url: str) -> dict | None:
    """Fallback parser BeautifulSoup generic."""
    try:
        response = http.get(url)
        if response is None or response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
        
        publish_date = ""
        for meta_name in ["article:published_time", "publishdate", "datePublished"]:
            date_meta = soup.find("meta", {"property": meta_name}) or soup.find("meta", {"name": meta_name})
            if date_meta and date_meta.get("content"):
                publish_date = date_meta["content"][:10]
                break
        
        content_area = (
            soup.find("article") or
            soup.find("div", class_="post-content") or
            soup.find("div", class_="entry-content") or
            soup.find("div", class_="article-content") or
            soup.find("div", {"itemprop": "articleBody"}) or
            soup
        )
        
        all_paragraphs = content_area.find_all("p")
        clean_paragraphs = [
            p.get_text(strip=True) for p in all_paragraphs
            if len(p.get_text(strip=True)) >= MIN_PARAGRAPH_LENGTH and not is_boilerplate(p.get_text(strip=True))
        ]
        
        if not clean_paragraphs:
            return None
        
        return {
            "title": title,
            "publish_date": publish_date,
            "author": "",
            "full_text": "\n\n".join(clean_paragraphs),
            "paragraphs": clean_paragraphs,
            "total_paragraphs_found": len(all_paragraphs),
            "relevant_paragraphs": len(clean_paragraphs),
            "extraction_method": "fallback_bs4",
        }
    except Exception:
        return None


def process_single_article(item: dict) -> tuple[dict | None, list[dict], dict | None]:
    """
    Worker function yang dijalankan di setiap thread:
    1. Ambil resolved_url
    2. Extract isi artikel (Antara -> newspaper3k -> bs4)
    3. Kembalikan (article_record, list_of_paragraphs, error_record)
    """
    raw_url = item.get("url", "")
    real_url = item.get("resolved_url", raw_url)
    source_portal = item.get("resolved_domain", get_domain(real_url))
    title_hint = item.get("title", "")
    query_used = item.get("query_used", "")
    discovery_date = item.get("publish_date", "")
    
    # 1. Extract Konten
    result = None
    if "antaranews.com" in real_url:
        result = extract_antara(real_url)
    
    if result is None:
        result = extract_newspaper3k(real_url)
        
    if result is None:
        result = extract_fallback(real_url)
    
    # 2. Handle Gagal
    if result is None:
        failed_entry = {
            "raw_url": raw_url,
            "real_url": real_url,
            "title": title_hint,
            "source_portal": source_portal,
            "error": "extraction_failed",
            "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        log.warning("Extraction failed", url=real_url[:80], source=source_portal)
        return None, [], failed_entry
    
    # 3. Handle Sukses
    log.info("Extracted successfully", url=real_url[:80], method=result["extraction_method"])
    article_data = {
        "title": result["title"] or title_hint,
        "raw_url": raw_url,
        "url": real_url,
        "source_portal": source_portal,
        "publish_date": result["publish_date"] or discovery_date,
        "author": result["author"],
        "full_text": result["full_text"],
        "total_paragraphs_found": result["total_paragraphs_found"],
        "relevant_paragraphs": result["relevant_paragraphs"],
        "extraction_method": result["extraction_method"],
        "query_used": query_used,
        "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    paragraphs_data = []
    for p_text in result["paragraphs"]:
        paragraphs_data.append({
            "text": p_text,
            "article_title": result["title"] or title_hint,
            "article_url": real_url,
            "source_portal": source_portal,
            "publish_date": result["publish_date"] or discovery_date,
            "query_used": query_used,
            "word_count": len(p_text.split()),
            "collector": "Aulia",
        })
    
    return article_data, paragraphs_data, None


def main():
    parser = argparse.ArgumentParser(description="Extract article content from resolved URLs")
    parser.add_argument("--limit", type=int, default=None, help="Limit jumlah URL yang diekstrak (smoke test)")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"Jumlah worker threads (default: {MAX_WORKERS})")
    parser.add_argument("--input", type=str, default=RESOLVED_CSV, help="File input resolved CSV")
    parser.add_argument("--output-db", type=str, default=ARTICLES_DB_CSV, help="File output database artikel")
    parser.add_argument("--output-para", type=str, default=PARAGRAPHS_RAW_CSV, help="File output dataset paragraf")
    parser.add_argument("--smoke-test", action="store_true", help="Jalankan dalam mode smoke test terisolasi")
    args, _ = parser.parse_known_args()

    input_csv = args.input
    output_articles_csv = args.output_db
    output_paragraphs_csv = args.output_para
    output_failed_csv = FAILED_URLS_CSV if not args.smoke_test else os.path.join(os.path.dirname(output_articles_csv), "failed_urls.csv")

    if not os.path.exists(input_csv):
        print(f"❌ File tidak ditemukan: {input_csv}", flush=True)
        print("   Jalankan 02_resolver.py terlebih dahulu!", flush=True)
        return
    
    df = pd.read_csv(input_csv)
    
    # Filter hanya yang resolve statusnya success (atau jika kolom tidak ada, pakai semua)
    if "resolve_status" in df.columns:
        df = df[df["resolve_status"] == "success"].copy()
    
    total_in_file = len(df)

    # === RESUME LOGIC ===
    existing_articles = []
    existing_paragraphs = []
    max_article_id = 0
    max_paragraph_id = 0

    if not args.smoke_test and os.path.exists(output_articles_csv):
        df_existing = pd.read_csv(output_articles_csv)
        existing_urls = set(df_existing["url"].dropna().tolist())
        if "raw_url" in df_existing.columns:
            existing_urls.update(df_existing["raw_url"].dropna().tolist())
        
        before = len(df)
        url_col = "resolved_url" if "resolved_url" in df.columns else "url"
        df = df[~df[url_col].isin(existing_urls)].copy()
        skipped = before - len(df)
        if skipped > 0:
            print(f"⏭️  Resume mode: skip {skipped} URL yang sudah di-extract di {output_articles_csv}", flush=True)
        
        existing_articles = df_existing.to_dict(orient="records")
        if not df_existing.empty and "article_id" in df_existing.columns:
            max_article_id = int(df_existing["article_id"].max())

    if not args.smoke_test and os.path.exists(output_paragraphs_csv):
        df_para_existing = pd.read_csv(output_paragraphs_csv)
        existing_paragraphs = df_para_existing.to_dict(orient="records")
        if not df_para_existing.empty and "paragraph_id" in df_para_existing.columns:
            max_paragraph_id = int(df_para_existing["paragraph_id"].max())

    # Limit untuk smoke test
    if args.limit and args.limit > 0:
        df = df.head(args.limit).copy()

    total_urls = len(df)
    if total_urls == 0:
        print("✅ Semua URL sudah di-extract sebelumnya!", flush=True)
        return

    print("=" * 65, flush=True)
    print("🚀 EXTRACTION — Mengambil Konten Berita Ekosistem Startup Aceh", flush=True)
    print(f"   • Total URL diproses : {total_urls} artikel (dari {total_in_file} resolved)", flush=True)
    print(f"   • Existing database  : {len(existing_articles)} artikel tersimpan", flush=True)
    print(f"   • Worker Threads     : {args.workers} threads paralel", flush=True)
    print(f"   • Newspaper3k Parser : {'AKTIF ✅' if HAS_NEWSPAPER else 'NONAKTIF ⚠️'}", flush=True)
    if args.limit or args.smoke_test:
        print(f"   • Mode               : 🧪 Smoke Test ({total_urls} URLs)", flush=True)
    print("=" * 65, flush=True)
    print(flush=True)
    
    log.info("Starting article extraction", total=total_urls, workers=args.workers)

    items = df.to_dict(orient="records")
    new_articles_db = []
    new_paragraphs_all = []
    failed_urls = []
    
    completed_count = 0
    update_progress("03_extraction.py", "Extracting Articles", 0, total_urls, "Memulai ekstraksi paralel...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_single_article, item): item for item in items}
        
        with tqdm(total=total_urls, desc="Extracting Articles", unit="url", ncols=85) as pbar:
            for future in as_completed(futures):
                completed_count += 1
                try:
                    art_record, paras, failed_record = future.result()
                    
                    if art_record:
                        art_record["article_id"] = max_article_id + len(new_articles_db) + 1
                        new_articles_db.append(art_record)
                        
                        for p in paras:
                            p["paragraph_id"] = max_paragraph_id + len(new_paragraphs_all) + 1
                            p["article_id"] = art_record["article_id"]
                            new_paragraphs_all.append(p)
                    else:
                        failed_urls.append(failed_record)
                        
                except Exception as e:
                    original = futures[future]
                    raw_u = original.get("url", "unknown")
                    real_u = original.get("resolved_url", raw_u)
                    failed_urls.append({
                        "raw_url": raw_u,
                        "real_url": real_u,
                        "title": original.get("title", "Exception"),
                        "source_portal": original.get("resolved_domain", "unknown"),
                        "error": str(e),
                        "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                pbar.set_postfix({
                    "sukses": len(new_articles_db),
                    "paragraf": len(new_paragraphs_all),
                    "gagal": len(failed_urls)
                })
                pbar.update(1)
                
                if completed_count % 10 == 0 or completed_count == total_urls:
                    update_progress(
                        "03_extraction.py", 
                        "Extracting Articles", 
                        completed_count, 
                        total_urls, 
                        f"Baru: {len(new_articles_db)} | Paragraf: {len(new_paragraphs_all)} | Gagal: {len(failed_urls)}"
                    )
    
    elapsed = time.time() - start_time
    
    # Simpan hasil (Gabungkan existing + new)
    os.makedirs(os.path.dirname(output_articles_csv), exist_ok=True)
    os.makedirs(os.path.dirname(output_paragraphs_csv), exist_ok=True)
    
    all_articles_to_save = existing_articles + new_articles_db
    all_paragraphs_to_save = existing_paragraphs + new_paragraphs_all
    
    if all_articles_to_save:
        pd.DataFrame(all_articles_to_save).to_csv(output_articles_csv, index=False, encoding="utf-8-sig")
    if all_paragraphs_to_save:
        pd.DataFrame(all_paragraphs_to_save).to_csv(output_paragraphs_csv, index=False, encoding="utf-8-sig")
    if failed_urls:
        # Append atau save failed URLs
        if os.path.exists(output_failed_csv) and not args.smoke_test:
            try:
                df_f_exist = pd.read_csv(output_failed_csv)
                df_f_combined = pd.concat([df_f_exist, pd.DataFrame(failed_urls)], ignore_index=True)
                df_f_combined.drop_duplicates(subset=["real_url"], keep="last").to_csv(output_failed_csv, index=False, encoding="utf-8-sig")
            except Exception:
                pd.DataFrame(failed_urls).to_csv(output_failed_csv, index=False, encoding="utf-8-sig")
        else:
            pd.DataFrame(failed_urls).to_csv(output_failed_csv, index=False, encoding="utf-8-sig")
    
    update_progress(
        "03_extraction.py", 
        "Completed", 
        total_urls, 
        total_urls, 
        f"Selesai dalam {elapsed/60:.1f} menit! {len(new_articles_db)} artikel baru sukses."
    )
    
    print("\n" + "=" * 65, flush=True)
    print("✅ EXTRACTION SELESAI!", flush=True)
    print(f"   • Waktu eksekusi     : {elapsed:.1f} detik ({elapsed/60:.1f} menit)", flush=True)
    print(f"   • Artikel baru sukses: {len(new_articles_db)} / {total_urls} ({(len(new_articles_db)/total_urls*100):.1f}%)", flush=True)
    print(f"   • Artikel baru gagal : {len(failed_urls)}", flush=True)
    print(f"   • Paragraf baru      : {len(new_paragraphs_all)} paragraf", flush=True)
    print(f"   • Total DB artikel   : {len(all_articles_to_save)} artikel", flush=True)
    print(f"   • Total DB paragraf  : {len(all_paragraphs_to_save)} paragraf", flush=True)
    print("=" * 65, flush=True)
    print(f"📁 Database Artikel  : {output_articles_csv}", flush=True)
    print(f"📁 Dataset Paragraf  : {output_paragraphs_csv}", flush=True)
    if failed_urls:
        print(f"📁 Log URL Gagal     : {output_failed_csv}", flush=True)
    print(flush=True)
    print("▶️  Langkah selanjutnya: jalankan 'python3 04_cleaning.py'", flush=True)

    log.info(
        "Extraction completed",
        new_articles=len(new_articles_db),
        new_paragraphs=len(new_paragraphs_all),
        total_articles=len(all_articles_to_save),
        elapsed_sec=round(elapsed, 1),
    )


if __name__ == "__main__":
    main()
