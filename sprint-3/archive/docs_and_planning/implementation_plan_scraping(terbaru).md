# Plan Implementasi: Scraping Web Berita — Ekosistem Startup Aceh

**Pelaksana**: Aulia (scraping & labeling untuk semua wilayah)
**Timeframe konten**: 2021–2026 (5 tahun terakhir)
**Target output**: 60–400 text relevan dari berita online

---

## Arsitektur Scraping (3 Layer)

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: DISCOVERY — Cari artikel yang relevan          │
│  Google News RSS → daftar URL artikel                    │
│  Antara Search   → daftar URL artikel                    │
│  Manual seed     → URL yang sudah diketahui              │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: EXTRACTION — Ambil konten dari setiap URL      │
│  Antara parser   → untuk antaranews.com                  │
│  newspaper3k     → untuk portal berita lainnya           │
│  Tribun parser   → khusus tribunnews.com (perlu browser) │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: CLEANING & STORAGE — Bersihkan dan simpan      │
│  Hapus duplikat, pecah per paragraf, simpan ke CSV        │
└─────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Kenapa 3 layer terpisah?** Supaya kalau satu sumber gagal, yang lain tetap jalan. Junior cukup jalankan script per layer secara berurutan.

---

## LAYER 1: Discovery — Menemukan Artikel Relevan

### Metode 1A: Google News RSS ✅ SUDAH DIVALIDASI

**Ini metode paling powerful**. Google News punya RSS feed yang bisa di-query. Hasilnya sudah terfilter dan relevan.

**URL Pattern**:
```
https://news.google.com/rss/search?q={QUERY}&hl=id&gl=ID&ceid=ID:id
```

**Hasil test live** (31 Agustus 2026):
- Query `startup Aceh OR UMKM digital Aceh` → **35 artikel** ditemukan
- Sumber yang muncul: Kabar Tamiang, Sudut Berita, Diskominfo Banda Aceh, KBA.ONE, NOA.co.id, AcehEkspres.com, Kementerian Komdigi
- Semua sudah **Aceh-specific** karena query-nya sudah mengandung "Aceh"

**Daftar query yang harus dijalankan** (masing-masing jadi 1 RSS call):

| # | Query | Target |
|---|-------|--------|
| 1 | `startup Aceh` | Berita umum startup Aceh |
| 2 | `UMKM digital Aceh` | UMKM yang adopsi digital |
| 3 | `ekonomi digital Aceh` | Kebijakan & perkembangan digital |
| 4 | `inkubator bisnis Aceh` | Program inkubasi |
| 5 | `wirausaha muda Aceh` | Entrepreneur muda |
| 6 | `teknologi informasi Aceh` | Perkembangan IT di Aceh |
| 7 | `startup Banda Aceh` | Spesifik ibu kota |
| 8 | `UMKM Lhokseumawe OR UMKM Meulaboh` | Wilayah luar Banda Aceh |
| 9 | `bisnis digital Langsa OR startup Takengon` | Wilayah luar Banda Aceh |
| 10 | `pelatihan digital Aceh OR bootcamp Aceh` | Program pelatihan |
| 11 | `pendanaan startup Aceh OR investasi Aceh` | Funding & investasi |
| 12 | `komunitas teknologi Aceh` | Komunitas tech |
| 13 | `"Banda Aceh" AND (startup OR digital OR teknologi)` | Broad Banda Aceh |
| 14 | `e-commerce Aceh OR marketplace Aceh` | Digital commerce |
| 15 | `talent digital Aceh OR programmer Aceh OR developer Aceh` | Talent |

**Pseudocode (step-by-step untuk junior)**:

