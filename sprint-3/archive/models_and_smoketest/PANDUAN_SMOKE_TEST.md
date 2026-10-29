# 🧪 Panduan Smoke Test & Evaluasi Efisiensi Scraping Pipeline

> **Tujuan**: Memastikan pipeline scraping (HTTP client anti-ban, structured logger, multi-strategy resolver, dan extractor) berjalan normal dan efisien pada **50 artikel** tanpa perlu scraping penuh 1.350 URL terlebih dahulu.

---

## 🎯 Mengapa Smoke Test 50 Artikel?

1. **Non-Destruktif (Database Aman)**:
   - Data uji disimpan terpisah di `materi-4/data/smoke_test_output/`.
   - Database utama (`articles_database.csv` sebanyak 660 artikel dan `paragraphs_raw.csv` 8.323 paragraf) **tidak akan terkontaminasi atau tertimpa**.
2. **Evaluasi Efisiensi & Kecepatan**:
   - Menghitung *throughput* nyata (kecepatan URLs/detik dan artikel/detik).
   - Mengukur efektivitas *rate-limiting* dan anti-ban pada portal berita.
3. **Proyeksi Waktu Riil**:
   - Memberikan estimasi akurat berapa menit yang dibutuhkan untuk menjalankan full scraping 1.350 URL.
4. **Verifikasi Kualitas Konten**:
   - Memastikan pembersihan boilerplate berjalan, panjang paragraf memenuhi syarat (>= 50 karakter), dan skema kolom lengkap.

---

## 🚀 Cara Menjalankan Smoke Test

### Metode 1: Menggunakan Makefile (Paling Mudah & Cepat ⭐)

Cukup ketik satu perintah dari root folder project:

```bash
make smoke
```
*Perintah ini otomatis menjalankan smoke test 50 artikel lengkap dengan evaluasi efisiensi.*

Opsi lainnya via Makefile:
* `make smoke-quick` : Smoke test kilat 10 artikel (~10 detik).
* `make status`      : Memeriksa jumlah data artikel & paragraf saat ini.
* `make logs`        : Melihat 20 catatan log JSON terbaru.
* `make clean-smoke` : Membersihkan folder sementara hasil smoke test.

---

### Metode 2: Direct Python Command

Buka terminal dan jalankan:

```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 smoke_test.py
```

*Atau tentukan jumlah sampel sesuai kebutuhan:*
```bash
python3 smoke_test.py --sample-size 50
```


### Yang Diuji Secara Otomatis:
- **Stage 1**: Pengecekan dependensi library (`requests`, `bs4`, `newspaper`, `googlenewsdecoder`, `pandas`, `tqdm`).
- **Stage 2**: Uji koneksi `RateLimitedClient` (rotasi User-Agent, handling backoff, pool connection).
- **Stage 3**: Uji pencatatan `StructuredLogger` ke file JSON Lines di `materi-4/logs/`.
- **Stage 4**: Multi-strategy URL Resolver pada 50 URL sampel (5 threads paralel).
- **Stage 5**: Ekstraksi artikel utuh & paragraf (8 threads paralel) dengan fallback parser.
- **Stage 6**: Validasi skema dataset dan quality gate konten.
- **Stage 7**: Laporan efisiensi & proyeksi waktu eksekusi penuh 1.350 URL.

---

### Metode 2: Uji Manual Bertahap (Opsi Fleksibel)

Jika Anda ingin menguji masing-masing script secara terpisah dengan limit 50 data:

#### 1. Uji Resolver (50 URL)
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 02_resolver.py --limit 50 --output ../data/smoke_test_output/manual_resolved.csv
```

#### 2. Uji Ekstraksi (50 URL)
```bash
python3 03_extraction.py --limit 50 \
  --input ../data/smoke_test_output/manual_resolved.csv \
  --output-db ../data/smoke_test_output/manual_articles.csv \
  --output-para ../data/smoke_test_output/manual_paragraphs.csv \
  --smoke-test
