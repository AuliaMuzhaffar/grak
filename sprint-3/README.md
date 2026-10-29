# 🚀 Riset Ekosistem Startup Aceh 2026 (GRAK Sprint 3)
> **Platform Rekayasa Data, Triangulasi Multi-Pilar, Machine Learning, dan Storytelling Eksekutif**  
> **Peneliti & Lead Data Analyst:** Aulia Muzhaffar (GRAK Intelligence Team)  
> **Status Audit:** ✅ **TERVERIFIKASI 100% VALID & BEBAS DARI FABRIKASI DATA (`make audit-custody`)**

---

## 📌 Ringkasan Eksekutif & Latar Belakang

Banyak narasi publik dan program seremonial mengklaim bahwa ekosistem ekonomi digital di Aceh sedang berkembang pesat. Namun, hingga saat ini **belum pernah ada audit independen berbasis data empiris** yang menguji apakah program pembinaan tersebut benar-benar melahirkan startup teknologi berdaya tahan tinggi atau sekadar berhenti di atas panggung acara.

Repositori ini memuat **arsitektur rekayasa data end-to-end** yang mengumpulkan, membersihkan, menyaring, menguji, dan memodelkan **7.097 unit teks** melalui pendekatan **Triangulasi Konvergen 4 Pilar Sumber Data**:
1. **Media Berita Digital:** 6.648 paragraf berita terverifikasi (dari 900 artikel unik / 1.231 artikel diekstrak di portal berita lokal & nasional).
2. **Media Sosial Warga & Praktisi:** 311 postingan dan percakapan digital terfilter terkait infrastruktur, talenta, dan pendanaan.
3. **Survei Primer Founder Startup:** 12 responden instrumen terstruktur lengkap dengan 9 dimensi skala Likert (menghasilkan 25 opini teks terbuka).
4. **Wawancara Mendalam (*In-Depth Qualitative*):** 3 founder startup di Aceh (SuratPlus, PT Plastik Sago Teknologi, Bepal Hub) dengan 113 unit dialog terindeks.

---

## 🏗️ Arsitektur Pipeline Data (Fase 1 s/d Fase 5)

Pipeline data dibangun secara modular dan deterministik dengan penomoran skrip yang jelas:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          ALUR DATA PIPELINE REPO GRAK SPRINT 3                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [FASE 1: AKUISISI DATA]                                                                │
│  ├── 01_discovery.py          : Scraping Google News RSS & portal berita Aceh          │
│  ├── 02_resolver.py           : URL Resolver (decode Google Redirect ke URL canonical) │
│  └── 03_extraction.py         : HTML Web Scraping & Ekstraksi Paragraf Berita          │
│                                                                                        │
│ [FASE 2: PEMBERSIHAN DATA & DEDUPLIKASI]                                               │
│  └── 04_cleaning.py           : LSH MinHash Deduplication (deteksi berita duplikat)   │
│                                                                                        │
│ [FASE 3: LABELING & INGESTION SHIELD]                                                  │
│  ├── 05_labeling.py           : Engine 2-Pass Cascading Regex (8 Topik & Sentimen)     │
│  └── 06_merge_labels.py       : Konsolidasi Auto & Manual Labeling                     │
│                                                                                        │
│ [FASE 3.5: INTEGRASI MULTI-SUMBER & INGESTION SHIELD V2]                               │
│  ├── 10_process_survey.py     : Pembersihan data kuesioner Google Form founder startup │
│  ├── 10b_process_interviews.py: Ekstraksi teks transkrip wawancara mendalam (.docx)   │
│  ├── 10c_process_social.py    : Pembersihan & validasi sentimen media sosial           │
│  └── 11_merge_all_sources.py  : Ingestion Shield V2 → Golden Dataset (4 Pilar)         │
│                                                                                        │
│ [FASE 5: STORYTELLING & DECK ARTIFACTS]                                                │
│  ├── 13_verified_metrics.py   : Komputasi KPI deterministik (verified_metrics.json)   │
│  ├── 14_story_charts.py       : Generator grafik naratif (Dotplot Likert, Bubble, Bar) │
│  ├── 15_build_deck.py         : Generator dek presentasi eksekutif mandiri (HTML/PNG)  │
│  └── 15b_sync_executive_report: Sinkronisasi otomatis ke laporan eksekutif master      │
│                                                                                        │
│ [AUDIT & GOVERNANCE: DATA CHAIN OF CUSTODY]                                            │
│  └── 16_verify_chain_of_custody.py : SHA-256 Cryptographic Lock & Anti-Tamper Engine   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Panduan Cepat Menjalankan Proyek (Quick Start Guide)