```
LANGKAH 1: Import library
  - import requests
  - import xml.etree.ElementTree as ET  
  - import pandas as pd
  - import time
  - import urllib.parse

LANGKAH 2: Definisikan daftar query
  - queries = ["startup Aceh", "UMKM digital Aceh", ...]
  
LANGKAH 3: Untuk setiap query:
  a. Encode query ke URL: urllib.parse.quote(query)
  b. Buat URL: f"https://news.google.com/rss/search?q={encoded}&hl=id&gl=ID&ceid=ID:id"
  c. GET request dengan headers User-Agent
  d. Parse XML response dengan ET.fromstring(response.content)
  e. Untuk setiap <item> dalam XML:
     - Ambil <title> → judul artikel
     - Ambil <link> → URL artikel (PERHATIAN: ini URL Google redirect, 
       perlu resolve ke URL asli)
     - Ambil <pubDate> → tanggal publish
     - Ambil <source> → nama portal berita
  f. Simpan ke list: {title, url, date, source, query_used}
  g. TUNGGU 2 detik sebelum query berikutnya (time.sleep(2))

LANGKAH 4: Gabungkan semua hasil ke DataFrame
LANGKAH 5: Hapus duplikat berdasarkan URL
LANGKAH 6: Simpan ke CSV: "discovery_articles.csv"
```

**⚠️ PERHATIAN untuk junior**: 
- URL dari Google News RSS adalah redirect URL (dimulai dengan `https://news.google.com/rss/articles/...`). Untuk mendapatkan URL asli, lakukan `requests.get(url, allow_redirects=True)` dan ambil `response.url`.
- Jangan jalankan semua query sekaligus. Beri jeda `time.sleep(2)` antar query.
- Kalau dapat error 429 (too many requests), tunggu 5 menit lalu coba lagi.

**Estimasi yield**: 15 query × 20-50 artikel = **100-400 URL unik** (setelah dedup).

---

### Metode 1B: Antara News Direct Search ✅ SUDAH DIVALIDASI

**URL Pattern**:
```
https://www.antaranews.com/search?q={QUERY}
```

**Hasil test live**:
- Query `startup aceh` → **70 berita** ditemukan  
- CSS Selector yang **confirmed working**: `.card__post__title a`

**Pseudocode**:

```
LANGKAH 1: Import library
  - import requests
  - from bs4 import BeautifulSoup

LANGKAH 2: Definisikan query yang sama seperti Metode 1A

LANGKAH 3: Untuk setiap query:
  a. Buat URL: f"https://www.antaranews.com/search?q={query.replace(' ', '+')}"
  b. GET request dengan headers User-Agent:
     headers = {
       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) 
                      AppleWebKit/537.36 (KHTML, like Gecko) 
                      Chrome/120.0.0.0 Safari/537.36"
     }
  c. Parse HTML: soup = BeautifulSoup(response.content, 'html.parser')
  d. Cari artikel: soup.select('.card__post__title a')
  e. Untuk setiap <a>:
     - title = a.get_text(strip=True)
     - url = a['href']  
     - Jika URL relatif, tambahkan: "https://www.antaranews.com" + url
  f. Simpan ke list
  g. TUNGGU 3 detik

LANGKAH 4: Gabungkan, dedup, simpan ke CSV
```

**⚠️ Pagination**: Antara menampilkan ~20 artikel per halaman. Untuk halaman selanjutnya, cek apakah ada link "next page" di HTML. Jika tidak perlu banyak, halaman pertama sudah cukup.

---

### Metode 1C: Manual Seed URLs

Untuk portal yang sulit di-scrape (Tribunnews, Serambinews), kumpulkan URL secara **manual** melalui Google Search:

```
Buka Google → ketik:
  site:aceh.tribunnews.com startup
  site:aceh.tribunnews.com UMKM digital
  site:aceh.tribunnews.com ekonomi digital
  site:serambinews.com startup
```

Copy-paste URL artikel yang relevan ke spreadsheet/CSV. Ini lebih lambat tapi **pasti berhasil** dan tidak perlu coding.

**Estimasi**: 30-60 menit untuk mengumpulkan 30-50 URL manual.

> [!TIP]
> **Rekomendasi untuk junior**: Mulai dari Metode 1A (Google News RSS) karena paling banyak hasilnya dan paling mudah. Lalu tambahkan dari Metode 1B (Antara). Metode 1C sebagai pelengkap terakhir.

---

## LAYER 2: Extraction — Mengambil Konten Artikel

Setelah punya daftar URL, sekarang ambil isi artikelnya.

### Metode 2A: Antara News Parser ✅ SUDAH DIVALIDASI

Khusus untuk URL dari `antaranews.com`.

