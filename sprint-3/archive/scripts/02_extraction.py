"""
02_extraction.py — Mengambil konten artikel dengan Google News Decoder & Multithreading
GRAK 2026 · Sprint 3 · Materi 4

FITUR UTAMA:
  1. Google News Decoder  → Membuka enkripsi link Google News ke URL berita asli
  2. Multithreading Pool  → Memproses 10-12 URL paralel (estimasi ~3-4 menit total)
  3. Live Progress Bar    → Progress visual tqdm dengan metrik sukses/gagal & kecepatan
  4. Resilient Fallbacks  → Antara Parser → newspaper3k → BeautifulSoup generic

CARA PAKAI:
  python3 02_extraction.py

PRASYARAT:
  → Sudah jalankan 01_discovery.py (file discovery_articles.csv harus ada)

HASIL:
  → data/articles_database.csv   (1 baris = 1 artikel utuh — REFERENSI)
  → data/paragraphs_raw.csv      (1 baris = 1 paragraf — DATASET MENTAH)
  → data/failed_urls.csv         (URL yang gagal di-extract)
  → data/progress.json           (Status tracking live)
"""

import requests
import pandas as pd
import time
import os
import sys
import json
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    HEADERS, DATA_DIR, DISCOVERY_CSV,
    ARTICLES_DB_CSV, PARAGRAPHS_RAW_CSV, FAILED_URLS_CSV,
    ANTARA_CONTENT_SELECTOR, MIN_PARAGRAPH_LENGTH,
    BOILERPLATE_PATTERNS, REQUEST_TIMEOUT,
)

PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
MAX_WORKERS = 10  # Jumlah thread paralel

# Import Google News Decoder
try:
    # pyrefly: ignore [missing-import]
    from googlenewsdecoder import gnewsdecoder
    HAS_GNEWS_DECODER = True
except ImportError:
    HAS_GNEWS_DECODER = False
    print("⚠️ googlenewsdecoder belum terinstall. Install dengan: pip install googlenewsdecoder", flush=True)

# Import newspaper3k
try:
    from newspaper import Article as NewsArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False

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


