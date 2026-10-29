# Plan Detail: Scraping Public Text — 4 Platform

## Problem Statement

> **Masalah utama**: Kita riset ekosistem startup **Aceh**, tapi komentar di social media bersifat **general Indonesia**. Misalnya, video "Tantangan Startup Indonesia" akan punya komentar dari orang Jakarta, Surabaya, dll — **bukan perspektif Aceh**.

Ini bukan masalah kecil. Kalau kita asal ambil komentar dari video bertema "startup Indonesia", dataset kita akan berisi opini orang seluruh Indonesia — bukan mendengarkan suara ekosistem Aceh.

---

## Strategi Mengatasi Bias: 3 Lapis Filter

### Lapis 1 — Search Query yang Aceh-Specific

Jangan cari konten general. Cari konten yang **sudah** membahas Aceh.

| ✅ Query yang Aceh-Specific | ❌ Query yang Terlalu General |
|---|---|
| `startup Aceh` | `startup Indonesia` |
| `UMKM digital Banda Aceh` | `UMKM digital` |
| `inkubator bisnis Aceh` | `inkubator bisnis` |
| `founder Aceh` | `founder Indonesia` |
| `teknologi Aceh` | `teknologi startup` |
| `ekonomi digital Aceh` | `ekonomi digital Indonesia` |

**Keyword pool** yang direkomendasikan:

```
PRIMARY (wajib ada "Aceh"):
- startup Aceh, startup Banda Aceh
- UMKM digital Aceh, bisnis digital Aceh
- founder Aceh, wirausaha muda Aceh
- ekonomi digital Aceh, ekosistem startup Aceh
- inkubator Aceh, akselerator Aceh
- teknologi Aceh, tech Aceh

SECONDARY (nama kota/kabupaten):
- startup Lhokseumawe, UMKM Meulaboh
- bisnis digital Langsa, startup Takengon
- ekonomi kreatif Aceh Besar

TERTIARY (institusi/program lokal):
- [nama inkubator lokal] + startup
- [nama program pemerintah Aceh] + digital
- [nama event/komunitas lokal]
```

### Lapis 2 — Source Curation (Akun & Kreator Lokal Aceh)

Selain keyword search, kita **langsung pergi ke sumbernya** — akun/channel yang memang membahas Aceh.

| Platform | Tipe Akun/Channel Target |
|---|---|
| **YouTube** | Channel berita lokal Aceh (Serambi TV, Aceh TV, dll), vlog founder Aceh, channel pemerintah Aceh |
| **TikTok** | Kreator konten Aceh, akun bisnis lokal Aceh, akun pemerintah daerah |
| **Instagram** | Akun komunitas startup Aceh, akun inkubator kampus (USK, Malikussaleh, dll), akun dinas terkait |
| **Web Berita** | Serambinews.com, aceh.tribunnews.com, modusaceh.co, dialeksis.com |

> [!TIP]
> **Ini approach paling aman**. Komentar di video Serambi TV tentang "UMKM digital Aceh" hampir pasti dari orang yang berkaitan dengan Aceh — jauh lebih reliable daripada keyword filtering dari video nasional.

### Lapis 3 — Post-Collection Filtering & Tagging

Setelah data terkumpul, validasi lagi:

| Filter | Cara | Tujuan |
|---|---|---|
| **Aceh-mention check** | Cek apakah text menyebut lokasi/konteks Aceh | Buang yang benar-benar irrelevant |
| **Source tag** | Tag setiap text: `aceh_specific` vs `general_indonesia` | Bisa dianalisis terpisah |
| **Confidence level** | High (dari akun lokal Aceh) / Medium (keyword match) / Low (general) | Transparansi kualitas data |
| **Manual review sample** | Review 20% secara manual | Validasi pipeline |

---

## Detail per Platform

### 1. YouTube

**Apa yang diambil**: Komentar dari video yang membahas startup/UMKM/ekonomi digital Aceh.

**Strategi pencarian video**:
```
Tier 1 — Channel lokal Aceh (HIGH confidence):
  → Cari channel berita Aceh, lalu ambil video tentang startup/UMKM/ekonomi digital
  → Contoh: Serambi TV, Aceh TV, channel pemerintah Aceh
  
Tier 2 — Search keyword Aceh-specific (MEDIUM confidence):
  → YouTube search: "startup Aceh", "UMKM digital Banda Aceh", dll
  → Filter: hanya video yang judulnya menyebut Aceh
  
Tier 3 — Video nasional tapi ada segment Aceh (LOW confidence):
  → Video "startup daerah Indonesia" yang menyebut Aceh
  → Harus di-tag sebagai lower confidence
```