**Selector yang confirmed working**:

| Elemen | CSS Selector | Contoh Hasil |
|--------|-------------|--------------|
| **Judul** | `h1` | "Garuda Spark Innovation Hub diluncurkan..." |
| **Tanggal** | `meta[property="article:published_time"]` → atribut `content` | "2026-08-26T13:18:46+07:00" |
| **Isi artikel** | `div.post-content` → semua `<p>` di dalamnya | Paragraf-paragraf artikel |
| **Penulis** | `div.post-content span` atau `meta[name="author"]` | Nama reporter |

**Pseudocode**:

```
FUNGSI extract_antara(url):
  1. GET request dengan headers User-Agent
  2. Cek status_code == 200, jika tidak → skip, catat error
  3. Parse HTML: soup = BeautifulSoup(response.content, 'html.parser')
  4. Ambil judul: soup.find('h1').get_text(strip=True)
  5. Ambil tanggal: 
     meta = soup.find('meta', {'property': 'article:published_time'})
     date = meta['content'] jika meta ada, else "unknown"
  6. Ambil konten:
     content_div = soup.select_one('div.post-content')
     paragraphs = content_div.find_all('p')
     text_list = []
     UNTUK setiap p dalam paragraphs:
       text = p.get_text(strip=True)
       JIKA len(text) > 30:  # skip paragraf pendek (ads, caption)
         text_list.append(text)
  7. Return {title, date, paragraphs: text_list, url, source: "antaranews"}
```

---

### Metode 2B: newspaper3k Universal Parser

Untuk URL dari portal berita **selain Antara** (KBA.ONE, Sudut Berita, Dialeksis, Aceh Ekspres, dll).

**Install**:
```bash
pip install newspaper3k lxml_html_clean
```

**Pseudocode**:

```
FUNGSI extract_generic(url):
  1. import newspaper
  2. article = newspaper.Article(url, language='id')
  3. TRY:
     a. article.download()
     b. article.parse()
     c. title = article.title
     d. date = article.publish_date  # bisa None
     e. text = article.text  # full text otomatis
     f. authors = article.authors
     g. Return {title, date, text, authors, url, source: domain_dari_url}
  4. EXCEPT error:
     a. Catat URL yang gagal ke error_log.csv
     b. Return None
```

> [!WARNING]
> **newspaper3k tidak selalu berhasil**. Beberapa website Indonesia punya struktur HTML yang aneh. Jika gagal extract >30% URL, fallback ke **Metode 2C**.

---

### Metode 2C: Fallback Manual — BeautifulSoup Generic

Jika newspaper3k gagal untuk suatu URL:

```
FUNGSI extract_fallback(url):
  1. GET request
  2. Parse HTML
  3. Ambil judul: soup.find('h1').get_text(strip=True)
  4. Ambil semua paragraf: soup.find_all('p')
  5. Filter paragraf:
     - Buang yang len < 40 karakter (kemungkinan bukan konten)
     - Buang yang mengandung "Baca Juga", "ADVERTISEMENT", "Copyright"
     - Buang yang mengandung "Ikuti kami", "Bagikan"
  6. Gabungkan paragraf yang lolos filter
  7. Return hasilnya
```

---

### Strategi Pemilihan Extractor

```
UNTUK setiap url dalam discovery_articles.csv:
  
  JIKA "antaranews.com" ada di url:
    → gunakan extract_antara(url)         # Metode 2A
  
  LAINNYA:
    → coba extract_generic(url)           # Metode 2B (newspaper3k)
    → JIKA gagal atau text kosong:
       → coba extract_fallback(url)       # Metode 2C
       → JIKA masih gagal:
          → catat ke failed_urls.csv, skip
  
  TUNGGU 2 detik antar request (time.sleep(2))
```

---

## LAYER 3: Cleaning & Storage

### Langkah 3.1 — Pecah Artikel Menjadi Unit Text

Satu artikel berita bisa panjang 10-20 paragraf. Untuk text analysis, kita **pecah per paragraf** yang bermakna.

