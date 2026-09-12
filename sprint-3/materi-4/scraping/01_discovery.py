"""
01_discovery.py — Menemukan URL artikel berita tentang ekosistem startup Aceh
GRAK 2026 · Sprint 3 · Materi 4

CARA PAKAI:
  python3 01_discovery.py

HASIL:
  → data/discovery_articles.csv (daftar URL artikel + judul + tanggal + sumber)

WAKTU: ~5-10 menit (tergantung jumlah query dan kecepatan internet)
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import urllib.parse
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    HEADERS, DISCOVERY_QUERIES, DATA_DIR, DISCOVERY_CSV,
    GOOGLE_NEWS_RSS_BASE, GOOGLE_NEWS_PARAMS,
    ANTARA_SEARCH_URL, ANTARA_BASE_URL, ANTARA_ARTICLE_SELECTOR,
    REQUEST_TIMEOUT, DELAY_BETWEEN_QUERIES,
)


def discover_google_news_rss(query: str) -> list[dict]:
    """
    Cari artikel via Google News RSS feed.
    
    Input:  query string, misal "startup Aceh"
    Output: list of dict {title, url, date, source_portal, query_used}
    """
    results = []
    
    # Buat URL RSS
    params = {**GOOGLE_NEWS_PARAMS, "q": query}
    url = f"{GOOGLE_NEWS_RSS_BASE}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            pubdate_el = item.find("pubDate")
            source_el = item.find("source")
            
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            raw_url = link_el.text.strip() if link_el is not None and link_el.text else ""
            pub_date = pubdate_el.text.strip() if pubdate_el is not None and pubdate_el.text else ""
            source = source_el.text.strip() if source_el is not None and source_el.text else ""
            
            if not raw_url:
                continue
            
            results.append({
                "title": title,
                "url": raw_url,
                "publish_date": pub_date,
                "source_portal": source,
                "query_used": query,
                "discovery_method": "google_news_rss",
            })
        
        print(f"  ✓ Google News RSS: {len(results)} artikel untuk '{query}'")
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Google News RSS gagal untuk '{query}': {e}")
    except ET.ParseError as e:
        print(f"  ✗ Google News RSS parse error untuk '{query}': {e}")
    
    return results


def discover_antara_search(query: str) -> list[dict]:
    """
    Cari artikel via halaman pencarian Antara News.
    
    Input:  query string
    Output: list of dict {title, url, date, source_portal, query_used}
    """
    results = []
    
    url = f"{ANTARA_SEARCH_URL}?q={urllib.parse.quote_plus(query)}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.select(ANTARA_ARTICLE_SELECTOR)
        
        for a in articles:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            
            # Skip jika judul terlalu pendek (bukan artikel)
            if len(title) < 15:
                continue
            
            # Pastikan URL lengkap
            if href.startswith("/"):
                href = ANTARA_BASE_URL + href
            
            # Skip jika bukan URL berita
            if "/berita/" not in href and "/foto/" not in href:
                continue
            
            results.append({
                "title": title,
                "url": href,
                "publish_date": "",  # akan diambil saat extraction
                "source_portal": "antaranews.com",
                "query_used": query,
                "discovery_method": "antara_search",
            })
        
        print(f"  ✓ Antara Search: {len(results)} artikel untuk '{query}'")
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Antara Search gagal untuk '{query}': {e}")
    
    return results


def resolve_google_news_url(google_url: str) -> str:
    """
    Google News RSS memberikan URL redirect.
    Fungsi ini mencoba mendapatkan URL asli dari redirect.
    
    Jika gagal, kembalikan URL Google asli (masih bisa diakses).
    """
    try:
        # Coba follow redirect untuk mendapatkan URL asli
        response = requests.head(
            google_url, 
            headers=HEADERS, 
            timeout=10,
            allow_redirects=True
        )
        final_url = response.url
        
        # Jika masih URL Google, coba GET
        if "news.google.com" in final_url:
            response = requests.get(
                google_url,
                headers=HEADERS,
                timeout=10,
                allow_redirects=True
            )
            final_url = response.url
        
        return final_url
    except Exception:
        return google_url  # Kembalikan URL asli jika gagal


def main():
    print("=" * 60)
    print("DISCOVERY — Mencari artikel berita tentang startup Aceh")
    print(f"Jumlah query: {len(DISCOVERY_QUERIES)}")
    print(f"Estimasi waktu: {len(DISCOVERY_QUERIES) * 5} detik")
    print("=" * 60)
    print()
    
    all_results = []
    
    # --- Google News RSS ---
    print("📡 METODE 1: Google News RSS")
    print("-" * 40)
    for i, query in enumerate(DISCOVERY_QUERIES, 1):
        print(f"[{i}/{len(DISCOVERY_QUERIES)}] Query: '{query}'")
        results = discover_google_news_rss(query)
        all_results.extend(results)
        
        if i < len(DISCOVERY_QUERIES):
            time.sleep(DELAY_BETWEEN_QUERIES)
    
    print()
    
    # --- Antara News Direct Search ---
    print("📡 METODE 2: Antara News Search")
    print("-" * 40)
    # Gunakan subset query untuk Antara (yang paling penting saja)
    antara_queries = [q for q in DISCOVERY_QUERIES if "aceh" in q.lower()][:10]
    for i, query in enumerate(antara_queries, 1):
        print(f"[{i}/{len(antara_queries)}] Query: '{query}'")
        results = discover_antara_search(query)
        all_results.extend(results)
        
        if i < len(antara_queries):
            time.sleep(DELAY_BETWEEN_QUERIES)
    
    print()
    
    # --- Hasil ---
    if not all_results:
        print("⚠️  Tidak ada artikel ditemukan! Cek koneksi internet.")
        return
    
    df = pd.DataFrame(all_results)
    print(f"Total hasil mentah: {len(df)} artikel")
    
    # Deduplicate berdasarkan URL
    df_dedup = df.drop_duplicates(subset=["url"], keep="first")
    print(f"Setelah hapus duplikat: {len(df_dedup)} artikel unik")
    
    # Resolve Google News URLs (ini bisa lambat, jadi opsional)
    print()
    print("🔗 Resolving Google News redirect URLs...")
    print("   (ini bisa lambat, tunggu sebentar...)")
    
    resolved_count = 0
    for idx, row in df_dedup.iterrows():
        if "news.google.com" in row["url"]:
            original = row["url"]
            resolved = resolve_google_news_url(original)
            if resolved != original:
                df_dedup.at[idx, "url"] = resolved
                # Coba ambil nama portal dari URL
                try:
                    domain = urllib.parse.urlparse(resolved).netloc
                    domain = domain.replace("www.", "")
                    df_dedup.at[idx, "source_portal"] = domain
                except Exception:
                    pass
                resolved_count += 1
            time.sleep(1)  # Jangan terlalu cepat
    
    print(f"   Resolved {resolved_count} URLs")
    
    # Deduplicate lagi setelah resolve (bisa ada duplikat dari URL yang sama tapi beda redirect)
    df_dedup = df_dedup.drop_duplicates(subset=["url"], keep="first")
    
    # Simpan
    os.makedirs(DATA_DIR, exist_ok=True)
    df_dedup.to_csv(DISCOVERY_CSV, index=False, encoding="utf-8-sig")
    
    print()
    print("=" * 60)
    print(f"✅ SELESAI! {len(df_dedup)} artikel unik ditemukan.")
    print(f"📁 File disimpan di: {DISCOVERY_CSV}")
    print()
    print("📊 Breakdown per sumber:")
    if "source_portal" in df_dedup.columns:
        source_counts = df_dedup["source_portal"].value_counts()
        for source, count in source_counts.items():
            print(f"   {source}: {count} artikel")
    print()
    print("📊 Breakdown per metode:")
    method_counts = df_dedup["discovery_method"].value_counts()
    for method, count in method_counts.items():
        print(f"   {method}: {count} artikel")
    print()
    print("▶️  Langkah selanjutnya: jalankan 02_extraction.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
