"""
02_extraction.py — Mengambil konten dari setiap URL artikel (dengan Live Progress Tracking)
GRAK 2026 · Sprint 3 · Materi 4

CARA PAKAI:
  python3 02_extraction.py

PRASYARAT:
  → Sudah jalankan 01_discovery.py (file discovery_articles.csv harus ada)

HASIL:
  → data/articles_database.csv   (1 baris = 1 artikel utuh — REFERENSI)
  → data/paragraphs_raw.csv      (1 baris = 1 paragraf — DATASET)
  → data/failed_urls.csv         (URL yang gagal di-extract)
  → data/progress.json           (Status tracking live)
"""

import requests
import pandas as pd
import time
import os
import sys
import json
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    HEADERS, DATA_DIR, DISCOVERY_CSV,
    ARTICLES_DB_CSV, PARAGRAPHS_RAW_CSV, FAILED_URLS_CSV,
    ANTARA_CONTENT_SELECTOR, ANTARA_BASE_URL,
    MIN_PARAGRAPH_LENGTH, BOILERPLATE_PATTERNS,
    REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS,
)

PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

# Coba import newspaper3k
try:
    from newspaper import Article as NewsArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False


def update_progress(script_name: str, status: str, current: int, total: int, item_name: str = ""):
    """Simpan status progress ke file JSON agar bisa dipantau dari luar/dashboard."""
    try:
        data = {
            "script": script_name,
            "status": status,
            "current": current,
            "total": total,
            "percent": round((current / total * 100) if total > 0 else 0, 1),
            "current_item": item_name[:100],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def is_boilerplate(text: str) -> bool:
    """Cek apakah text adalah boilerplate (bukan konten artikel)."""
    text_lower = text.lower().strip()
    for pattern in BOILERPLATE_PATTERNS:
        if pattern in text_lower:
            return True
    return False


def extract_antara(url: str) -> dict | None:
    """Extract artikel dari antaranews.com."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
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
        
        full_text = "\n\n".join(clean_paragraphs)
        
        return {
            "title": title,
            "publish_date": publish_date,
            "author": author,
            "full_text": full_text,
            "paragraphs": clean_paragraphs,
            "total_paragraphs_found": len(all_paragraphs),
            "relevant_paragraphs": len(clean_paragraphs),
            "extraction_method": "antara_parser",
        }
    except Exception:
        return None


def extract_newspaper3k(url: str) -> dict | None:
    """Extract artikel menggunakan newspaper3k."""
    if not HAS_NEWSPAPER:
        return None
    try:
        article = NewsArticle(url, language="id")
        article.download()
        article.parse()
        
        if not article.text or len(article.text) < 100:
            return None
        
        raw_paragraphs = article.text.split("\n")
        clean_paragraphs = []
        for p in raw_paragraphs:
            text = p.strip()
            if len(text) >= MIN_PARAGRAPH_LENGTH and not is_boilerplate(text):
                clean_paragraphs.append(text)
        
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
    """Fallback: extract menggunakan BeautifulSoup generic."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
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
            soup.find("div", class_="content") or
            soup.find("div", class_="post-content") or
            soup.find("div", class_="entry-content") or
            soup.find("div", class_="article-content") or
            soup.find("div", {"itemprop": "articleBody"}) or
            soup
        )
        
        all_paragraphs = content_area.find_all("p")
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
            "author": "",
            "full_text": "\n\n".join(clean_paragraphs),
            "paragraphs": clean_paragraphs,
            "total_paragraphs_found": len(all_paragraphs),
            "relevant_paragraphs": len(clean_paragraphs),
            "extraction_method": "fallback_bs4",
        }
    except Exception:
        return None


def extract_article(url: str, source_portal: str) -> dict | None:
    """Strategi extraction bertingkat."""
    if "antaranews.com" in url:
        result = extract_antara(url)
        if result:
            return result
    
    result = extract_newspaper3k(url)
    if result:
        return result
    
    return extract_fallback(url)


