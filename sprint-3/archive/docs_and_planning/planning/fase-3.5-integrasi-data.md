# Fase 3.5: Integrasi Dataset Multi-Source (Survey + Interview + Scraping + Social Media)

> **Estimasi waktu**: 1.5 - 2 hari kerja (3 chat session)  
> **Prioritas**: 🔴 P0  
> **Prasyarat**: Fase 3 selesai (`labeled_dataset_final.csv` ada, 13.840 paragraf berlabel)  
> **Output Utama**:  
> - `data/processed/survey_structured.csv` — Data terstruktur survey (11 responden, siap statistik deskriptif)  
> - `data/processed/interview_dataset.csv` — Transkrip interview tersegmentasi per ide (~40-60 unit)  
> - `data/processed/social_media_labeled.csv` — Data social media yang sudah dibersihkan dan dilabel *(opsional, jika data dari rekan tersedia)*  
> - `data/processed/combined_text.csv` — Unified text dataset (scraping + survey open-ended + interview + social media)  
> - `data/processed/triangulation_matrix.csv` — Evidence per hypothesis per sumber data  
> - `data/processed/triangulation_report.md` — Laporan triangulasi naratif  

---

## 🎯 Tujuan Fase Ini

1. **Proses data survey** — Pecah Survey CSV menjadi data terstruktur (Likert, multiple choice) dan text open-ended (Q21-23)
2. **Proses data interview** — Ekstrak jawaban dari 3 file docx, segmentasi per ide/argumen, label topic + sentiment
3. **Proses data social media** *(opsional)* — Bersihkan dan label data dari X, YouTube, LinkedIn (disediakan oleh rekan tim)
4. **Gabungkan semua sumber text** — Merge scraping + survey open-ended + interview (+ social media jika tersedia) ke format unified
5. **Bangun triangulation matrix** — Hitung evidence per hypothesis (H1-H6) dari setiap sumber data
6. **Validasi multi-source** — Pastikan setiap hypothesis dijawab oleh minimal 2 sumber (triangulasi)

---