```

---

## 📊 Cara Membaca Output & Scorecard

Setelah eksekusi selesai, terminal akan menampilkan **Scorecard & Metrik Efisiensi**:

```text
=================================================================
📊 SMOKE TEST SCORECARD SUMMARY
=================================================================
   ✅ Stage 1 - Dependencies             : [PASS]
   ✅ Stage 2 - HTTP Client              : [PASS]
   ✅ Stage 3 - Logger                   : [PASS]
   ✅ Stage 4 - URL Resolver             : [PASS]
   ✅ Stage 5 - Extraction               : [PASS]
   ✅ Stage 6 - Quality Gate             : [PASS]
-----------------------------------------------------------------
⏱️  Total waktu pengujian : ~25-45 detik

📈 METRIK EFISIENSI (Berdasarkan pengujian 50 artikel):
• Kecepatan Resolver   : ~2.5 - 4.0 URLs/detik
• Kecepatan Extractor  : ~1.5 - 2.5 artikel/detik
• Success Rate Gabungan: >= 80%
-----------------------------------------------------------------
⏱️ PROYEKSI WAKTU SCRAPING PENUH (1.350 ARTIKEL):
• Estimasi Resolusi URL (1.350 URL)   : ~5 - 8 menit
• Estimasi Ekstraksi (~1.100 artikel) : ~7 - 12 menit
• TOTAL ESTIMASI EKSEKUSI PENUH       : ~12 - 20 menit
=================================================================
```

---

## 🔍 Cara Verifikasi Log & File Output

### 1. Cek File Output Smoke Test
```bash
ls -la /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/smoke_test_output/
```
Output yang terbentuk:
- `smoke_resolved_urls.csv`: Hasil dekripsi URL Google News ke portal berita asli.
- `smoke_articles_db.csv`: Data artikel lengkap (judul, tanggal, portal, penulis, teks lengkap).
- `smoke_paragraphs_raw.csv`: Data level paragraf siap analisis.

### 2. Cek Log Terstruktur (JSON Lines)
```bash
tail -n 20 /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/logs/scraping_*.jsonl | python3 -m json.tool --no-ensure-ascii
```
Setiap event scraping tersimpan rapi dalam format JSON dengan metadata URL, latency, metode ekstraksi, dan status.

---

## ✅ Kriteria Kelulusan Smoke Test (Health Check Gate)

Sebelum memulai full scrape, pastikan hal-hal berikut terpenuhi:
- [ ] Seluruh Stage 1 sampai 6 berstatus **[PASS]**.
- [ ] Resolver Success Rate minimal **≥ 70%** (target akhir ≥ 80%).
- [ ] Tidak ada unhandled exception / crash fatal.
- [ ] Kecepatan total wajar (tidak terkena IP ban atau rate-limit 429 berulang).
- [ ] File log `logs/scraping_YYYY-MM-DD.jsonl` mencatat riwayat event secara terstruktur.

---

## 🚀 Langkah Selanjutnya (Full Run Fase 1)

Setelah smoke test dinyatakan **[ALL PASSED]** dan Anda puas dengan efisiensinya, jalankan pipeline scraping penuh:

### Menggunakan Makefile (Mudah):
```bash
# Opsi 1: Jalankan sekaligus (Resolve lalu Extract)
make full

# Opsi 2: Jalankan bertahap
make resolve   # Step 1: Resolusi URL penuh (1.350 artikel)
make extract   # Step 2: Ekstraksi konten artikel baru (resume mode aktif)
```

### Atau Menggunakan Python Langsung:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping

# 1. Jalankan resolusi URL penuh (1.350 artikel)
python3 02_resolver.py

# 2. Jalankan ekstraksi konten penuh (mode resume otomatis skip 660 artikel lama)
python3 03_extraction.py
```
Dengan mode resume otomatis pada `03_extraction.py`, script hanya akan menarik URL artikel baru yang belum ada di database, dan nomor ID (`article_id` dan `paragraph_id`) akan berlanjut secara terurut tanpa duplikasi.