```
UNTUK setiap artikel yang berhasil di-extract:
  UNTUK setiap paragraf dalam artikel:
    JIKA len(paragraf) >= 50 karakter:   # minimal bermakna
    DAN paragraf BUKAN boilerplate:       # bukan "Baca juga:", dll
      → simpan sebagai 1 row di dataset
      → kolom article_id menghubungkan ke artikel asalnya
```

### Langkah 3.2 — Filter Relevansi Aceh

```
DAFTAR kata_aceh = [
  "aceh", "banda aceh", "lhokseumawe", "meulaboh", "langsa", 
  "takengon", "bireuen", "sigli", "sabang", "jantho",
  "nagan raya", "simeulue", "subulussalam", "aceh besar",
  "aceh barat", "aceh utara", "aceh tengah", "aceh selatan",
  "aceh tenggara", "aceh jaya", "bener meriah", "gayo lues",
  "pidie", "usk", "unsyiah", "malikussaleh"
]

UNTUK setiap row:
  text_lower = text.lower()
  JIKA ada kata dari kata_aceh di text_lower:
    aceh_confidence = "high"
  LAINNYA JIKA judul_artikel mengandung kata_aceh:
    aceh_confidence = "medium"  
  LAINNYA:
    aceh_confidence = "low"  # mungkin tidak relevan
```

### Langkah 3.3 — Hapus Duplikat & Boilerplate

```
HAPUS baris yang:
  - text persis sama (exact duplicate)
  - text terlalu mirip (>90% overlap) → gunakan set(words) comparison sederhana
  - mengandung pola boilerplate:
    "Baca Juga", "Baca juga", "ADVERTISEMENT", "Iklan",
    "Simak breaking news", "Ikuti kami di", "Google News",
    "Copyright", "Hak Cipta", "Penulis:", "Editor:",
    "Tag:", "Sumber:"
```

### Langkah 3.4 — Output Format CSV

**File: `public_text_news_raw.csv`**

| Kolom | Tipe | Contoh | Keterangan |
|-------|------|--------|------------|
| `id` | int | 1 | Auto increment |
| `text` | str | "Akses terhadap pendanaan masih menjadi..." | Paragraf atau kalimat bermakna |
| `article_title` | str | "Garuda Spark Innovation Hub..." | Judul artikel asal |
| `article_url` | str | `https://antaranews.com/berita/...` | URL artikel |
| `source_portal` | str | "antaranews" | Nama portal |
| `publish_date` | str | "2026-08-26" | Tanggal publish (YYYY-MM-DD) |
| `query_used` | str | "startup Aceh" | Query yang menemukan artikel ini |
| `aceh_confidence` | str | "high" | high/medium/low |
| `word_count` | int | 42 | Jumlah kata |
| `collector` | str | "Aulia" | Siapa yang mengumpulkan |

**File: `articles_metadata.csv`** (metadata per artikel)

| Kolom | Tipe | Contoh |
|-------|------|--------|
| `article_id` | int | 1 |
| `title` | str | "Garuda Spark Innovation Hub..." |
| `url` | str | URL lengkap |
| `source_portal` | str | "antaranews" |
| `publish_date` | str | "2026-08-26" |
| `total_paragraphs` | int | 15 |
| `relevant_paragraphs` | int | 8 |
| `extraction_method` | str | "antara_parser" / "newspaper3k" / "fallback" |
| `extraction_status` | str | "success" / "partial" / "failed" |

**File: `failed_urls.csv`** (URL yang gagal)

| Kolom | Contoh |
|-------|--------|
| `url` | URL yang gagal |
| `error` | "timeout" / "403" / "empty_content" |
| `attempted_at` | "2026-09-01 14:00" |

---

## Urutan Eksekusi (Step-by-Step untuk Junior)

### Step 1: Setup Environment (~15 menit)

```bash
# Install Python packages
pip install requests beautifulsoup4 newspaper3k lxml_html_clean pandas

# Buat folder kerja
mkdir -p sprint-3/materi-4/scraping
mkdir -p sprint-3/materi-4/data
```

### Step 2: Jalankan Discovery (~30 menit)

```
Jalankan script discovery (Google News RSS + Antara Search)
→ Output: sprint-3/materi-4/data/discovery_articles.csv
→ Berisi: daftar URL artikel + judul + tanggal + sumber
→ Estimasi: 100-400 URL unik
```