## 📋 Daftar File yang Dibuat

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/10_process_survey.py` | Proses survey CSV → `survey_structured.csv` + rows open-ended |
| **[NEW]** | `scraping/10b_process_interviews.py` | Ekstrak jawaban docx → segmentasi → `interview_dataset.csv` |
| **[NEW]** | `scraping/10c_process_social_media.py` | Bersihkan + label data social media → `social_media_labeled.csv` *(opsional)* |
| **[NEW]** | `scraping/11_merge_all_sources.py` | Gabung semua text sources → `combined_text.csv` |
| **[NEW]** | `scraping/12_triangulation.py` | Hitung evidence per hypothesis → matrix + report |
| **[DATA]** | `data/processed/survey_structured.csv` | Data terstruktur survey (Likert + multiple choice) |
| **[DATA]** | `data/processed/interview_dataset.csv` | Interview tersegmentasi per unit bermakna |
| **[DATA]** | `data/processed/social_media_labeled.csv` | Social media bersih dan berlabel *(opsional)* |
| **[DATA]** | `data/processed/combined_text.csv` | Unified text dataset semua sumber |
| **[DATA]** | `data/processed/triangulation_matrix.csv` | Evidence matrix per hypothesis |
| **[REPORT]** | `data/processed/triangulation_report.md` | Laporan naratif triangulasi |

---

## 📊 Audit Dataset Saat Ini (Pre-Integrasi)

### Dataset 1: Scraping (Berita Online) ✅
- **File**: `data/processed/labeled_dataset_final.csv`
- **Jumlah**: 13.840 paragraf dari 1.163 artikel, 243 portal
- **Label**: Topic (8 kategori) + Sentiment (3 kategori)
- **Kekuatan**: Volume besar, coverage topik luas
- **Kelemahan**: Sentiment 86.5% neutral (sifat jurnalistik objektif)

### Dataset 2: Survey ✅
- **File**: `data/Survey GRAK 2026 - Sprint 3 (Responses) - Form Responses 1.csv`
- **Jumlah**: 11 responden × 28 kolom (12 baris termasuk header)
- **Tipe data**:
  - **Terstruktur (Q1-Q20)**: Multiple choice, Likert scale 1-5, ranking
  - **Open-ended (Q21-Q23)**: Text bebas (12 + 12 + 6 = ~30 jawaban)
- **Kekuatan**: Data primer langsung dari pelaku ekosistem, sentimen jelas
- **Kelemahan**: N=11 (terlalu kecil untuk statistik inferensial)

### Dataset 3: Interview ✅
- **File**: 3 file docx di `data/`
  - ` INTERVIEW (bepal).docx` — Bepal (Komunitas/Edukasi Digital, Lhokseumawe)
  - ` INTERVIEW (SURATPLUS ).docx` — SuratPlus (Startup Digital AI, Banda Aceh)
  - ` INTERVIEW (PT PLASTIK SAGO TEKNOLOGI (PST)).docx` — PST (Startup Riset/Produk, Lhokseumawe)
- **Format**: Q&A terstruktur (pertanyaan + jawaban), bukan transkrip mentah
- **Kekuatan**: Cerita personal mendalam, konteks kualitatif kuat
- **Kelemahan**: N=3, belum di-segmentasi atau di-label

### Dataset 4: Social Media ⏳ (Menunggu dari Rekan Tim)
- **File**: Belum tersedia — sedang di-scraping oleh rekan tim
- **Platform**: X (Twitter), YouTube, LinkedIn (post + komentar)
- **Status**: Data mentah, belum di-filter, belum di-bersihkan
- **Yang diminta ke rekan** (instruksi sudah dikirim):
  - Filter: hanya konten terkait startup/digital Aceh
  - Bersihkan: hapus spam, komentar < 5 kata, duplikat
  - Format CSV: `text`, `source_portal`, `publish_date`, `url`, `account`, `content_type`
  - JANGAN di-label (kita yang label setelah data diterima)
- **Kekuatan**: Sentimen langsung dari publik, bahasa informal/opini
- **Kelemahan**: Noise tinggi, perlu filter ketat untuk Aceh-specific
- **Estimasi**: Belum diketahui (tergantung hasil scraping rekan)

> [!NOTE]
> **Social media bersifat NON-BLOCKING.** Chat Session 1 & 2 bisa berjalan tanpa menunggu data ini. Jika data dari rekan sudah siap sebelum Chat Session 3, proses di Chat 3. Jika belum, jalankan Chat 3 tanpa social media, dan tambahkan nanti dengan re-run `11_merge_all_sources.py`.

---

## 🧠 Konsep Kunci: Mixed-Methods Data Integration

### Kenapa TIDAK Bisa Langsung Merge Semua Jadi 1 Tabel?

```
SCRAPING DATA     SURVEY DATA        INTERVIEW DATA     SOCIAL MEDIA
━━━━━━━━━━━━      ━━━━━━━━━━━        ━━━━━━━━━━━━━━     ━━━━━━━━━━━━
Tipe: TEXT         Tipe: STRUCTURED    Tipe: QUALITATIVE  Tipe: TEXT (informal)
Unit: paragraf     Unit: responden     Unit: jawaban Q&A  Unit: post/komentar
N: 13,840          N: 11               N: 3               N: belum diketahui
Format: CSV        Format: CSV         Format: DOCX       Format: CSV (dari rekan)
```

Keempat dataset ini **berbeda nature-nya**. Pendekatan integrasi yang benar adalah **Triangulasi** — setiap dataset menjawab hypothesis yang sama dari sudut berbeda.

### Arsitektur 4 Dataset Final

```
┌─────────────────────────────────────────────────────────────┐
│                    FINAL DATASET SUITE                       │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  1. combined_text    │  │  2. survey_structured        │ │
│  │     .csv             │  │     .csv                     │ │
│  │                      │  │                              │ │
│  │  Scraping paragraf   │  │  Likert scale (Q15-20)       │ │
│  │  + Survey open-end   │  │  Multiple choice (Q1-14)     │ │
│  │  + Interview units   │  │  Demografis responden        │ │
│  │  + Social media posts│  │                              │ │
│  │                      │  │                              │ │
│  │  Untuk: NLP, Topic   │  │  Untuk: Statistik deskriptif │ │
│  │  Modeling, Sentiment │  │  deskriptif, cross-tab       │ │
│  └──────────┬───────────┘  └───────────┬──────────────────┘ │
│             │                          │                     │
│             ▼                          ▼                     │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  3. triangulation_matrix.csv                             ││
│  │                                                          ││
│  │  Per Hypothesis × Per Data Source → Evidence Summary      ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │  4. triangulation_report.md                              ││
│  │                                                          ││
│  │  Insight naratif + evidence dari semua sumber            ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Peran Setiap Dataset dalam Analisis

| Aspek Analisis | Sumber Utama | Alasan |
|---------------|-------------|--------|
| **Topic distribution** | Scraping (13.840 rows) | Volume besar, coverage luas |
| **Sentiment / Persepsi** | Survey + Interview + Social Media | Data primer, sentimen langsung dari pelaku & publik |
| **Statistik deskriptif** | Survey structured (N=11) | Likert scale, ranking, demografis |
| **Konteks kualitatif** | Interview (N=3) | Cerita personal, kutipan langsung |
| **Opini publik informal** | Social Media (X, YouTube, LinkedIn) | Bahasa informal, sentimen langsung |
| **Triangulasi hypothesis** | Semua 4 sumber (3 wajib + 1 opsional) | Cross-validation findings |

---

## 🔧 Catatan Metodologis

### N=11 Survey: Batasan dan Cara Penggunaan

Dengan 11 responden, analisis yang **BOLEH** dilakukan:
- Statistik deskriptif: mean, median, modus, distribusi frekuensi
- Visualisasi: bar chart, radar chart, Likert diverging bar
- Narasi: "8 dari 11 responden (73%) menyebut pendanaan sebagai tantangan"
- Cross-tabulation deskriptif (wilayah × tantangan)