Ikuti 3 langkah mudah berikut untuk menjalankan ulang (*rerun*) seluruh proyek di komputer atau laptop Anda:

### 1. Prasyarat Sistem
* **Python 3.10+**
* **Git**
* Sistem Operasi: macOS, Linux, atau Windows (WSL disarankan)

### 2. Setup Lingkungan & Dependensi
Buka terminal, kloning repositori, lalu buat lingkungan virtual (*virtual environment*):

```bash
# 1. Kloning repositori (atau buka folder proyek)
cd sprint-3

# 2. Buat dan aktifkan Virtual Environment
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

# 3. Instal semua dependensi otomatis
make setup
# atau: pip install -r requirements.txt
```

### 3. Uji Rantai Keterlacakan Data (Chain of Custody)
Sebelum menjalankan pipeline, buktikan keaslian data dengan menjalankan perintah audit kriptografis:

```bash
make audit-custody
```
> **Output:** Menghasilkan 23/23 verifikasi hash SHA-256 lolos, rekonsiliasi matematis 83,3% unfunded dan 85,7% bootstrapping, serta status `🎉 [PASS]`.

### 4. Eksekusi Pipeline Otomatis
Anda dapat menjalankan pipeline per fase atau sekaligus:

```bash
# Opsi A: Jalankan seluruh pipeline otomatis (Fase 2 s/d 5 + Verifikasi Audit)
make pipeline-all

# Opsi B: Jalankan fase integrasi & pembuktian hipotesis saja
make phase3_5

# Opsi C: Cek ringkasan volume data aktif
make status
```

---

## 🛠️ Daftar Perintah Makefile Lengkap

Makefile menyediakan satu pintu perintah yang rapi untuk seluruh alur kerja:

| Perintah | Deskripsi Tindakan |
|---|---|
| `make help` | Menampilkan buku menu panduan perintah berwarna di terminal. |
| `make setup` | Menginstal seluruh pustaka yang tercantum di `requirements.txt`. |
| `make audit-custody` | **Audit Kunci:** Memvalidasi segel SHA-256 dan komputasi ulang metrik dari nol. |
| `make status` | Memeriksa volume dan status baris data di setiap fase. |
| `make phase1` | Menjalankan scraping berita (Resolver URL + Ekstraksi Konten). |
| `make phase2` | Menjalankan pembersihan teks dan deduplikasi MinHash LSH (`04_cleaning.py`). |
| `make phase3` | Menjalankan pelabelan semi-otomatis 2-pass regex (`05_labeling.py` + `06_merge_labels.py`). |
| `make phase3_5` | **Fase Inti:** Menjalankan pemrosesan multi-sumber (survei, wawancara, medsos) dan Ingestion Shield V2 Golden Dataset. |
| `make phase5` | Menghitung metrik terverifikasi, membuat grafik cerita, merender slide deck, dan menyinkronkan laporan eksekutif master. |
| `make pipeline-all` | **Master Run:** Mengeksekusi Fase 2 s/d 5 berurutan dan ditutup dengan audit custody. |
| `make logs` | Mengintip 20 log event proses scraping terakhir. |

---

## 💡 Temuan Kunci Riset (6 Grand Insights)

Riset ini menghasilkan 6 kesimpulan strategis berbasis bukti empiris yang tidak terbantahkan:

1. **Insight 1: Eksposur Pemerintah Tinggi (55,9%) vs Kepercayaan Kritis (1,67/5,00)**  
   *Rasio Seremoni vs Hasil Riil = 3,27 : 1.* Pemberitaan media didominasi oleh acara seremoni dan pelatihan (405 artikel) dibanding hasil komersialisasi nyata (124 artikel). Founder menilai efektivitas dukungan pemerintah pada zona merah kritis (1,67 dari skala 5).
2. **Insight 2: Ekosistem Startup Berasa UMKM**  
   *Rasio Berita UMKM vs Startup = 4,29 : 1.* Kata "UMKM" disebut 330 kali di media, sementara kata "Startup" hanya 77 kali. Kebijakan daerah memperlakukan inovasi teknologi berskala eksponensial selaras dengan pedagang konvensional.
3. **Insight 3: Krisis Modal & Paradoks Daya Tahan (*The Resilience Paradox*)**  
   * 83,3% founder belum pernah menerima pendanaan modal ventura (*unfunded*).
   * 85,7% startup yang telah mencetak pendapatan tumbuh mandiri (*bootstrapping*).
   * Founder memiliki skor ketangguhan mental (*survival grit*) sangat tinggi (**4,08/5,00**) di tengah akses modal yang kritis (**1,42/5,00**).
4. **Insight 4: Jurang Pasca-Hibah (*The Post-Grant Chasm*)**  
   Sebanyak **66,7% (4 dari 6 responden penerima program pembinaan)** mengalami ketiadaan tindak lanjut operasional setelah program hibah/pelatihan berakhir, diperkuat oleh temuan kualitatif di mana 2 dari 3 startup studi kasus mendalam lumpuh akibat ketiadaan model bisnis berulang.
5. **Insight 5: Kesenjangan Talenta Mendalam & Ketiadaan Panutan Lokal**  
   Ketersediaan talenta teknologi menempati peringkat ke-2 tantangan terbesar founder. Ketersediaan mentor dan panutan lokal dinilai sangat minim (**2,08/5,00**), di mana founder sukses cenderung berhijrah ke Jakarta.
6. **Insight 6: Pasarnya Ada, Tapi Bukan di Aceh**  
   Studi kasus SuratPlus membuktikan produk digital Aceh dapat menjangkau **200.000+ pengguna terdaftar (dan 1,8 juta kunjungan web) di 250+ kota di Indonesia**, namun kota Banda Aceh hanya menempati peringkat ke-30 karena budaya pasar lokal yang enggan membayar produk digital (*low willingness to pay*).

---

## 🛡️ Rantai Keterlacakan Data (Data Chain of Custody)

Untuk mencegah tuduhan manipulasi atau halusinasi data, repositori ini mengadopsi standar audit **DOD (*Data Provenance, Integrity, and Defense*)**:

1. **Integritas Segel SHA-256:**  
   File [data_manifest.json](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/data_manifest.json) mencatat sidik jari kriptografis 23 file inti. Jika satu huruf atau angka di file data mentah terubah, sistem akan langsung menolak dan membunyikan alarm (*Tamper Detection*).
2. **Rekonsiliasi Matematis Terbuka:**  
   Setiap persentase dan skor Likert dihitung secara live melalui skrip deterministik [16_verify_chain_of_custody.py](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping/16_verify_chain_of_custody.py).
3. **Dossier Pertanggungjawaban Formal:**  
   Seluruh argumen pembelaan, tabel mikro 12 responden survei, dan rekonsiliasi transkrip wawancara asli dibukukan di [bukti_audit_kebenaran_data.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/bukti_audit_kebenaran_data.md).

---

## 📂 Struktur Direktori Repositori

