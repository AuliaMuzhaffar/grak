"""
config.py — Konfigurasi untuk semua script scraping
GRAK 2026 · Sprint 3 · Materi 4 · Text Analysis

Semua setting ada di sini. Jika perlu ubah query, tambah portal, 
atau ganti path — ubah di file ini saja.
"""

import os

# ============================================================
# PATH — Lokasi file output
# ============================================================
# Base directory (folder "data" di sebelah folder "scraping")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Output files
DISCOVERY_CSV = os.path.join(DATA_DIR, "discovery_articles.csv")
ARTICLES_DB_CSV = os.path.join(DATA_DIR, "articles_database.csv")       # 1 baris = 1 artikel (referensi)
PARAGRAPHS_RAW_CSV = os.path.join(DATA_DIR, "paragraphs_raw.csv")      # 1 baris = 1 paragraf (dataset mentah)
PARAGRAPHS_CLEAN_CSV = os.path.join(DATA_DIR, "public_text_news_clean.csv")  # Dataset final ✅
FAILED_URLS_CSV = os.path.join(DATA_DIR, "failed_urls.csv")

# ============================================================
# HTTP — Headers untuk request
# ============================================================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

REQUEST_TIMEOUT = 20  # detik
DELAY_BETWEEN_REQUESTS = 2  # detik antar request (jangan terlalu cepat)
DELAY_BETWEEN_QUERIES = 3   # detik antar query discovery

# ============================================================
# QUERY — Daftar pencarian untuk discovery
# ============================================================
DISCOVERY_QUERIES = [
    # --- Startup & Bisnis Digital ---
    "startup Aceh",
    "startup Banda Aceh",
    "bisnis digital Aceh",
    "UMKM digital Aceh",
    "ekonomi digital Aceh",
    "wirausaha muda Aceh",
    
    # --- Ekosistem & Program ---
    "inkubator bisnis Aceh",
    "akselerator startup Aceh",
    "pelatihan digital Aceh",
    "bootcamp teknologi Aceh",
    "komunitas teknologi Aceh",
    
    # --- Funding & Investasi ---
    "pendanaan startup Aceh",
    "investasi digital Aceh",
    
    # --- Talent & SDM ---
    "talent digital Aceh",
    "programmer Aceh",
    "developer Aceh",
    
    # --- Wilayah Spesifik ---
    "UMKM Lhokseumawe",
    "startup Langsa",
    "bisnis digital Meulaboh",
    
    # --- E-commerce & Market ---
    "e-commerce Aceh",
    "marketplace Aceh",
    
    # --- Teknologi & Infrastruktur ---
    "teknologi informasi Aceh",
    "transformasi digital Aceh",
]

# ============================================================
# ACEH KEYWORDS — Untuk filter relevansi Aceh
# ============================================================
ACEH_KEYWORDS = [
    # Provinsi
    "aceh",
    # Kota/Kabupaten
    "banda aceh", "lhokseumawe", "langsa", "sabang", "subulussalam",
    "meulaboh", "takengon", "bireuen", "sigli", "jantho",
    "blangkejeren", "tapaktuan", "singkil", "kutacane",
    "calang", "sinabang", "suka makmue",
    # Kabupaten (nama resmi)
    "aceh besar", "aceh barat", "aceh utara", "aceh tengah",
    "aceh selatan", "aceh tenggara", "aceh jaya", "aceh timur",
    "aceh tamiang", "aceh singkil", "aceh barat daya",
    "nagan raya", "simeulue", "bener meriah", "gayo lues",
    "pidie", "pidie jaya",
    # Institusi
    "usk", "unsyiah", "unimal", "malikussaleh",
    "iain lhokseumawe", "uin ar-raniry",
    # Budaya/Identitas
    "serambi mekkah", "tanah rencong", "nanggroe",
]

# ============================================================
# BOILERPLATE — Pattern yang harus dihapus dari text
# ============================================================
BOILERPLATE_PATTERNS = [
    "baca juga",
    "baca selengkapnya",
    "baca artikel",
    "simak breaking news",
    "ikuti kami di",
    "google news",
    "download aplikasi",
    "unduh aplikasi",
    "advertisement",
    "iklan",
    "copyright",
    "hak cipta",
    "penulis:",
    "editor:",
    "reporter:",
    "sumber:",
    "tag:",
    "artikel ini telah tayang",
    "dengan judul",
    "bagikan berita ini",
    "kirimkan ke email",
    "follow akun",
    "subscribe",
    "komentar",
    "dapatkan update berita",
    "selengkapnya di",
    "tribunnews.com",
    "antaranews.com",
]

# Minimum karakter agar paragraf dianggap bermakna
MIN_PARAGRAPH_LENGTH = 50

# ============================================================
# ANTARA NEWS — Konfigurasi khusus
# ============================================================
ANTARA_SEARCH_URL = "https://www.antaranews.com/search"
ANTARA_BASE_URL = "https://www.antaranews.com"
ANTARA_ARTICLE_SELECTOR = ".card__post__title a"
ANTARA_CONTENT_SELECTOR = "div.post-content"

# ============================================================
# GOOGLE NEWS RSS — Konfigurasi
# ============================================================
GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"
GOOGLE_NEWS_PARAMS = {
    "hl": "id",
    "gl": "ID",
    "ceid": "ID:id",
}