Yang **TIDAK BOLEH** dilakukan:
- Uji statistik inferensial (t-test, chi-square, regresi)
- Klaim "signifikan secara statistik"
- Generalisasi ke populasi pelaku ekosistem Aceh

### Sentiment dari Scraping: Kenapa 86.5% Neutral?

Distribusi sentiment scraping: neutral (86.5%), positive (12.8%), negative (0.7%).

**Ini bukan bug, ini sifat data berita jurnalistik:**
- Jurnalis dilatih menulis objektif/informatif
- `SENTIMENT_MIN_MATCHES = 2` artinya butuh ≥2 keyword untuk non-neutral
- Keyword negatif (`"hambatan"`, `"kendala"`) jarang muncul karena gaya bahasa diplomatis

**Implikasi**: Untuk analisis sentiment, andalkan survey + interview + social media. Di report, tulis:
> *"Analisis sentimen didasarkan pada data primer (survey, interview, dan social media) karena data berita cenderung ditulis dalam nada jurnalistik netral."*

### Labeling Survey, Interview & Social Media: Manual vs Auto

- **Survey open-ended (Q21-23)**: Label MANUAL (hanya ~30 rows, 15 menit kerja)
- **Interview units**: Label SEMI-AUTO (keyword matching + manual review, ~40-60 units)
- **Social media**: Label SEMI-AUTO (keyword matching + manual review). Bahasa informal, perlu keyword tambahan untuk slang
- **Alasan**: Auto-labeler dilatih dari pola berita formal. Bahasa interview/survey/social media informal dan berbeda

### Social Media: Instruksi untuk Rekan Tim

Data social media di-scraping oleh rekan tim. Instruksi yang sudah dikirim:

1. **Filter**: Buang post/komentar yang bukan tentang startup/digital Aceh. Hapus spam, komentar < 5 kata, duplikat
2. **Format CSV** dengan kolom: `text`, `source_portal` (twitter/youtube/linkedin), `publish_date`, `url`, `account`, `content_type` (post/comment/reply)
3. **JANGAN di-label** — kita yang label agar konsisten
4. **Nama file**: `social_media_clean.csv`, encoding UTF-8

> [!IMPORTANT]
> **Social media data bersifat non-blocking.** Chat Session 1 & 2 bisa berjalan tanpa menunggu data ini. Kalau data sudah tersedia sebelum Chat Session 3, masukkan di Chat 3. Kalau belum, jalankan Chat 3 tanpa social media, dan tambahkan nanti dengan re-run `11_merge_all_sources.py`.

---

## 📦 Eksekusi: 3 Chat Session

Fase ini dipecah menjadi **3 chat session** yang masing-masing independen.

---

### Chat Session 1: Data Preparation (Survey + Interview → CSV)

**Estimasi**: Sedang (2 script + verifikasi)

#### Scope Chat 1:
1. Buat `scraping/10_process_survey.py`
2. Buat `scraping/10b_process_interviews.py`
3. Jalankan kedua script
4. Verifikasi output

#### Prompt untuk Chat 1:

```
@materi-4 ini folder projek kita
@planning ini folder planning

Kita sedang mengerjakan Fase 3.5: Integrasi Dataset untuk riset ekosistem startup Aceh 
(GRAK Sprint 3). Planning lengkap ada di planning/fase-3.5-integrasi-data.md

Ini adalah Chat Session 1 dari 3.

Dataset yang ada:
1. Scraping berita: data/processed/labeled_dataset_final.csv (13,840 paragraf, sudah 
   labeled topic+sentiment)
2. Survey: data/Survey GRAK 2026 - Sprint 3 (Responses) - Form Responses 1.csv 
   (11 responden, 28 kolom)
3. Interview: 3 file docx di data/ (Bepal, SuratPlus, PT Plastik Sago Teknologi) 
   — format Q&A (pertanyaan + jawaban, bukan transkrip mentah)

TUGAS CHAT INI:
1. Buat script scraping/10_process_survey.py:
   - Input: Survey CSV
   - Output A: data/processed/survey_structured.csv (data terstruktur: Likert Q15-20 
     dikonversi ke int 1-5, multiple choice Q1-14 di-rename kolom, tantangan Q12 
     dipecah jadi 3 kolom)
   - Output B: rows open-ended (Q21, Q22, Q23) dengan format kompatibel 
     labeled_dataset_final.csv untuk di-merge nanti ke combined_text.csv
   - Label topic+sentiment untuk open-ended: MANUAL assignment dalam script 
     (hardcode berdasarkan isi jawaban, karena hanya ~30 rows)

2. Buat script scraping/10b_process_interviews.py:
   - Input: 3 file docx interview
   - Proses: Baca docx → identifikasi blok "Jawaban:" → segmentasi per ide/argumen 
     (1 unit = 1 ide, min 5 kata) → label topic+sentiment semi-auto
   - Output: data/processed/interview_dataset.csv
   - Format: paragraph_id (INT_XXXX), text, article_title, source_portal="interview", 
     data_source="interview", publish_date, aceh_confidence="high", word_count, 
     interviewee, role, location, topic, sentiment

3. Jalankan kedua script dan verifikasi output (jumlah rows, distribusi label, 
   sample data)

Catatan penting:
- Format output harus kompatibel dengan kolom di labeled_dataset_final.csv
- Untuk interview, segmentasi per IDE bukan per kalimat
- N=11 survey sudah final
- Lihat planning/fase-3.5-integrasi-data.md untuk detail arsitektur
- Lihat planning/panduan-data-strategy.md Section 4 untuk contoh segmentasi interview
```