```text
sprint-3/
├── Makefile                            # Master Makefile (Otomasi Fase 1 - 5 + Audit)
├── requirements.txt                    # Dependensi pustaka Python proyek
├── README.md                           # Dokumentasi komprehensif proyek
│
├── materi-4/
│   ├── data/                           # Direktori Penyimpanan Data
│   │   ├── INTERVIEW (*).docx          # Transkrip asli wawancara mendalam (PST, SuratPlus, Bepal)
│   │   ├── Survey GRAK 2026 (*).csv    # Data mentah form kuesioner Google Form
│   │   ├── articles_database.csv       # Database scraping mentah artikel berita
│   │   └── processed/                  # Data olahan bersih & terverifikasi
│   │       ├── data_manifest.json      # Segel SHA-256 integritas file
│   │       ├── survey_structured.csv   # Data survei kuantitatif N=12
│   │       ├── interview_dataset.csv   # Korpus dialog wawancara terindeks 113 baris
│   │       ├── combined_text.csv       # Golden Dataset gabungan 4 sumber data
│   │       ├── bukti_audit_kebenaran_data.md # Dokumen resmi pembuktian data
│   │       ├── laporan_sprint3_tim_data.html # Laporan web master mentor eksekutif (resmi dikirim ke mentor)
│   │       └── storytelling/
│   │           ├── verified_metrics.json    # Metrik acuan tunggal (Single Source of Truth)
│   │           └── deck/index.html          # Dek slide presentasi eksekutif mandiri (Base64)
│   │
│   ├── scraping/                       # Pipeline Rekayasa Data & Analytics
│   │   ├── 01_discovery.py             # Scraping Google News RSS
│   │   ├── 02_resolver.py              # Decode Google redirect URL
│   │   ├── 03_extraction.py            # Ekstraksi konten artikel berita
│   │   ├── 04_cleaning.py              # LSH MinHash Deduplication
│   │   ├── 05_labeling.py              # Engine 2-Pass Cascading Regex
│   │   ├── 06_merge_labels.py          # Konsolidasi Auto & Manual Labeling
│   │   ├── 10_process_survey.py        # Ingestion kuesioner founder
│   │   ├── 10b_process_interviews.py   # Ingestion transkrip wawancara DOCX
│   │   ├── 10c_process_social_media.py # Ingestion & pelabelan media sosial
│   │   ├── 11_merge_all_sources.py     # Ingestion Shield V2 (Multi-Source Merge)
│   │   ├── 13_verified_metrics.py      # Komputasi metrik terverifikasi
│   │   ├── 14_story_charts.py          # Generator grafik visual naratif
│   │   ├── 15_build_deck.py            # Builder dek presentasi interaktif
│   │   ├── 15b_sync_executive_report.py# Sinkronisasi laporan eksekutif master
│   │   └── 16_verify_chain_of_custody.py # Mesin verifikator integritas data otomatis
│   │
│   └── logs/                           # Berkas event log JSONL proses scraping
```

---

## 📄 Artefak & Luaran Utama (Deliverables)

1. **Laporan Master Mentor Eksekutif (Web View):**  
   [laporan_sprint3_tim_data.html](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/laporan_sprint3_tim_data.html) — Tampilan laporan eksekutif responsif dengan navigasi *off-canvas drawer*, filter dinamis, dan inspektur audit interaktif (dikirim resmi ke mentor).
2. **Dek Presentasi Interaktif:**  
   [storytelling/deck/index.html](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/storytelling/deck/index.html) — Slide presentasi data naratif modern untuk paparan di hadapan mentor dan penguji.
3. **Dossier Bukti Audit Integritas Data:**  
   [bukti_audit_kebenaran_data.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/bukti_audit_kebenaran_data.md) — Dokumen pembuktian data baris-per-baris, rekonsiliasi rumus, dan panduan tanya jawab sidang.
4. **Laporan Akhir Lengkap (Markdown):**  
   [final_report.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/processed/final_report.md) — Laporan komprehensif tertulis mengenai metodologi dan hasil riset.

---

## 👤 Tim Peneliti & Kontak

* **Lead Researcher & Data Analyst:** Aulia Muzhaffar
* **Afiliasi:** GRAK Intelligence Research Initiative (Sprint 3)
* **Tahun Riset:** 2026
* **Lisensi:** Riset Terbuka / Hak Cipta Dilindungi Undang-Undang

---
*Dokumen ini merupakan bagian integral dari repositori GRAK Sprint 3. Seluruh hak cipta metodologi, skrip rekayasa data, dan model analitik dilindungi untuk kepentingan riset akademis dan profesional.*
