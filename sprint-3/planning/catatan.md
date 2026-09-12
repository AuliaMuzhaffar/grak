# 📓 Master Catatan Belajar: Arsitektur, Algoritma, & Studi Kasus Pipeline NLP (Sprint 3)

> **Proyek**: Analisis Ekosistem Startup Aceh 2026  
> **Tujuan Dokumen**: Buku pintar arsitektur sistem end-to-end, penjelasan mendalam "The Why" sebelum "The How", diagram alur data, intuisi matematika tanpa rumus rumit, serta studi kasus nyata dari Fase 1 sampai Fase 3 untuk persiapan interview teknis dan presentasi.

---

# 📑 DAFTAR ISI MASTER

1. [Bagian 1: Arsitektur & Algoritma Fase 1 — Scraping, URL Resolver, & Extraction](#bagian-1-arsitektur--algoritma-fase-1--scraping-url-resolver--extraction)
   - [1.1 Masalah Utama: Mengapa 690 URL Google News Gagal?](#11-masalah-utama-mengapa-690-url-google-news-gagal)
   - [1.2 Diagram Arsitektur Pipeline Fase 1](#12-diagram-arsitektur-pipeline-fase-1)
   - [1.3 Bedah Algoritma `02_resolver.py` (Multi-Strategy Resolver)](#13-bedah-algoritma-02_resolverpy-multi-strategy-resolver)
   - [1.4 Bedah Algoritma `03_extraction.py` (Dual-Engine & Checkpointing)](#14-bedah-algoritma-03_extractionpy-dual-engine--checkpointing)
   - [1.5 Modul Pendukung: Anti-Ban HTTP Client & Structured Logging](#15-modul-pendukung-anti-ban-http-client--structured-logging)
2. [Bagian 2: Arsitektur & Algoritma Fase 2 — Data Cleaning & MinHash LSH Deduplication](#bagian-2-arsitektur--algoritma-fase-2--data-cleaning--minhash-lsh-deduplication)
   - [2.1 Masalah Utama: Mengapa Exact Dedup Saja Gagal? (The "Why")](#21-masalah-utama-mengapa-exact-dedup-saja-gagal-the-why)
   - [2.2 Diagram Arsitektur Pipeline Corong 6-Tahap](#22-diagram-arsitektur-pipeline-corong-6-tahap)
   - [2.3 Intuisi Matematika: Jaccard Similarity & Jebakan O(N^2)](#23-intuisi-matematika-jaccard-similarity--jebakan-on2)
   - [2.4 Solusi Skala Besar: k-Shingling + MinHash + LSH](#24-solusi-skala-besar-k-shingling--minhash--lsh)
   - [2.5 Pembuktian Matematis: Tabel 4 Skenario Tiket Terkecil](#25-pembuktian-matematis-tabel-4-skenario-tiket-terkecil)
   - [2.6 Aceh Context Tagging (Confidence Scoring)](#26-aceh-context-tagging-confidence-scoring)
3. [Bagian 3: Arsitektur & Algoritma Fase 3 — Semi-Automated Labeling & 2-Pass Cascading](#bagian-3-arsitektur--algoritma-fase-3--semi-automated-labeling--2-pass-cascading)
   - [3.1 Masalah Utama: The Labeling Bottleneck & Active Learning](#31-masalah-utama-the-labeling-bottleneck--active-learning)
   - [3.2 Diagram Arsitektur Pipeline 2-Pass Cascading](#32-diagram-arsitektur-pipeline-2-pass-cascading)
   - [3.3 Logika Scoring Multi-Tier & Intuisi Papan Skor](#33-logika-scoring-multi-tier--intuisi-papan-skor)
   - [3.4 Ambang Batas (Thresholding = 3) & Penanganan Skor Seri](#34-ambang-batas-thresholding--3--penanganan-skor-seri)
   - [3.5 Empat (4) Use Case Nyata dari Berita Startup Aceh](#35-empat-4-use-case-nyata-dari-berita-startup-aceh)
   - [3.6 Logika Sentimen Jurnalisme Berita (Threshold >= 2)](#36-logika-sentimen-jurnalisme-berita-threshold--2)
   - [3.7 Teknik Lanjutan: Title-Context & Article-Level Propagation](#37-teknik-lanjutan-title-context--article-level-propagation)
   - [3.8 Proteksi Data Manual (Idempotensi & Data Persistence)](#38-proteksi-data-manual-idempotensi--data-persistence)

---
---

# Bagian 1: Arsitektur & Algoritma Fase 1 — Scraping, URL Resolver, & Extraction

## 1.1 Masalah Utama: Mengapa 690 URL Google News Gagal?

Pada tahap awal proyek (Fase 0), kita mengumpulkan artikel berita melalui Google News RSS berdasarkan berbagai kata kunci seputar startup Aceh.
Dari total **1.350 artikel** yang terdeteksi, scraper awal hanya berhasil mengekstrak **660 artikel** (tingkat keberhasilan hanya 48.9%, dan **690 artikel gagal total**).

### Mengapa Bisa Gagal Sebanyak Itu?
Google News tidak memberikan link langsung ke portal media lokal (seperti `serambinews.com`, `antaranews.com`, atau `dialeksis.com`).
Google News **mengaburkan (*obfuscate*) URL asli** menjadi token terenkripsi yang sangat panjang:
`https://news.google.com/rss/articles/CBMiWWh0dHBzOi8vZGlhbGVrc2lzLmNvbS9la29ub21pL2tlbWVudGVyaWFuLWVrb25vbWkta3JlYXRpZi1sdW5jdXJrYW4tcHJvZ3JhbS1kaWdpdGFs...`

Jika scraper mencoba langsung mendownload halaman HTML dari URL Google News ini:
1. Google mendeteksi bot dan memblokir IP address (*Rate-Limited* / HTTP 429).
2. Terjadi putaran pengalihan tak berujung (*Redirect Loop*).
3. Pustaka scraper biasa seperti `requests.get()` langsung melempar error *Timeout* atau *ConnectionRefused*.

**Solusi Kita di Fase 1**:  
Membangun arsitektur pipeline terpisah dengan **URL Resolver Khusus** dan **Anti-Ban HTTP Client**.

---

## 1.2 Diagram Arsitektur Pipeline Fase 1

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 01_discovery.py (Pencarian Berita via RSS Google News)                     │
│ Query: "startup Aceh", "UMKM digital Aceh", "inkubator bisnis Aceh", dll.  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Output: discovery_articles.csv
                                       ▼ (1.350 URL Google News Terenkripsi)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 02_resolver.py (Multi-Strategy Google News URL Resolver)                    │
│ ├── Strategi 1: Decoding Token via library `googlenewsdecoder`              │
│ ├── Strategi 2: HTTP HEAD Redirection via `lib/http_client.py`              │
│ └── Strategi 3: Regex Meta-Refresh & JavaScript Redirect Sniffer            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Output: resolved_urls.csv
                                       ▼ (URL Asli Bersih: dialeksis.com/..., dll.)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 03_extraction.py (Dual-Engine Fulltext & Paragraph Extractor)               │
│ ├── Checkpoint System (Skip URL yang sudah berhasil, hanya scrape sisanya)  │
│ ├── Mesin 1: `newspaper.Article` (NLP extractor judul, teks, tanggal, auth) │
│ ├── Mesin 2: `BeautifulSoup` (Fallback manual jika newspaper gagal)         │
│ └── Paragraph Splitting: Memecah teks utuh artikel menjadi paragraf mandiri │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Output:
                                       ├── articles_database.csv (1.000+ Artikel)
                                       └── paragraphs_raw.csv (14.818 Paragraf)
```

---

## 1.3 Bedah Algoritma `02_resolver.py` (Multi-Strategy Resolver)

Resolver dirancang dengan konsep *Graceful Degradation* (jika strategi cepat gagal, turun ke strategi cadangan):

1. **Input**: Membaca kolom `link` dari `discovery_articles.csv`.
2. **Pengecekan Awal**: Jika URL sudah merupakan URL portal langsung (bukan awalan `news.google.com`), langsung tandai sebagai `resolved` tanpa komputasi tambahan.
3. **Strategi 1 (Reverse Engineering Token)**:  
   Menggunakan `googlenewsdecoder` untuk membongkar payload base64 biner Google secara offline. Tingkat keberhasilan strategi ini mencapai ~85% dan sangat cepat karena tidak membebani jaringan.
4. **Strategi 2 (Network Redirect Follower)**:  
   Jika decoding token gagal, kirim request HTTP `HEAD` ringan menggunakan `lib/http_client.py` dengan mengikuti header pengalihan (`allow_redirects=True`).
5. **Strategi 3 (DOM Sniffer)**:  
   Jika respons server adalah halaman intermediet, regex mencari script pengalihan: `window.location.replace("URL_ASLI")`.
6. **Hasil**: Tingkat resolusi URL melonjak dari **48.9% menjadi 92.4%**!

---

## 1.4 Bedah Algoritma `03_extraction.py` (Dual-Engine & Checkpointing)

1. **Checkpointing & Fault Tolerance**:  
   Sebelum melakukan request ke internet, skrip membaca `articles_database.csv`. Jika URL sudah pernah diekstrak sebelumnya, skrip langsung melewatinya. Jika listrik mati atau koneksi putus di tengah jalan, proses bisa dilanjutkan seketika tanpa mengulang dari awal.
2. **Dual-Engine Extraction**:
   - Skrip memanggil `newspaper.Article(url)`. Library ini menganalisis struktur HTML dan membersihkan iklan secara otomatis.
   - Jika `article.text` kosong atau kurang dari 100 karakter, fallback aktif: `BeautifulSoup` mencari tag `<article>` atau kumpulan tag `<p>` di dalam `div.content-detail`.
3. **Pemisahan Paragraf (`paragraphs_raw.csv`)**:
   - Teks artikel utuh dipecah berdasarkan pemisah dua baris baru (`\n\n`).
   - Setiap potongan paragraf diberi ID unik: `paragraph_id`.
   - Disimpan bersama metadata judul (`article_title`), portal asal (`source_portal`), dan tanggal terbit (`publish_date`).

---

## 1.5 Modul Pendukung: Anti-Ban HTTP Client & Structured Logging

### A. `lib/http_client.py` (Ketahanan Scraping)
- **User-Agent Rotation**: Menyimpan 10 User-Agent dari browser modern asli (Chrome di macOS/Windows, Safari, Firefox). Setiap request memilih User-Agent secara acak agar server portal berita tidak mencurigai traffic sebagai bot Python.
- **Connection Pooling**: Menggunakan `requests.Session` yang mempertahankan koneksi TCP (*keep-alive*), menghemat latensi handshake TLS hingga 60%.
- **Per-Domain Rate Limiting**: Menjaga jeda waktu (misal 1-2 detik) antar request ke domain yang sama agar tidak membuat server media lokal down (*polite crawling*).
- **Exponential Backoff**: Jika server membalas dengan status 500, 502, atau 503, scraper menunggu $2^n$ detik sebelum mencoba ulang (retry maksimal 3 kali).

### B. `lib/logger.py` (Observabilitas Sistem)
Menyimpan log dalam format **JSONL** (`logs/scraping_YYYY-MM-DD.jsonl`) di mana setiap event pencarian, resolusi URL, dan error tercatat secara terstruktur dengan timestamp dan status error.

---
---

# Bagian 2: Arsitektur & Algoritma Fase 2 — Data Cleaning & MinHash LSH Deduplication

## 2.1 Masalah Utama: Mengapa Exact Dedup Saja Gagal? (The "Why")

Dari Fase 1, kita memperoleh **14.818 paragraf mentah** di `paragraphs_raw.csv`.
Jika data ini langsung dilatih ke model Machine Learning di Fase 4, model akan hancur oleh 3 masalah fatal:
1. **Data Leakage (Kebocoran Data)**: Akibat sindikasi media online Indonesia. Berita yang sama diterbitkan ulang di berbagai portal daerah dengan sedikit perubahan kata pengantar (misal: satu portal menulis *"BANDA ACEH (Antara) -"*, portal lain menulis *"SERAMBINEWS.COM, BANDA ACEH -"*).
2. **Feature Space Poisoning**: Teks navigasi berita (*"Baca Juga"*, *"Simak breaking news"*) jika tidak dibersihkan akan dianggap fitur penting oleh algoritma TF-IDF.
3. **Jebakan O(N^2)**: Membandingkan 14.818 teks secara berpasangan manual membutuhkan **hampir 110 juta kali operasi** (~3 jam lebih di memori).

---

## 2.2 Diagram Arsitektur Pipeline Corong 6-Tahap

Data mentah disaring secara bertahap menggunakan prinsip corong (*funnel filtration*):

```text
[ 14.818 Paragraf Mentah ] (paragraphs_raw.csv)
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 1: Text Normalization                            │
│ → Hapus URL, email, emoji, dan karakter non-printable  │
│ → Rapikan multiple spasi menjadi 1 spasi tunggal       │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 2: Structural Validation Heuristics              │
│ → Panjang kata: 5 - 500 kata                           │
│ → Rasio alfabet minimal 50% (bukan angka/simbol acak)  │
│ → Minimal 3 kata unik (bukan teks berulang)            │
│ → Panjang karakter minimal 50 karakter                 │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 3: Boilerplate Stripping                         │
│ → Hapus 60+ pola noise media: "baca juga", "penulis:" │
│ → Hapus pola navigasi foto, pagination, dsb.           │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 4: Exact Deduplication (O(N))                    │
│ → Hapus teks yang 100% sama persis                     │
│ → Cukup simpan kemunculan pertama                      │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 5: Near-Duplicate Detection (MinHash LSH)        │
│ → Deteksi kemiripan teks >= 85% via 3-shingles         │
│ → Tangani sindikasi berita dan parafrase editorial    │
│ → Waktu eksekusi turun dari 3 jam ke 15 detik!         │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 6: Aceh Context Tagging                          │
│ → Klasifikasi confidence: HIGH, MEDIUM, LOW            │
│ → Berdasarkan kemunculan kata kunci di teks vs judul   │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
[ 13.840 Paragraf Bersih Siap ML ] (public_text_news_clean.csv)
```

---

## 2.3 Intuisi Matematika: Jaccard Similarity & Jebakan O(N^2)

### Konsep Jaccard Similarity
Kemiripan antara Dokumen A dan B diukur dari jumlah kata irisan dibagi jumlah total kata gabungan:
$$\text{Jaccard}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

### Jebakan Perhitungan Berpasangan O(N^2)
Jika kita membandingkan $N = 14.818$ dokumen satu per satu:
$$\text{Total Pasangan} = \frac{N \times (N - 1)}{2} = \frac{14.818 \times 14.817}{2} = 109.779.153\text{ perbandingan!}$$

Inilah alasan mengapa script lama (`03_cleaning.py`) terpaksa men-skip deteksi near-duplicate jika datanya lebih dari 2.000 baris. Komputer tidak sanggup memproses 110 juta perbandingan teks secara berpasangan.

---

## 2.4 Solusi Skala Besar: k-Shingling + MinHash + LSH

Untuk memproses 14.818 data dalam hitungan **detik**, kita menggunakan algoritma yang dipatenkan oleh Andrei Broder (digunakan di Google dan Twitter):

### 1. k-Shingling (k=3)
Memecah kalimat menjadi potongan 3 kata berurutan agar konteks dan susunan frasa tidak hilang.  
Contoh: *"Pemerintah Aceh dukung startup"* $\rightarrow$ `["pemerintah aceh dukung", "aceh dukung startup"]`.

### 2. MinHash (Kompresi Vektor Ekstrem)
Alih-alih menyimpan ribuan string frasa, setiap teks dikompresi menjadi **Signature Vector berisi 128 angka integer** melalui 128 fungsi hash acak yang berbeda.  
Sifat ajaib MinHash:
$$\Pr[\text{MinHash}(A) = \text{MinHash}(B)] = \text{Jaccard}(A, B)$$
Peluang angka hash terkecil bernilai sama persis sama dengan persentase kemiripan teks aslinya!

### 3. LSH (Locality-Sensitive Hashing)
128 angka MinHash dibagi menjadi **16 Bands** (masing-masing band berisi 8 angka).
- Dua dokumen yang mirip $\ge 85\%$ dipastikan memiliki potongan 8 angka yang identik di minimal salah satu Band, sehingga otomatis **jatuh ke dalam keranjang (bucket) yang sama**.
- Komputer **HANYA** membandingkan dokumen yang berada di keranjang yang sama, dan mengabaikan jutaan pasang dokumen lainnya!
- Kompleksitas waktu komputasi terpangkas dari **$O(N^2)$ menjadi mendekati $O(N)$**.

---

## 2.5 Pembuktian Matematis: Tabel 4 Skenario Tiket Terkecil

Bayangkan kita punya dua dokumen:
- **Dokumen A**: `[kopi, aceh, gayo]` (3 kata)
- **Dokumen B**: `[kopi, aceh, enak]` (3 kata)
- Irisan (kata sama): `[kopi, aceh]` = 2 kata.
- Gabungan (kata unik total): `[kopi, aceh, gayo, enak]` = 4 kata.
- Kemiripan asli Jaccard: $2 / 4 = 0.5$ (**50%**).

Mesin hash mengocok ke-4 kata tersebut dan memberikan nomor tiket acak. Siapa pun kata yang memegang nomor tiket terkecil menjadi Juara 1:

| Skenario | Pemenang Tiket Terkecil | Kata Terkecil Dok A | Kata Terkecil Dok B | Apakah Nilai MinHash A dan B Sama? |
|:---:|:---:|:---:|:---:|:---:|
| **Skenario 1** | Kata **`kopi`** menang (tiket 5) | `kopi` (5) | `kopi` (5) | **SAMA ✅** (karena `kopi` ada di A dan B) |
| **Skenario 2** | Kata **`aceh`** menang (tiket 8) | `aceh` (8) | `aceh` (8) | **SAMA ✅** (karena `aceh` ada di A dan B) |
| **Skenario 3** | Kata **`gayo`** menang (tiket 2) | `gayo` (2) | `kopi`/`aceh` (lebih besar) | **BEDA ❌** (karena `gayo` hanya ada di A) |
| **Skenario 4** | Kata **`enak`** menang (tiket 1) | `kopi`/`aceh` (lebih besar) | `enak` (1) | **BEDA ❌** (karena `enak` hanya ada di B) |

> 💡 **Kesimpulan Matematis**:  
> Dari 4 kemungkinan pemenang, ada **2 skenario bernilai SAMA** (Skenario 1 & 2).  
> Peluang nilainya sama = $2 / 4 = \mathbf{50\%}$!  
> Angka ini **PERSIS SAMA** dengan persentase kemiripan teks aslinya (**50%**).

---

## 2.6 Aceh Context Tagging (Confidence Scoring)

Tidak semua paragraf menyebut kata "Aceh" secara eksplisit. Jika kita menghapus semua teks tanpa kata "Aceh", maka kutipan berharga tentang mentoring atau product-market fit di dalam artikel lokal Aceh akan terbuang.
Oleh karena itu kita membuat tingkatan relevansi:

| Level | Aturan Logika | Makna Bisnis |
|---|---|---|
| **HIGH** | Teks paragraf itu sendiri menyebut kata "Aceh", "Banda Aceh", "USK", "Gayo", dll. | Paragraf 100% spesifik berbicara tentang wilayah Aceh. |
| **MEDIUM** | Teks paragraf tidak menyebut Aceh, TETAPI judul artikelnya menyebut Aceh. | Paragraf adalah bagian integral dari artikel lokal Aceh. |
| **LOW** | Teks paragraf DAN judul artikel sama-sama tidak menyebut kata kunci Aceh. | Kemungkinan berita nasional yang tersaring saat pencarian awal. |

---
---

# Bagian 3: Arsitektur & Algoritma Fase 3 — Semi-Automated Labeling & 2-Pass Cascading

## 3.1 Masalah Utama: The Labeling Bottleneck & Active Learning

Di Fase 4 nanti, kita akan melatih model Supervised Learning (Multi-class Classifier untuk Topik dan Classifier untuk Sentimen). Syarat mutlaknya adalah tersedianya **Ground Truth Label**.
- Melabeli **13.840 baris secara manual** butuh waktu:
  $$13.840 \times 30\text{ detik} = 415.200\text{ detik} \approx \mathbf{115\text{ jam kerja}} \ (\sim 14\text{ hari kerja!})$$
- Melabeli pakai LLM API (GPT-4 / Claude) memakan biaya token tinggi, berisiko rate limit, dan bersifat *black-box* (tidak bisa diaudit).

**Solusi Kita**: Programmatic Weak Supervision + Human-in-the-Loop (Active Learning):
1. Mesin melabeli otomatis data yang berkarakteristik tegas.
2. Manusia memusatkan waktu hanya untuk meninjau data yang ambigu (`needs_review.csv`).
3. Waktu kerja terpangkas dari **14 hari menjadi 2 jam saja**!

---

## 3.2 Diagram Arsitektur Pipeline 2-Pass Cascading

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             labeling_rules.py                                    │
│  (Kamus Aturan Deklaratif: TOPIC_RULES, SENTIMENT_RULES, Thresholds)             │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ di-import ke
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                               05_labeling.py                                     │
│                                                                                  │
│   INPUT:                                                                         │
│   └── public_text_news_clean.csv (13.840 baris bersih Fase 2)                    │
│                                                                                  │
│   TAHAP 1: Inisialisasi & Cek Label Manual (Data Persistence)                   │
│   ├── Load 13.840 baris data                                                     │
│   └── Cek manual_cache dari needs_review.csv (amankan label manual)             │
│                                                                                  │
│   TAHAP 2: PASS 1 — Direct Paragraph Keyword Matching                            │
│   ├── Untuk setiap baris teks:                                                   │
│   │   ├── Ubah teks ke huruf kecil (text_lower)                                  │
│   │   ├── Cek kata kunci:                                                        │
│   │   │   ├── Panjang <= 3 huruf ──► Regex Word Boundary (\b) [Anti-Salah]       │
│   │   │   └── Panjang > 3 huruf  ──► Substring check biasa                       │
│   │   ├── Akumulasi Skor: (Strong × 3) + (Medium × 2) + (Weak × 1)               │
│   │   ├── Cek Quality Gate: Skor Tertinggi >= 3?                                 │
│   │   │   ├── YA (Tidak Seri) ──► Topic = Best Topic | Method = "auto"           │
│   │   │   └── TIDAK / SERI    ──► Topic = ""         | Method = "needs_review"   │
│   │   └── Hitung Sentimen: Positif vs Negatif (Threshold >= 2)                   │
│   └── Hasil Pass 1: 5.973 baris "auto" | 7.867 baris "needs_review"              │
│                                                                                  │
│   TAHAP 3: PASS 2 — Context Propagation (Hanya untuk yang "needs_review")        │
│   ├── Mekanisme 1: Article Majority Rule                                         │
│   │   └── Jika saudara 1 artikel punya mayoritas topik >= 50%:                   │
│   │       └── Wariskan topik! Method = "article_propagated" (+5.617 baris)       │
│   └── Mekanisme 2: Title Fallback Scoring                                        │
│       └── Jika judul artikel punya skor topik >= 3:                              │
│           └── Wariskan topik! Method = "title_propagated" (+388 baris)           │
│                                                                                  │
│   TAHAP 4: Pemisahan Data & Ekspor File                                          │
│   ├── labeled_dataset.csv (13.840 baris — SEMUA data + status metodenya)         │
│   ├── auto_labeled.csv    (11.978 baris — 86.5% confident untuk spot check)      │
│   ├── needs_review.csv    ( 1.862 baris — 13.5% unclassified untuk human review) │
│   └── label_stats.json    (Ringkasan metrik kuantitatif & distribusi)            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3.3 Logika Scoring Multi-Tier & Intuisi Papan Skor

Mengapa tidak pakai `if "bisnis" in text` biasa?  
Karena kata umum seperti *"bisnis"* atau *"uang"* bisa muncul di berita seminar kedokteran dan memicu **False Positive**.

Kita membagi kata kunci ke dalam **3 Tier Poin (Papan Skor)**:
- 🥇 **Strong (3 Poin)**: Sangat spesifik. Sekali muncul, hampir pasti ini topiknya (`"modal ventura"`, `"angel investor"`, `"bootcamp"`).
- 🥈 **Medium (2 Poin)**: Relevan, tapi butuh konteks pendukung (`"modal"`, `"pelatihan"`, `"pasar"`, `"aturan"`).
- 🥉 **Weak (1 Poin)**: Kata umum. Hanya pelengkap, dilarang menang sendirian (`"uang"`, `"bisnis"`, `"acara"`, `"modern"`).

### Rumus Perhitungan Skor Topik:
$$\text{Skor Topik } k = (3 \times N_{\text{strong}}) + (2 \times N_{\text{medium}}) + (1 \times N_{\text{weak}})$$

---

## 3.4 Ambang Batas (Thresholding = 3) & Penanganan Skor Seri

$$\text{TOPIC\_MIN\_SCORE} = 3$$

> 🛡️ **Aturan Ambang Batas**:  
> *"Sebuah topik baru boleh dinyatakan menang dan otomatis dilabeli jika perolehan skornya **minimal 3 poin**! Jika skor tertinggi < 3, mesin angkat tangan (Unclassified) dan menyerahkannya ke manusia di `needs_review.csv`."*

### Tabel Skenario Kelolosan Ambang Batas:
| Kombinasi Kata yang Ditemukan | Hitungan Poin | Skor Akhir | Lolos Threshold ($\ge 3$)? | Keputusan Mesin |
|---|:---:|:---:|:---:|---|
| **1 kata Strong** (misal: `"modal ventura"`) | $1 \times 3$ | **3** | **YA ✅** | Auto-label langsung sebagai `funding` |
| **1 kata Medium + 1 kata Weak** (misal: `"modal"` + `"bisnis"`) | $2 + 1$ | **3** | **YA ✅** | Auto-label langsung sebagai `funding` |
| **2 kata Medium** (misal: `"pelatihan"` + `"skill"`) | $2 + 2$ | **4** | **YA ✅** | Auto-label langsung sebagai `talent` |
| **2 kata Weak saja** (misal: `"uang"` + `"bisnis"`) | $1 + 1$ | **2** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |
| **1 kata Medium saja** (misal: `"pasar"`) | $1 \times 2$ | **2** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |
| **Tidak ada kata kunci cocok** | 0 | **0** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |

### Penanganan Skor Seri (Tie-Break Opsi B - Active Learning)
Jika ada dua topik yang skornya sama-sama tertinggi (misal `funding` = 4 dan `talent` = 4), komputer tidak boleh menebak secara acak. Kasus seri ini dianggap ambigu dan langsung dialirkan ke `needs_review.csv` untuk diputuskan oleh manusia.

---

## 3.5 Empat (4) Use Case Nyata dari Berita Startup Aceh

### 📌 Use Case 1: Kemenangan Telak Satu Topik (Clear Winner)
> **Teks**: *"Startup agritech asal Banda Aceh berhasil mengamankan **seed funding** sebesar 1,5 Miliar Rupiah dari konsorsium **angel investor** Jakarta. Dana ini akan digunakan sebagai **modal** ekspansi."*
- Papan Skor `funding`: Strong: `"seed funding"` (3) + `"angel investor"` (3) + Medium: `"modal"` (2) = **8 poin**.
- Keputusan: Skor 8 ($\ge 3$) $\rightarrow$ ✅ **Auto-label: `funding`**.

### 📌 Use Case 2: Persaingan Sengit Antar-Topik (Competition & $\arg\max$)
> **Teks**: *"Dinas Koperasi Aceh menggelar program **inkubator bisnis** bersama **komunitas startup**. Di dalamnya, para founder diberikan **pelatihan** validasi ide bisnis digital."*
- Papan Skor: `ecosystem` (6 poin), `talent` (2 poin), `digitalization` (2 poin).
- Keputusan: `ecosystem` menang mutlak $\rightarrow$ ✅ **Auto-label: `ecosystem`**.

### 📌 Use Case 3: Penyelamatan dari Jebakan False Positive (Quality Gate Rejection)
> **Teks**: *"Bupati Aceh Besar secara resmi membuka **acara** perayaan hari ulang tahun kota yang dihadiri ratusan warga di lapangan terbuka."*
- Papan Skor: `ecosystem` hanya mendapat Weak: `"acara"` (1 poin).
- Evaluasi: $1 < 3$ (**GAGAL**).
- Keputusan: 🛡️ **Tolak Auto-label! Label = `"unclassified"` $\rightarrow$ Dialirkan ke `needs_review.csv`**.

### 📌 Use Case 4: Skenario Skor Imbang / Seri (Tie-Break Dilemma)
> **Teks**: *"Pemerintah meluncurkan program **subsidi modal** untuk pelaku usaha sekaligus menyediakan sertifikasi **keterampilan digital** bagi para pemuda."*
- Papan Skor: `funding` (4 poin) == `talent` (4 poin).
- Keputusan: ⚠️ **Dialirkan ke `needs_review.csv`** agar manusia membaca konteks kalimat utuhnya.

---

## 3.6 Logika Sentimen Jurnalisme Berita (Threshold >= 2)

Berita media Indonesia menggunakan gaya bahasa formal dan diplomatis. Satu kata positif seperti *"menyambut baik"* sering kali hanya basa-basi protokoler pidato.

### Aturan Keputusan Sentimen:
1. Hitung jumlah kata positif ($N_{\text{pos}}$) dan negatif ($N_{\text{neg}}$).
2. Jika $N_{\text{pos}} > N_{\text{neg}}$ **DAN** $N_{\text{pos}} \ge 2 \implies \mathbf{positive}$
3. Jika $N_{\text{neg}} > N_{\text{pos}}$ **DAN** $N_{\text{neg}} \ge 2 \implies \mathbf{negative}$
4. Jika selisihnya tidak signifikan atau keduanya $< 2 \implies \mathbf{neutral}$

---

## 3.7 Teknik Lanjutan: Title-Context & Article-Level Propagation

### Masalah: Paragraf Pendek Tanpa Kata Kunci
```text
Judul Artikel: 
"BSI Salurkan KUR Rp1,5 Triliun untuk UMKM di Banda Aceh"

├── Paragraf 1: "...menyalurkan KUR sebesar Rp1,5 triliun..." ──► Skor 8 -> Auto: 'funding'
├── Paragraf 2: "...membantu pelaku usaha lokal..."          ──► Skor 2 -> Masuk needs_review
└── Paragraf 3: "...dilaksanakan mulai awal bulan depan..."   ──► Skor 0 -> Masuk needs_review
```
Paragraf 3 sendirian tidak punya kata kunci. Tetapi kita tahu 100% topiknya adalah `funding` karena judul dan artikelnya!

### Cascading Strategy di Pass 2:
1. **Mekanisme 1 (Article Majority)**: Jika $\ge 50\%$ paragraf berlabel di artikel tersebut adalah `funding`, paragraf tak berlabel mewarisi topik tersebut (`article_propagated`).
2. **Mekanisme 2 (Title Fallback)**: Jika paragraf belum berlabel dan tidak ada mayoritas, periksa kata kunci pada judul artikel (`article_title`). Jika judul memiliki skor $\ge 3$, wariskan topik judul tersebut (`title_propagated`).

Hasilnya: Tingkat kelengkapan auto-label melonjak dari **43.2% menjadi 86.5%**!

---

## 3.8 Proteksi Data Manual (Idempotensi & Data Persistence)

### Mengapa Sangat Kritis?
Jika kamu sudah memeriksa dan mengisi 50 baris di `needs_review.csv`, lalu kamu menambah kata kunci baru di `labeling_rules.py` dan menjalankan ulang `05_labeling.py`:
- Tanpa proteksi: 50 baris ketikan manualmu akan terhapus tertimpa file baru!
- **Dengan Proteksi Sistem Kita**:
  Skrip menyimpan cache dari `needs_review.csv`:
  ```python
  if p_id in manual_cache:
      labeled_row["topic"] = m_data["topic"]
      labeled_row["topic_method"] = "manual"
      labeled_row["topic_score"] = -1.0  # Penanda keputusan manusia
  ```
  Skrip melewati kalkulasi kata kunci dan **mempertahankan label manualmu 100% utuh**, menjamin keamanan pekerjaan analisis kamu kapan pun skrip di-run ulang!

---
*Dokumen ini merupakan panduan master resmi arsitektur dan algoritma Sprint 3 GRAK 2026.*