**Tools**:
| Tool | Kelebihan | Kekurangan |
|---|---|---|
| `youtube-comment-downloader` (Python pip) | Gratis, tanpa API key, unlimited | Kadang break jika YouTube update |
| YouTube Data API v3 | Resmi, stabil | Quota 10,000 units/hari, perlu API key |
| Manual export (copy-paste) | Paling simpel | Lambat, tidak scalable |

**Rekomendasi**: Gunakan `youtube-comment-downloader` sebagai primary, YouTube API sebagai fallback.

**Estimasi yield**: 10-20 video relevan × 20-100 komentar = **200-2000 komentar mentah**, setelah filter → **50-300 text relevan**.

---

### 2. TikTok

**Apa yang diambil**: Komentar dari video TikTok tentang bisnis/startup di Aceh + caption video itu sendiri.

**Strategi pencarian**:
```
Tier 1 — Akun kreator lokal Aceh (HIGH confidence):
  → Cari kreator TikTok Aceh yang membahas bisnis/startup
  → Hashtag: #startupaceh #umkmaceh #bisnisaceh #aceh
  
Tier 2 — Hashtag search (MEDIUM confidence):
  → #startupaceh, #umkmdigitalaceh, #founderaceh
  → #bandaaceh + bisnis/startup
  
Tier 3 — Sound/trend + Aceh filter (LOW confidence):
  → Trend "cerita founder" yang kebetulan dari Aceh
```

**Tools**:
| Tool | Kelebihan | Kekurangan |
|---|---|---|
| Apify TikTok Scraper | Paling reliable, headless browser | Berbayar ($5 free tier cukup) |
| `TikTokApi` (Python) | Gratis | Sering break, butuh `playwright` |
| Manual screenshot + entry | Pasti dapat data | Sangat lambat |

**Rekomendasi**: Apify free tier (cukup untuk volume kita) atau manual collection jika volume kecil.

**Estimasi yield**: 15-30 video × 10-50 komentar = **150-1500 mentah**, setelah filter → **30-200 text relevan**.

> [!WARNING]
> **TikTok adalah platform paling tricky untuk scraping**. API mereka sangat restriktif. Jika tools tidak bekerja, fallback ke manual collection: screenshot → ketik ulang komentar ke spreadsheet. Ini lebih lambat tapi pasti jalan.

---

### 3. Instagram

**Apa yang diambil**: Komentar post dan caption dari akun yang membahas startup/UMKM Aceh.

**Strategi pencarian**:
```
Tier 1 — Akun institusi/komunitas Aceh (HIGH confidence):
  → Akun inkubator kampus (USK, dll)
  → Akun komunitas startup Aceh
  → Akun dinas/pemerintah Aceh terkait ekonomi digital
  → Akun event startup lokal
  
Tier 2 — Hashtag Aceh-specific (MEDIUM confidence):
  → #startupaceh #umkmaceh #bisnisdigitalaceh
  → #ekonomidigitalaceh #founderaceh
  
Tier 3 — Akun founder Aceh individual (HIGH confidence):
  → Founder yang sudah diidentifikasi di Sprint 1 & 2
  → Post mereka tentang pengalaman berbisnis di Aceh
```

**Tools**:
| Tool | Kelebihan | Kekurangan |
|---|---|---|
| Apify Instagram Scraper | Reliable, bisa komentar + caption | Berbayar (free tier terbatas) |
| `instaloader` (Python) | Gratis, bisa post + komentar | Perlu login, risk ban |
| Manual screenshot + entry | Aman, tanpa risk | Lambat |

**Rekomendasi**: Kombinasi `instaloader` untuk public posts + manual untuk komentar penting.

**Estimasi yield**: 20-40 post × 5-30 komentar = **100-1200 mentah**, setelah filter → **30-150 text relevan**.

---

### 4. Web Berita

**Apa yang diambil**: Paragraf artikel + komentar berita (jika ada) tentang startup/UMKM Aceh.

**Strategi pencarian**:
```
Tier 1 — Portal berita lokal Aceh (HIGH confidence):
  → serambinews.com → search "startup", "UMKM digital", "ekonomi digital"
  → aceh.tribunnews.com → search "startup", "bisnis digital"
  → modusaceh.co, dialeksis.com
  → acehterkini.com, acehtrend.com
  
Tier 2 — Portal berita nasional + filter Aceh (MEDIUM confidence):
  → detik.com, kompas.com, cnnindonesia.com
  → Search: "startup Aceh", "UMKM digital Aceh"
  
Tier 3 — Google News search (MEDIUM confidence):
  → Query: "startup Aceh" OR "UMKM digital Aceh" OR "ekonomi digital Aceh"
  → Filter: 1-2 tahun terakhir
```