def decode_url_if_needed(raw_url: str) -> str:
    """Jika URL dari Google News, decode ke URL portal asli."""
    if "news.google.com" in raw_url and HAS_GNEWS_DECODER:
        try:
            res = gnewsdecoder(raw_url)
            if res.get("status") and res.get("decoded_url"):
                return res["decoded_url"]
        except Exception:
            pass
    return raw_url


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
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
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
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
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
    1. Decode URL (jika link Google News)
    2. Extract isi artikel
    3. Kembalikan (article_record, list_of_paragraphs, error_record)
    """
    raw_url = item["url"]
    title_hint = item.get("title", "")
    source_hint = item.get("source_portal", "")
    query_used = item.get("query_used", "")
    discovery_date = item.get("publish_date", "")
    
    # 1. Decode Google News URL
    real_url = decode_url_if_needed(raw_url)
    source_portal = get_domain(real_url) if ("news.google.com" in raw_url or not source_hint) else source_hint
    
    # 2. Extract Konten
    result = None
    if "antaranews.com" in real_url:
        result = extract_antara(real_url)
    
    if result is None:
        result = extract_newspaper3k(real_url)
        
    if result is None:
        result = extract_fallback(real_url)
    
    # 3. Handle Gagal
    if result is None:
        failed_entry = {
            "raw_url": raw_url,
            "real_url": real_url,
            "title": title_hint,
            "source_portal": source_portal,
            "error": "extraction_failed",
            "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return None, [], failed_entry
    
    # 4. Handle Sukses
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
    if not os.path.exists(DISCOVERY_CSV):
        print(f"❌ File tidak ditemukan: {DISCOVERY_CSV}", flush=True)
        print("   Jalankan 01_discovery.py terlebih dahulu!", flush=True)
        return
    
    df_discovery = pd.read_csv(DISCOVERY_CSV)
    total_urls = len(df_discovery)
    
    print("=" * 60, flush=True)
    print("🚀 EXTRACTION — Mengambil Konten Berita Ekosistem Startup Aceh", flush=True)
    print(f"   • Total URL        : {total_urls} artikel", flush=True)
    print(f"   • Worker Threads   : {MAX_WORKERS} threads paralel", flush=True)
    print(f"   • Google Decoder   : {'AKTIF ✅' if HAS_GNEWS_DECODER else 'NONAKTIF ⚠️'}", flush=True)
    print(f"   • Estimasi Waktu   : ~3 - 4 menit", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)
    
    items = df_discovery.to_dict(orient="records")
    
    articles_db = []
    paragraphs_all = []
    failed_urls = []
    
    completed_count = 0
    update_progress("02_extraction.py", "Extracting Articles", 0, total_urls, "Memulai ekstraksi paralel...")
    
    start_time = time.time()
    
    # Menjalankan ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_single_article, item): item for item in items}
        
        with tqdm(total=total_urls, desc="Extracting Articles", unit="url", ncols=85) as pbar:
            for future in as_completed(futures):
                completed_count += 1
                try:
                    art_record, paras, failed_record = future.result()
                    
                    if art_record:
                        art_record["article_id"] = len(articles_db) + 1
                        articles_db.append(art_record)
                        
                        for p in paras:
                            p["paragraph_id"] = len(paragraphs_all) + 1
                            p["article_id"] = art_record["article_id"]
                            paragraphs_all.append(p)
                    else:
                        failed_urls.append(failed_record)
                        
                except Exception as e:
                    failed_urls.append({
                        "raw_url": "unknown",
                        "real_url": "unknown",
                        "title": "Exception",
                        "source_portal": "unknown",
                        "error": str(e),
                        "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                # Update visual progress
                pbar.set_postfix({
                    "sukses": len(articles_db),
                    "paragraf": len(paragraphs_all),
                    "gagal": len(failed_urls)
                })
                pbar.update(1)
                
                if completed_count % 15 == 0 or completed_count == total_urls:
                    update_progress(
                        "02_extraction.py", 
                        "Extracting Articles", 
                        completed_count, 
                        total_urls, 
                        f"Sukses: {len(articles_db)} | Paragraf: {len(paragraphs_all)} | Gagal: {len(failed_urls)}"
                    )
    
    elapsed = time.time() - start_time
    
    # Simpan hasil
    os.makedirs(DATA_DIR, exist_ok=True)
    if articles_db:
        pd.DataFrame(articles_db).to_csv(ARTICLES_DB_CSV, index=False, encoding="utf-8-sig")
    if paragraphs_all:
        pd.DataFrame(paragraphs_all).to_csv(PARAGRAPHS_RAW_CSV, index=False, encoding="utf-8-sig")
    if failed_urls:
        pd.DataFrame(failed_urls).to_csv(FAILED_URLS_CSV, index=False, encoding="utf-8-sig")
    
    update_progress(
        "02_extraction.py", 
        "Completed", 
        total_urls, 
        total_urls, 
        f"Selesai dalam {elapsed/60:.1f} menit! {len(articles_db)} artikel sukses, {len(paragraphs_all)} paragraf."
    )
    
    print("\n" + "=" * 60, flush=True)
    print("✅ EXTRACTION SELESAI!", flush=True)
    print(f"   • Waktu eksekusi     : {elapsed:.1f} detik ({elapsed/60:.1f} menit)", flush=True)
    print(f"   • Artikel berhasil   : {len(articles_db)} / {total_urls} ({(len(articles_db)/total_urls*100):.1f}%)", flush=True)
    print(f"   • Artikel gagal      : {len(failed_urls)}", flush=True)
    print(f"   • Total paragraf     : {len(paragraphs_all)} paragraf", flush=True)
    print("=" * 60, flush=True)
    print(f"📁 Database Artikel  : {ARTICLES_DB_CSV}", flush=True)
    print(f"📁 Dataset Paragraf  : {PARAGRAPHS_RAW_CSV}", flush=True)
    if failed_urls:
        print(f"📁 Log URL Gagal     : {FAILED_URLS_CSV}", flush=True)
    print(flush=True)
    print("▶️  Langkah selanjutnya: jalankan 'python3 03_cleaning.py'", flush=True)


if __name__ == "__main__":
    main()