#### Step 1: Buat `scraping/10_process_survey.py`

**Input**: `data/Survey GRAK 2026 - Sprint 3 (Responses) - Form Responses 1.csv`

**Proses**:

```text
Survey CSV (28 kolom × 12 baris)
│
├── Kolom terstruktur (Q1-Q20) ──────→ survey_structured.csv
│   ├── Rename kolom panjang → nama pendek
│   ├── Konversi Likert text → int (1-5)
│   │   "1 - Sangat Tidak Setuju" → 1
│   │   "2 - Tidak Setuju" → 2
│   │   "3 - Netral" → 3
│   │   "4 - Setuju" → 4
│   │   "5 - Sangat Setuju" → 5
│   ├── Pecah Q12 (tantangan multi-select) → 3 kolom
│   └── Hapus kolom PII (WhatsApp/Email)
│
└── Kolom open-ended (Q21-Q23) ──────→ rows untuk combined_text.csv
    ├── Q21: "Jika bisa mengubah satu hal..." (12 jawaban)
    ├── Q22: "Kebutuhan utama belum terpenuhi" (12 jawaban)
    ├── Q23: "Pengalaman positif/negatif" (6 jawaban valid)
    ├── Label topic+sentiment MANUAL per row
    └── Format: paragraph_id=SRV_XXXX, source_portal="survey"
```

**Output A — `survey_structured.csv`**:

| Kolom | Tipe | Asal | Keterangan |
|-------|------|------|------------|
| `respondent_id` | int | Generated | ID unik (1-12) |
| `timestamp` | str | Kolom 1 | Waktu submit |
| `wilayah` | str | Q1 | Banda Aceh / Lhokseumawe / dll |
| `wilayah_lainnya` | str | Q1b | Jika menjawab "Lainnya" |
| `peran` | str | Q2 | Founder / Akademisi / dll |
| `lama_terlibat` | str | Q3 | <1 tahun / 1-3 tahun / dll |
| `sektor` | str | Q4 | Teknologi/Software / dll |
| `status_bisnis` | str | Q5 | Sudah punya produk/MVP / dll |
| `pernah_inkubasi` | str | Q6 | Ya / Tidak |
| `sumber_program` | str | Q7a | Kampus / Investor / dll |
| `jenis_dukungan` | str | Q7b | Funding / Mentoring / dll |
| `followup_program` | str | Q8 | Ada, berkelanjutan / dll |
| `pernah_event` | str | Q9 | Ya / Tidak |
| `pernah_pendanaan` | str | Q10 | Ya / Tidak |
| `kemungkinan_bertahan` | int | Q11 | Skala 1-5 |
| `tantangan_1` | str | Q12 (split) | Tantangan pertama |
| `tantangan_2` | str | Q12 (split) | Tantangan kedua |
| `tantangan_3` | str | Q12 (split) | Tantangan ketiga |
| `kemudahan_talent` | int | Q13 | Skala 1-5 |
| `kemudahan_pasar` | int | Q14 | Skala 1-5 |
| `persepsi_ekosistem` | int | Q15 | Likert → int 1-5 |
| `persepsi_pendanaan` | int | Q16 | Likert → int 1-5 |
| `persepsi_mentor` | int | Q17 | Likert → int 1-5 |
| `persepsi_pemerintah` | int | Q18 | Likert → int 1-5 |
| `persepsi_optimis` | int | Q19 | Likert → int 1-5 |
| `persepsi_infra` | int | Q20 | Likert → int 1-5 |

**Output B — Rows open-ended** (format kompatibel `labeled_dataset_final.csv`):

| Kolom | Contoh |
|-------|--------|
| `paragraph_id` | SRV_001 |
| `text` | "pemerintah aja gk peduli dengan ekosistem startup di aceh" |
| `article_title` | "Survey Q21 - Responden 3" |
| `source_portal` | survey |
| `data_source` | survey |
| `aceh_confidence` | high |
| `word_count` | 10 |
| `topic` | regulation *(manual assign)* |
| `sentiment` | negative *(manual assign)* |
| `collector` | Aulia |

#### Step 2: Buat `scraping/10b_process_interviews.py`

**Input**: 3 file docx interview

**Proses**:

```text
3 File DOCX Interview
│
├── Baca dengan python-docx
├── Identifikasi blok "Jawaban:" 
│   (setiap paragraf setelah baris yang mengandung "Jawaban:")
├── Filter: skip baris template/cheat sheet di akhir dokumen
├── Segmentasi per ide/argumen:
│   ├── Split by "." atau baris kosong jika jawaban panjang
│   ├── Minimum 5 kata per unit
│   ├── Hapus filler ("jadi", "nah", "ya", "gitu")
│   └── 1 unit = 1 ide pokok
├── Assign metadata per interview:
│   ├── Bepal: role="Komunitas/Edukasi", location="Lhokseumawe"
│   ├── SuratPlus: role="Founder Startup", location="Banda Aceh"  
│   └── PST: role="Founder Startup Riset", location="Lhokseumawe"
└── Label topic+sentiment semi-auto (keyword + manual review)
```

**Output — `interview_dataset.csv`**:

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `paragraph_id` | str | Format: INT_XXXX |
| `text` | str | Unit bermakna (1 ide per row) |
| `article_title` | str | "Interview Bepal" / "Interview SuratPlus" / "Interview PST" |
| `article_url` | str | Kosong (tidak ada URL) |
| `source_portal` | str | "interview" |
| `data_source` | str | "interview" |
| `publish_date` | str | Tanggal interview (2026-09) |
| `aceh_confidence` | str | "high" (interview pelaku Aceh = selalu high) |
| `word_count` | int | Jumlah kata per unit |
| `query_used` | str | "interview_{role}" |
| `collector` | str | "Aulia" |
| `interviewee` | str | Nama narasumber/perusahaan |
| `role` | str | Komunitas / Founder / dll |
| `location` | str | Lhokseumawe / Banda Aceh |
| `topic` | str | Label topic (semi-auto) |
| `sentiment` | str | Label sentiment (semi-auto) |

**Estimasi output**: ~40-60 unit bermakna dari 3 interview

#### Verifikasi Chat 1

```bash
# Cek survey structured
python3 -c "
import pandas as pd
df = pd.read_csv('data/processed/survey_structured.csv')
print(f'Shape: {df.shape}')
print(f'Kolom: {list(df.columns)}')
print(df.describe())
"

# Cek interview dataset
python3 -c "
import pandas as pd
df = pd.read_csv('data/processed/interview_dataset.csv')
print(f'Shape: {df.shape}')
print(f'Interviewee: {df.interviewee.value_counts().to_dict()}')
print(f'Topic: {df.topic.value_counts().to_dict()}')
print(f'Sentiment: {df.sentiment.value_counts().to_dict()}')
"
```

---

### Chat Session 2: Merge + Triangulation

**Estimasi**: Sedang (2 script + verifikasi)

#### Scope Chat 2:
1. Buat `scraping/11_merge_all_sources.py`
2. Buat `scraping/12_triangulation.py`
3. Jalankan kedua script
4. Verifikasi output + review triangulation report

#### Prompt untuk Chat 2:

```
@materi-4 ini folder projek kita
@planning ini folder planning

Lanjutan Fase 3.5: Integrasi Dataset. Ini Chat Session 2 dari 3.
Planning lengkap: planning/fase-3.5-integrasi-data.md

Dataset dari Chat 1 sudah siap:
- data/processed/labeled_dataset_final.csv (scraping, 13,840 rows)
- data/processed/survey_structured.csv (survey terstruktur, 11 responden)
- data/processed/interview_dataset.csv (interview units, ~40-60 rows)
- Survey open-ended sudah di-extract di Chat 1

TUGAS CHAT INI:
1. Buat script scraping/11_merge_all_sources.py:
   - Gabung: scraping labeled + survey open-ended + interview → combined_text.csv
   - Format unified: id, paragraph_id, text, source_portal, data_source, 
     publish_date, aceh_confidence, word_count, topic, sentiment, collector
   - Tambah kolom data_source: "news" / "survey" / "interview"
   - Re-index ID berurutan

2. Buat script scraping/12_triangulation.py:
   - Input: combined_text.csv + survey_structured.csv
   - Hitung evidence per hypothesis H1-H6 dari setiap sumber:
     * H1 (Funding): topic "funding" % dari scraping + Q12 ranking dari survey 
       + kutipan interview
     * H2 (Talent): topic "talent" % + Q12 + interview
     * H3 (Kampus dependency): cross-tab wilayah×topic + interview PST/Bepal
     * H4 (Follow-up lemah): topic "ecosystem" neg% + Q8 survey + interview
     * H5 (Market access): topic "market_access" % + Q12 + interview
     * H6 (Marketing > Product): topic analysis + Q7b survey + interview
   - Output: triangulation_matrix.csv + triangulation_report.md

3. Jalankan dan verifikasi

Catatan:
- Scraping mendominasi combined dataset (99.4%) — ini normal
- Untuk sentiment analysis, prioritaskan survey+interview (scraping 86% neutral)
- Hypothesis H1-H6 mapping ada di planning/panduan-data-strategy.md Section 6
```

#### Step 3: Buat `scraping/11_merge_all_sources.py`

**Input**:
- `data/processed/labeled_dataset_final.csv` (scraping, 13.840 rows)
- Survey open-ended rows (~30 rows, dari output Script 1)
- `data/processed/interview_dataset.csv` (~40-60 rows)
- `data/processed/social_media_labeled.csv` *(opsional — jika sudah tersedia)*