### Step 3: Review Discovery Results (~15 menit)

```
Buka discovery_articles.csv
Scroll dan cek:
  - Apakah judul-judul relevan dengan startup/UMKM/digital Aceh?
  - Hapus manual jika ada yang jelas tidak relevan
  - Tandai yang priority tinggi
```

### Step 4: Jalankan Extraction (~60 menit, mostly waiting)

```
Jalankan script extraction untuk setiap URL di discovery_articles.csv
→ Output: sprint-3/materi-4/data/articles_raw.csv (per paragraf)
→ Output: sprint-3/materi-4/data/articles_metadata.csv
→ Output: sprint-3/materi-4/data/failed_urls.csv
→ Script akan otomatis tunggu 2 detik antar request
```

### Step 5: Cleaning & Filtering (~20 menit)

```
Jalankan script cleaning
→ Hapus duplikat
→ Filter boilerplate
→ Tag aceh_confidence
→ Output: sprint-3/materi-4/data/public_text_news_clean.csv
```

### Step 6: Quick Quality Check (~15 menit)

```
Buka public_text_news_clean.csv
Cek 20 baris secara random:
  - Apakah text bermakna? (bukan boilerplate)
  - Apakah aceh_confidence benar?
  - Apakah ada text aneh/rusak?
Catat jumlah total text → apakah sudah mencapai target?
```

**Total waktu estimasi: ~2.5 jam** (termasuk waktu tunggu script jalan)

---

## Struktur File Output

```
sprint-3/materi-4/
├── scraping/
│   ├── 01_discovery.py          ← Script cari URL artikel
│   ├── 02_extraction.py         ← Script ambil konten artikel
│   ├── 03_cleaning.py           ← Script bersihkan & format
│   └── config.py                ← Daftar query, headers, settings
└── data/
    ├── discovery_articles.csv   ← Hasil discovery (URL + judul)
    ├── articles_raw.csv         ← Paragraf mentah per artikel
    ├── articles_metadata.csv    ← Metadata per artikel
    ├── failed_urls.csv          ← URL yang gagal
    └── public_text_news_clean.csv  ← DATASET FINAL siap labeling ✅
```

---

## Panduan Error Handling untuk Junior

| Error | Penyebab | Solusi |
|-------|----------|--------|
| `ConnectionError` | Internet putus | Cek koneksi, coba lagi |
| `Status 403` | Website memblokir | Ganti User-Agent, atau skip URL ini |
| `Status 429` | Terlalu banyak request | Tunggu 5 menit, naikkan `time.sleep()` |
| `Timeout` | Website lambat | Naikkan timeout ke 30 detik |
| `Empty content` | Konten di-load via JavaScript | Catat ke failed_urls, coba newspaper3k |
| `UnicodeError` | Encoding aneh | Tambahkan `response.encoding = 'utf-8'` |
| `newspaper3k gagal` | Struktur HTML tidak standar | Gunakan fallback BeautifulSoup |

**Prinsip utama**: Jangan berhenti karena satu error. **Skip URL yang bermasalah, catat ke log, lanjut ke URL berikutnya.**

---

## Open Questions

> [!IMPORTANT]
> **1. Apakah mau langsung dibuatkan script Python yang siap jalan?**
> Plan ini berisi pseudocode. Jika sudah di-approve, saya akan buatkan 3 script Python (`01_discovery.py`, `02_extraction.py`, `03_cleaning.py`) yang tinggal `python3 namafile.py` untuk dijalankan.

> [!IMPORTANT]
> **2. Format output final: per-paragraf atau per-artikel?**
> Rekomendasi: **per-paragraf** (1 baris = 1 paragraf bermakna), karena untuk text analysis nanti lebih granular. Tapi kalau tim prefer per-artikel (1 baris = 1 artikel utuh), bisa diubah.

> [!IMPORTANT]
> **3. Tambahan portal berita spesifik?**
> Dari Sprint 1 & 2, apakah ada portal berita Aceh tertentu yang sering dipakai atau sudah dikenal tim? Misal: modusaceh.co, dialeksis.com, lintasgayo.co — bisa ditambahkan scraper khusus.