def get_domain(url: str) -> str:
    """Ambil domain dari URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return "unknown"


def main():
    if not os.path.exists(DISCOVERY_CSV):
        print(f"❌ File tidak ditemukan: {DISCOVERY_CSV}", flush=True)
        print("   Jalankan 01_discovery.py terlebih dahulu!", flush=True)
        return
    
    df_discovery = pd.read_csv(DISCOVERY_CSV)
    total_urls = len(df_discovery)
    
    print("=" * 60, flush=True)
    print("EXTRACTION — Mengambil konten artikel (dengan Live Progress)", flush=True)
    print(f"Total URL: {total_urls}", flush=True)
    print(f"Estimasi waktu: {total_urls * 3 // 60} menit", flush=True)
    print("=" * 60, flush=True)
    print()
    
    articles_db = []
    paragraphs_all = []
    failed_urls = []
    
    article_id = 0
    paragraph_id = 0
    
    update_progress("02_extraction.py", "running", 0, total_urls, "Memulai ekstraksi...")
    
    # Progress Bar interaktif menggunakan tqdm
    with tqdm(total=total_urls, desc="Extracting Articles", unit="url", ncols=80) as pbar:
        for idx, row in df_discovery.iterrows():
            url = row["url"]
            title_hint = row.get("title", "")
            source_portal = row.get("source_portal", get_domain(url))
            query_used = row.get("query_used", "")
            discovery_date = row.get("publish_date", "")
            
            update_progress("02_extraction.py", "running", idx + 1, total_urls, title_hint or url)
            
            result = extract_article(url, source_portal)
            
            if result is None:
                failed_urls.append({
                    "url": url,
                    "title": title_hint,
                    "source_portal": source_portal,
                    "error": "extraction_failed",
                    "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                pbar.set_postfix({"sukses": len(articles_db), "gagal": len(failed_urls)})
                pbar.update(1)
                time.sleep(DELAY_BETWEEN_REQUESTS)
                continue
            
            article_id += 1
            if not source_portal or source_portal == "":
                source_portal = get_domain(url)
            
            # Database artikel utuh
            articles_db.append({
                "article_id": article_id,
                "title": result["title"] or title_hint,
                "url": url,
                "source_portal": source_portal,
                "publish_date": result["publish_date"] or discovery_date,
                "author": result["author"],
                "full_text": result["full_text"],
                "total_paragraphs_found": result["total_paragraphs_found"],
                "relevant_paragraphs": result["relevant_paragraphs"],
                "extraction_method": result["extraction_method"],
                "query_used": query_used,
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            
            # Database per paragraf
            for para_text in result["paragraphs"]:
                paragraph_id += 1
                paragraphs_all.append({
                    "paragraph_id": paragraph_id,
                    "article_id": article_id,
                    "text": para_text,
                    "article_title": result["title"] or title_hint,
                    "article_url": url,
                    "source_portal": source_portal,
                    "publish_date": result["publish_date"] or discovery_date,
                    "query_used": query_used,
                    "word_count": len(para_text.split()),
                    "collector": "Aulia",
                })
            
            pbar.set_postfix({"sukses": len(articles_db), "paragraf": len(paragraphs_all)})
            pbar.update(1)
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Simpan hasil
    os.makedirs(DATA_DIR, exist_ok=True)
    if articles_db:
        pd.DataFrame(articles_db).to_csv(ARTICLES_DB_CSV, index=False, encoding="utf-8-sig")
    if paragraphs_all:
        pd.DataFrame(paragraphs_all).to_csv(PARAGRAPHS_RAW_CSV, index=False, encoding="utf-8-sig")
    if failed_urls:
        pd.DataFrame(failed_urls).to_csv(FAILED_URLS_CSV, index=False, encoding="utf-8-sig")
    
    update_progress("02_extraction.py", "completed", total_urls, total_urls, f"Selesai: {len(articles_db)} artikel, {len(paragraphs_all)} paragraf")
    
    print()
    print("=" * 60, flush=True)
    print("✅ EXTRACTION SELESAI!", flush=True)
    print(f"   Artikel berhasil: {len(articles_db)} / {total_urls}", flush=True)
    print(f"   Artikel gagal:    {len(failed_urls)}", flush=True)
    print(f"   Total paragraf:   {len(paragraphs_all)}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