**Proses**:

```text
4 Sumber Text (social media opsional)
│
├── Scraping (13,840 rows)
│   ├── Tambah kolom data_source = "news"
│   └── Standardisasi kolom
│
├── Survey Open-ended (~30 rows)
│   ├── Tambah kolom data_source = "survey"
│   └── Standardisasi kolom
│
├── Interview (~40-60 rows)
│   ├── Tambah kolom data_source = "interview"
│   └── Standardisasi kolom
│
├── Social Media (opsional, jika file ada)
│   ├── Tambah kolom data_source = "social_media"
│   └── Standardisasi kolom
│
└── pd.concat() → combined_text.csv
    ├── Re-index: id = 1, 2, 3, ...
    ├── Isi kolom kosong dengan ""
    └── Validasi: semua kolom required ada
```

> [!NOTE]
> Script `11_merge_all_sources.py` akan otomatis mendeteksi apakah `social_media_labeled.csv` ada. Jika belum ada, merge tetap jalan dengan 3 sumber lainnya. Jika nanti data social media tersedia, cukup re-run script ini.

**Output — `combined_text.csv`**:

Kolom unified (minimum required):

| Kolom | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `id` | int | ✅ | ID berurutan (1, 2, 3, ...) |
| `paragraph_id` | str | ✅ | ID asli (NEWS_XXXX / SRV_XXXX / INT_XXXX / SM_XXXX) |
| `text` | str | ✅ | Teks bermakna |
| `source_portal` | str | ✅ | antaranews.com / survey / interview / twitter / youtube / linkedin |
| `data_source` | str | ✅ | news / survey / interview / social_media |
| `publish_date` | str | ✅ | Tanggal |
| `aceh_confidence` | str | ✅ | high / medium / low |
| `word_count` | int | ✅ | Jumlah kata |
| `topic` | str | ✅ | 8 kategori + "" (kosong) |
| `sentiment` | str | ✅ | positive / negative / neutral |
| `collector` | str | ✅ | Aulia |

**Estimasi total**: ~13.910-13.930 rows (tanpa social media), lebih jika social media tersedia

#### Step 4: Buat `scraping/12_triangulation.py`

**Input**: `combined_text.csv` + `survey_structured.csv`

**Proses per Hypothesis**:

```text
Untuk setiap H1-H6:
│
├── DARI SCRAPING (combined_text.csv where data_source="news"):
│   ├── Hitung % paragraf dengan topic terkait
│   ├── Hitung sentiment distribution untuk topic itu
│   └── Ambil sample paragraf sebagai evidence
│
├── DARI SURVEY (survey_structured.csv):
│   ├── Hitung % responden yang menyebut tantangan terkait (Q12)
│   ├── Hitung mean Likert score terkait (Q15-20)
│   ├── Ambil kutipan open-ended (Q21-23) yang relevan
│   └── Cross-tab jika relevan (wilayah × tantangan)
│
├── DARI INTERVIEW (combined_text.csv where data_source="interview"):
│   ├── Hitung jumlah unit yang relevan per narasumber
│   ├── Ambil kutipan langsung sebagai evidence
│   └── Identifikasi apakah supporting atau contradicting
│
├── DARI SOCIAL MEDIA (combined_text.csv where data_source="social_media"):
│   ├── Hitung % post/komentar dengan topic terkait (jika data tersedia)
│   ├── Hitung sentiment distribution (lebih variatif dari berita)
│   └── Ambil kutipan sebagai evidence opini publik
│
└── KESIMPULAN per hypothesis:
    ├── Status: SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED
    ├── Strength: berapa sumber yang mendukung (1/4, 2/4, 3/4, 4/4)
    └── Key evidence dari setiap sumber
```

**Output — `triangulation_matrix.csv`**:

| Kolom | Contoh |
|-------|--------|
| `hypothesis` | H1 |
| `hypothesis_desc` | Funding adalah masalah utama |
| `scraping_evidence` | "funding" = 14.2% topics, 91 neg sentiment |
| `scraping_metric` | 0.142 |
| `survey_evidence` | 5/11 (45%) pilih "Akses Pendanaan" |
| `survey_metric` | 0.455 |
| `interview_evidence` | PST: mesin belum mampu; SuratPlus: dari lomba |
| `interview_count` | 2/3 narasumber |
| `social_media_evidence` | "susah banget cari funding di Aceh" (jika tersedia) |
| `social_media_count` | X posts / Y comments (jika tersedia) |
| `convergence` | SUPPORTED |
| `strength` | 3/3 sources converge (atau 4/4 jika social media tersedia) |

**Output — `triangulation_report.md`**: Laporan naratif per hypothesis

---

### Chat Session 3: Social Media (Opsional) + EDA + Visualisasi + Dashboard

**Estimasi**: Sedang-Berat (banyak grafik + analisis + opsional social media)