**Tools**:
| Tool | Kelebihan | Kekurangan |
|---|---|---|
| `requests` + `BeautifulSoup` | Gratis, full control | Perlu tulis parser per website |
| `newspaper3k` (Python) | Auto-extract article body | Kadang gagal di situs Indo |
| `Scrapy` | Industrial-grade, async | Overkill untuk volume kita |
| Google News RSS | Gratis, terstruktur | Terbatas jumlahnya |

**Rekomendasi**: `requests` + `BeautifulSoup` untuk 2-3 portal berita utama + `newspaper3k` sebagai helper.

**Estimasi yield**: 30-80 artikel × 2-5 paragraf relevan per artikel = **60-400 text relevan**.

> [!TIP]
> **Web berita adalah sumber paling reliable dan paling Aceh-specific**, karena portal berita lokal Aceh memang hanya membahas Aceh. Ini seharusnya jadi **prioritas scraping pertama**.

---

## Prioritas Scraping (Rekomendasi Urutan)

| Prioritas | Platform | Alasan |
|---|---|---|
| 🥇 **Pertama** | **Web Berita** | Paling Aceh-specific, paling reliable tool-nya, paling mudah di-scrape |
| 🥈 **Kedua** | **YouTube** | Banyak konten berita lokal Aceh di YouTube, tools cukup stabil |
| 🥉 **Ketiga** | **Instagram** | Bagus untuk komentar komunitas, tapi tools lebih tricky |
| 4️⃣ **Keempat** | **TikTok** | Paling sulit di-scrape, tapi bisa dapat perspektif anak muda |

---

## Pipeline Output: Format Dataset Standar

Setiap text yang dikumpulkan harus disimpan dengan format kolom ini:

| Kolom | Tipe | Contoh |
|---|---|---|
| `id` | int | 1, 2, 3, ... |
| `text` | str | "Susah cari developer di Banda Aceh" |
| `source` | str | "youtube_comment", "tiktok_comment", "news_article", "instagram_comment" |
| `platform` | str | "youtube", "tiktok", "instagram", "news" |
| `source_url` | str | URL video/post/artikel |
| `source_title` | str | Judul video/post/artikel |
| `source_account` | str | Nama channel/akun/portal |
| `date` | str | "2026-08-15" (jika tersedia) |
| `aceh_confidence` | str | "high", "medium", "low" |
| `collector` | str | "Aulia", "Taris", "Anum", "Neni" |
| `notes` | str | Catatan tambahan |

> [!IMPORTANT]
> **Kolom `aceh_confidence`** adalah kunci menjaga kualitas data. Setiap text di-tag seberapa yakin kita bahwa text ini benar-benar membahas/berkaitan dengan konteks Aceh.

---

## Estimasi Total Yield

| Platform | Mentah | Setelah Filter | Confidence Level |
|---|---|---|---|
| Web Berita | 60-400 | **60-400** | Mostly HIGH |
| YouTube | 200-2000 | **50-300** | Mix HIGH-MEDIUM |
| Instagram | 100-1200 | **30-150** | Mix HIGH-MEDIUM |
| TikTok | 150-1500 | **30-200** | Mix MEDIUM-LOW |
| **Total** | **510-5100** | **170-1050** | — |

Target Sprint 3: **300+ text samples** → achievable jika web berita + YouTube berjalan baik.

---

## Open Questions

> [!IMPORTANT]
> **1. Akun/channel lokal Aceh yang sudah dikenal?**
> Apakah dari Sprint 1 & 2 sudah ada daftar akun Instagram komunitas startup Aceh, channel YouTube berita lokal, atau portal berita yang sering dipakai? Ini bisa langsung jadi Tier 1 sources.

> [!IMPORTANT]
> **2. Apify free tier atau full manual?**
> Apify punya free tier $5/bulan yang cukup untuk TikTok dan Instagram scraping. Apakah tim bersedia pakai, atau prefer full manual collection?

> [!IMPORTANT]
> **3. Pembagian scraping per peneliti?**
> Apakah scraping dibagi per platform (misal: Aulia YouTube, Taris Instagram) atau per wilayah (setiap orang scrape semua platform untuk wilayahnya masing-masing)?

> [!IMPORTANT]
> **4. Timeframe konten yang diambil?**
> Apakah kita ambil konten dari kapan sampai kapan? Rekomendasi: **2024-2026** (2 tahun terakhir) agar tetap relevan. Terlalu jauh ke belakang, kondisi ekosistem mungkin sudah berubah.

---

## Verification Plan

### Setelah Scraping Selesai
- [ ] Setiap text punya `source_url` yang bisa diverifikasi
- [ ] Tidak ada duplikat (cek `text` column)
- [ ] Distribusi platform: minimal 2 platform terisi
- [ ] Minimal 70% data ber-tag `aceh_confidence` = "high" atau "medium"
- [ ] Total text ≥ 170 (minimum) atau target 300+
- [ ] Review 20% sample secara manual — apakah benar relevan Aceh?