#### Scope Chat 3:
1. **(Jika data tersedia)** Buat `scraping/10c_process_social_media.py` → bersihkan + label social media
2. **(Jika data tersedia)** Re-run `scraping/11_merge_all_sources.py` → update `combined_text.csv`
3. Buat/update `scraping/06_eda.py` untuk multi-source analysis
4. Visualisasi survey structured (radar, bar, Likert)
5. Visualisasi triangulation
6. Update dashboard (Fase 5)

#### Prompt untuk Chat 3:

```
@materi-4 ini folder projek kita
@planning ini folder planning

Lanjutan Fase 3.5: Integrasi Dataset. Ini Chat Session 3 dari 3 (final).
Planning lengkap: planning/fase-3.5-integrasi-data.md

Dataset dari Chat 1 & 2 sudah siap:
- data/processed/combined_text.csv (scraping + survey open-ended + interview)
- data/processed/survey_structured.csv (data terstruktur survey, 11 responden)
- data/processed/interview_dataset.csv (interview units, ~40-60 rows)
- data/processed/triangulation_matrix.csv (evidence per hypothesis H1-H6)
- data/processed/triangulation_report.md (laporan naratif)

DATA BARU (jika tersedia):
- data/social_media_clean.csv — dari rekan tim (X, YouTube, LinkedIn)
  Format: text, source_portal, publish_date, url, account, content_type
  BELUM di-label. Jika file ini ada, proses dulu sebelum EDA.
  Jika file ini BELUM ada, skip social media dan lanjut EDA.

TUGAS CHAT INI:
1. (Jika social_media_clean.csv ada) Buat scraping/10c_process_social_media.py:
   - Bersihkan: filter Aceh-specific, hapus noise, min 5 kata
   - Label topic+sentiment semi-auto (keyword matching + manual review)
   - Output: data/processed/social_media_labeled.csv
   - Lalu re-run 11_merge_all_sources.py untuk update combined_text.csv

2. Buat/update scraping/06_eda.py → EDA multi-source:
   - Topic distribution per data_source (stacked bar)
   - Sentiment distribution per topic (heatmap)
   - Word cloud per topic
   - Source composition pie chart

3. Visualisasi survey (file baru atau di 06_eda.py):
   - Radar chart persepsi ekosistem 6 dimensi (Q15-20, mean per dimensi)
   - Horizontal bar chart ranking tantangan (Q12, frekuensi)
   - Likert diverging bar chart (distribusi jawaban Q15-20)
   - Bar chart kemudahan talent (Q13) dan pasar (Q14)

4. Visualisasi triangulation:
   - Evidence summary table per hypothesis (HTML atau image)
   - Convergence indicator (berapa sumber mendukung per H)

5. Update dashboard Fase 5 untuk menampilkan combined insights

Catatan:
- Untuk sentiment, andalkan survey+interview+social media (scraping 86% neutral)
- Untuk topic, andalkan scraping (volume besar)
- N=11 survey: statistik deskriptif saja, jangan inferensial
- Social media perlu keyword tambahan untuk bahasa informal/slang
- Simpan semua grafik di data/processed/eda_report/
```

---

## 🗺️ Mapping Hypothesis × Data Source

| Hypothesis | Scraping (Topic Analysis) | Survey (Q Terkait) | Interview (Narasumber) | Social Media (Jika Tersedia) |
|-----------|--------------------------|-------------------|----------------------|-----------------------------|
| **H1**: Funding masalah utama | Topic `funding` frequency + sentiment | Q12 ranking tantangan + Q16 persepsi pendanaan (mean Likert) | PST: biaya produksi, SuratPlus: funding dari lomba | Post tentang fundraising / cari investor |
| **H2**: Talent hambatan | Topic `talent` frequency | Q12 + Q13 kemudahan talent | Bepal: kerja sendiri butuh tim, SuratPlus: sulit cari talent AI | Post tentang hiring / cari developer |
| **H3**: Luar BA bergantung kampus | Cross-tab `wilayah × topic` | Q7a sumber program | PST: bergantung Unimal, Bepal: interaksi kampus | — (sulit di-filter dari social media) |
| **H4**: Program kurang follow-up | Topic `ecosystem` + negative sentiment | Q8 tindak lanjut program | PST: "program 3 bulan ga ada follow-up" | Komentar tentang program inkubator |
| **H5**: Market access hambatan | Topic `market_access` frequency | Q12 + Q14 kemudahan pasar | PST: pameran banyak tapi belum bisa jual sendiri | Post tentang cari customer / pasar |
| **H6**: Digital marketing > product dev | Topic distribution analysis | Q7b jenis dukungan diterima | SuratPlus: "dukungan dominan workshop/eksposur" | Jenis konten yang di-share (marketing vs teknis) |

---

## ✅ Checklist Kesiapan Fase 3.5

Semua kriteria berikut wajib berstatus `[x]` sebelum melangkah ke **Fase 4 (EDA & ML Model)**:

### Wajib (Blocking) — 100% TERPENUHI
- [x] `10_process_survey.py` — Berjalan mulus, menghasilkan `survey_structured.csv` (12 responden) + rows open-ended berlabel
- [x] `10b_process_interviews.py` — Berhasil extract 3 interview docx → `interview_dataset.csv` (113 unit ide)
- [x] `11_merge_all_sources.py` — Menghasilkan `combined_text.csv` (13.978 baris) dengan kolom unified
- [x] `12_triangulation.py` — Menghasilkan `triangulation_matrix.csv` + `triangulation_report.md`
- [x] **Survey open-ended berlabel** — Semua 25 baris memiliki topic + sentiment
- [x] **Interview berlabel** — Semua 113 units memiliki topic + sentiment
- [x] **Combined dataset valid** — Tidak ada kolom critical yang kosong/NaN di rows survey+interview
- [x] **Triangulasi H1-H6** — Setiap hypothesis memiliki evidence konvergen dari 3/3 sumber data
- [x] **EDA multi-source** — Grafik komposisi, topic, & sentiment per sumber tersedia (13 grafik PNG)
- [x] **Survey visualisasi** — Radar chart 6 dimensi, ranking tantangan, & Likert diverging chart tersedia

### Opsional (Non-blocking, tergantung ketersediaan data dari rekan)
- [ ] `10c_process_social_media.py` — Social media dibersihkan + dilabel (Data rekan belum tersedia, arsitektur non-blocking siap integrasi kapan saja)
- [ ] **Social media berlabel** — Semua rows punya topic + sentiment
- [ ] **Combined dataset di-update** — `11_merge_all_sources.py` di-rerun setelah social media masuk
- [ ] **Triangulation di-update** — `12_triangulation.py` di-rerun dengan evidence social media

---

## 🚨 Troubleshooting & Failure Modes

| Gejala Masalah | Akar Masalah | Tindakan Korektif |
|---|---|---|
| `python-docx` tidak bisa baca file interview | Nama file mengandung spasi di awal | Gunakan path lengkap dengan spasi, wrap dalam quotes |
| Survey CSV parsing error | Kolom mengandung koma di dalam value (multi-select Q12) | Gunakan `pd.read_csv()` yang otomatis handle quoted fields |
| Interview segmentasi terlalu banyak unit kecil | Split terlalu agresif | Filter minimum 5 kata per unit, gabung kalimat pendek |
| Interview segmentasi terlalu sedikit unit | Jawaban panjang tidak di-split | Split by topik/ide, bukan by titik saja |
| Topic labeling interview tidak akurat | Auto-labeler dilatih dari berita, bukan bahasa informal | Manual review wajib untuk semua interview units |
| Combined dataset kolom tidak match | Scraping punya 18 kolom, interview punya kolom berbeda | Standardisasi ke kolom minimum required sebelum concat |
| Triangulation matrix kosong untuk 1 hypothesis | Tidak ada evidence dari sumber tertentu | Isi dengan "No evidence available" — ini finding yang valid |
| Social media data terlalu banyak noise | Rekan tidak filter dengan ketat | Re-filter di `10c_process_social_media.py`: min 5 kata, keyword Aceh wajib ada |
| Social media auto-labeling miss banyak | Bahasa informal tidak match keyword formal | Tambah keyword informal ke labeling rules khusus social media (slang, singkatan) |
| Social media belum tersedia saat Chat 3 | Rekan belum selesai scraping | Lanjut Chat 3 tanpa social media. Re-run merge + triangulation nanti setelah data masuk |

---

## 📝 Catatan Penting

1. **Scraping mendominasi combined dataset (~99%)** — Ini normal dan bukan masalah. Triangulasi bukan soal kuantitas, tapi perspektif berbeda. 30 jawaban survey + 50 unit interview + social media posts sudah cukup untuk cross-validate temuan dari 13.840 paragraf berita.

2. **Interview docx mengandung template/cheat sheet** — Di akhir setiap file docx ada "INTERVIEW CHEAT SHEET", "Opening Script", "Probing Phrases", dll. Script `10b_process_interviews.py` HARUS memfilter ini agar tidak masuk dataset.

3. **PII (Personally Identifiable Information)** — Survey kolom terakhir berisi WhatsApp/Email. Script WAJIB menghapus kolom ini dari output `survey_structured.csv`.

4. **Determinisme** — Semua script harus deterministic. Input yang sama → output yang sama. Tidak ada elemen random/seed.

5. **Social media bersifat non-blocking** — Pipeline didesain agar social media bisa ditambahkan kapan saja tanpa mengubah arsitektur. Script `11_merge_all_sources.py` otomatis mendeteksi ketersediaan file `social_media_labeled.csv`. Jika belum ada, merge tetap jalan dengan sumber lainnya.

6. **Perbedaan bahasa social media vs berita** — Social media menggunakan bahasa informal (slang, singkatan, emoji). Keyword list di `labeling_rules.py` mungkin tidak cukup. Script `10c_process_social_media.py` perlu keyword tambahan khusus untuk bahasa informal, contoh: "susah" → "sulit", "gk ada" → "tidak ada", "duit" → "dana".
