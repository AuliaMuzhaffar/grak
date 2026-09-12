# 📖 Panduan Lengkap: Data Strategy & Workflow untuk Sprint 3

> **Untuk**: Aulia — GRAK 2026  
> **Konteks**: Jawaban atas kebingungan tentang data sources, social media, interview, dan bagaimana semuanya terhubung  
> **Ditulis**: 11 September 2026  

---

## 1. Memahami Gambaran Besar Sprint 3

Sebelum bahas teknis, kita perlu **zoom out** dulu. Mentormu mendesain Sprint 3 dengan logika ini:

```
Sprint 1: OBSERVE    → "Apa yang kelihatan?" (data startup)
Sprint 2: MAP        → "Apa faktor pendukungnya?" (ecosystem data)
Sprint 3: LISTEN     → "Apa yang DIRASAKAN?" (people data + text data)
```

Sprint 3 bukan tentang scraping. **Sprint 3 tentang MENDENGAR pelaku ekosistem.** Scraping hanya salah satu cara mendapatkan "suara" mereka.

### Tiga Sumber Data yang Diminta Mentor

| # | Sumber | Status | Wajib? | Kontribusi ke Analisis |
|---|--------|--------|--------|----------------------|
| 1 | **Survey** | Belum | ✅ WAJIB | Primary data: tantangan, persepsi, pengalaman |
| 2 | **Public Text** | ✅ Sebagian (news) | ✅ WAJIB | Text analysis: topic, sentiment, trend |
| 3 | **Interview** | Belum | ⚠️ OPTIONAL | Enrichment: cerita, konteks, detail |

### Apa itu "Public Text"?

Dari PDF mentormu (halaman 8):
> "Komentar Instagram & YouTube, LinkedIn, X, berita, jawaban terbuka survey."

Jadi **Public Text = GABUNGAN dari berbagai sumber**:

```
Public Text Dataset
├── Berita online          ← SUDAH ADA (7,961 paragraf) ✅
├── Komentar Instagram     ← BELUM
├── Komentar YouTube       ← BELUM  
├── Post LinkedIn          ← BELUM
├── Post X (Twitter)       ← BELUM
├── Post Threads           ← BELUM
└── Jawaban open-ended survey ← BELUM (dari survey nanti)
```

---

## 2. Apakah Data Berita yang Kamu Punya Sudah Cukup?

**Jawaban jujur: Sebagian sudah, sebagian belum.**

### Yang Sudah Terpenuhi ✅

| Requirement dari Mentor | Status |
|------------------------|--------|
| Public text dataset sudah dibuat | ✅ 7,961 paragraf dari berita |
| Setiap text memiliki source | ✅ Kolom `source_portal`, `article_url` |
| 300+ text samples | ✅ Jauh melebihi (7,961 vs 300) |

### Yang Belum Terpenuhi ❌

| Requirement | Status | Catatan |
|-------------|--------|---------|
| Text dari social media | ❌ Belum | Mentor minta: Instagram, YouTube, LinkedIn, X |
| Jawaban open-ended survey | ❌ Belum | Dari survey yang belum dijalankan |
| Sample text sudah diberi label manual | ❌ Belum | Baru di-plan di Fase 3 |

### Kabar Baik

Mentormu menulis: **"300+ text samples, jika data tersedia."** Artinya:
- 300 adalah **minimum**, bukan target wajib per sumber
- "jika data tersedia" — mentor paham bahwa social media mungkin sulit
- 7,961 paragraf berita saja sudah **jauh melebihi minimum**

---

## 3. Masalah Social Media: Analisis Jujur

Kamu benar 100%: **social media scraping untuk riset ekosistem Aceh itu problematic.**

### Kenapa Social Media Sulit untuk Riset Ini

```
MASALAH 1: Geografis tidak bisa difilter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Video TikTok "Tantangan Startup Indonesia" → komentar dari seluruh Indonesia
Post IG @startupdulu → audience nasional, bukan Aceh specific
Thread X tentang "funding startup" → diskusi nasional

→ Komentar TIDAK mewakili perspektif Aceh

MASALAH 2: API Access terbatas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instagram → API hanya untuk business accounts, bukan scraping publik
TikTok → Tidak ada public API untuk komentar
X → API gratis sangat terbatas (100 tweets/bulan)
Threads → Belum ada API publik

→ Scraping tanpa API = melanggar ToS = risiko ban

MASALAH 3: Noise ratio sangat tinggi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Komentar social media: "keren!", "mantap!", emoji, spam
vs Berita: paragraf bermakna tentang isu startup

→ Effort besar, value kecil
```

### Pendekatan REALISTIS untuk Social Media

**Jangan scrape komentar umum.** Sebaliknya, fokus pada **konten Aceh-specific**:

#### Strategi A: Curated Account Scraping (RECOMMENDED)

```
Cari akun-akun yang KHUSUS membahas startup/digital Aceh:

Instagram:
  @bandaaceh.go.id → Post tentang program digital
  @garudaspark → Post tentang inkubator Aceh
  @diskominfoaceh → Post tentang digitalisasi
  
  YANG DIAMBIL: Caption post (bukan komentar!)
  Caption biasanya ditulis oleh tim komunikasi → berkualitas, on-topic

LinkedIn:
  Search: "startup Aceh" → ambil post dan artikel
  Search: "ekosistem digital Aceh" → ambil post
  
  YANG DIAMBIL: Post + artikel (bukan komentar)
  LinkedIn post biasanya substantif dan profesional

X/Twitter:
  Search: "startup Aceh" OR "UMKM Aceh" OR "digital Aceh"
  Filter: lang:id
  
  YANG DIAMBIL: Tweet (bukan reply)
```

**Estimasi yield**: 50-100 text dari social media. Kecil tapi berkualitas.

#### Strategi B: Manual Collection (PALING AMAN)

```
1. Buka Instagram, search "startup aceh", "UMKM digital aceh"
2. Screenshot / copy-paste caption yang relevan
3. Masukkan ke spreadsheet:
   - text (caption)
   - source: "instagram"
   - account: "@namaakun"
   - date: tanggal post
   - url: link post

Waktu: 1-2 jam untuk 30-50 text
ZERO risiko ban, ZERO coding needed
```

#### Strategi C: Skip Social Media (VALID!)

```
Justifikasi ke mentor:
"Kami memutuskan untuk tidak menggunakan social media scraping karena:
1. Komentar bersifat nasional, bukan Aceh-specific
2. API access terbatas dan scraping melanggar ToS
3. Data berita online sudah melebihi target (7,961 vs 300+ min)
4. Jawaban open-ended survey akan menjadi sumber text dari pelaku langsung

Sebagai gantinya, kami menambahkan jawaban open-ended survey
sebagai public text tambahan yang lebih representatif."
```

> **Rekomendasi saya: Kombinasi A + B.** Ambil caption Instagram dari akun-akun terkait Aceh secara manual (Strategi B), plus search LinkedIn/X untuk "startup Aceh" (Strategi A). Total 30-50 text. Sisanya fokus di survey open-ended.

---

## 4. Cara Mengubah Interview Menjadi Dataset Text

Ini pertanyaan kunci. Berikut workflow lengkapnya:

### Step 1: Transkrip (Record → Text)

```
Interview 15-30 menit → transkrip text

OPSI TRANSKRIPSI:
├── Manual (tulis sambil dengar) — lambat tapi akurat
├── Google Docs voice typing — gratis, cukup akurat untuk Bahasa Indonesia
├── Whisper (OpenAI) — gratis, offline, sangat akurat
└── Otter.ai / Clova Note — berbayar tapi mudah

REKOMENDASI: Whisper (gratis + akurat)

pip install openai-whisper
whisper interview_aulia_01.mp3 --language id --model small

Output: file .txt berisi transkrip lengkap
```

### Step 2: Segmentasi (Full Text → Unit Bermakna)

Transkrip mentah:
```
"Jadi kalau saya lihat ya, di Aceh itu sebenarnya banyak anak muda yang 
kreatif. Tapi masalahnya akses ke pendanaan itu sangat terbatas. Kita 
harus ke Jakarta dulu untuk ketemu investor. Dan di sini belum ada 
accelerator yang benar-benar connect ke investor. Paling inkubator kampus 
tapi itu juga programnya pendek, 3 bulan terus selesai tidak ada 
follow-up. Harusnya ada program yang lebih panjang, yang benar-benar 
mendampingi sampai startup-nya bisa sustain."
```

Setelah segmentasi → unit-unit bermakna:

```
Unit 1: "Di Aceh itu sebenarnya banyak anak muda yang kreatif."
  → topic: talent, sentiment: positive

Unit 2: "Masalahnya akses ke pendanaan itu sangat terbatas. Kita harus 
         ke Jakarta dulu untuk ketemu investor."
  → topic: funding, sentiment: negative

Unit 3: "Di sini belum ada accelerator yang benar-benar connect ke investor."
  → topic: ecosystem, sentiment: negative

Unit 4: "Inkubator kampus programnya pendek, 3 bulan terus selesai tidak 
         ada follow-up."
  → topic: ecosystem, sentiment: negative (H4: follow-up lemah)

Unit 5: "Harusnya ada program yang lebih panjang, yang benar-benar 
         mendampingi sampai startup-nya bisa sustain."
  → topic: ecosystem, sentiment: neutral (saran)
```

### Step 3: Masukkan ke Dataset dengan Format Sama

```csv
paragraph_id,text,article_title,article_url,source_portal,publish_date,aceh_confidence,word_count,query_used,collector,topic,sentiment
INT_001,"Di Aceh banyak anak muda yang kreatif","Interview Founder X","","interview",2026-09-15,high,8,"interview_aulia","Aulia",talent,positive
INT_002,"Akses ke pendanaan sangat terbatas. Harus ke Jakarta dulu","Interview Founder X","","interview",2026-09-15,high,10,"interview_aulia","Aulia",funding,negative
```

### Rules Segmentasi Interview:

```
1. SATU UNIT = SATU IDE/ARGUMEN
   ✅ "Akses ke pendanaan sangat terbatas" (1 ide)
   ❌ "Akses ke pendanaan terbatas dan juga talent susah dicari dan 
       program inkubator kurang" (3 ide dalam 1 unit)

2. MINIMUM 5 KATA per unit (terlalu pendek = tidak bermakna)

3. HAPUS filler words:
   "Jadi kalau saya lihat ya..." → hapus "jadi kalau saya lihat ya"
   "Nah itu dia, sebenarnya..." → hapus "nah itu dia"

4. JANGAN UBAH MAKNA
   ✅ Parafrasa OK: "Susah cari developer" → "Sulit menemukan developer"
   ❌ Interpretasi TIDAK OK: "Susah cari developer" → "Talent adalah masalah utama"

5. PRESERVE KONTEKS ACEH
   Jika narasumber bilang "di sini" → ubah ke "di Aceh" atau "di Banda Aceh"
   (agar text bisa berdiri sendiri tanpa konteks interview)
```

### Script Pembantu: `convert_interview.py`

```python
"""
convert_interview.py — Konversi transkrip interview ke format dataset

CARA PAKAI:
  1. Simpan transkrip sebagai .txt (1 file per interview)
  2. Pisahkan setiap unit dengan baris kosong
  3. Jalankan: python3 convert_interview.py data/interviews/

INPUT FORMAT (file .txt):
  Baris 1: INTERVIEWEE: Nama Narasumber
  Baris 2: ROLE: Founder/Mentor/Government/dll
  Baris 3: LOCATION: Banda Aceh/Langsa/dll
  Baris 4: DATE: 2026-09-15
  Baris 5: (kosong)
  Baris 6+: Setiap paragraf = 1 unit bermakna (pisahkan dengan baris kosong)

CONTOH FILE:
  INTERVIEWEE: Ahmad Founder
  ROLE: Founder
  LOCATION: Banda Aceh
  DATE: 2026-09-15

  Akses ke pendanaan di Aceh sangat terbatas, harus ke Jakarta dulu.

  Program inkubator kampus terlalu pendek, 3 bulan tanpa follow-up.

  Sebenarnya banyak anak muda kreatif di Aceh yang punya ide bagus.

OUTPUT:
  → data/processed/interview_dataset.csv
"""

import os
import sys
import glob
import pandas as pd
from datetime import datetime


def parse_interview_file(filepath: str) -> list[dict]:
    """Parse satu file transkrip interview."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
    lines = content.strip().split("\n")
    
    # Parse header
    metadata = {}
    content_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            content_start = i + 1
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().upper()] = value.strip()
    
    interviewee = metadata.get("INTERVIEWEE", "Unknown")
    role = metadata.get("ROLE", "")
    location = metadata.get("LOCATION", "")
    date = metadata.get("DATE", "")
    
    # Parse units (split by empty lines)
    remaining = "\n".join(lines[content_start:])
    units = [u.strip() for u in remaining.split("\n\n") if u.strip()]
    
    # Filter: minimum 5 kata
    units = [u for u in units if len(u.split()) >= 5]
    
    results = []
    for unit in units:
        results.append({
            "text": unit,
            "article_title": f"Interview {interviewee}",
            "article_url": "",
            "source_portal": "interview",
            "publish_date": date,
            "aceh_confidence": "high",  # Interview pelaku Aceh = selalu high
            "word_count": len(unit.split()),
            "query_used": f"interview_{role.lower()}",
            "collector": "Aulia",
            "interviewee": interviewee,
            "role": role,
            "location": location,
        })
    
    return results


def main():
    interview_dir = sys.argv[1] if len(sys.argv) > 1 else "data/interviews"
    
    if not os.path.exists(interview_dir):
        print(f"❌ Folder tidak ditemukan: {interview_dir}")
        print(f"   Buat folder dan simpan file .txt di dalamnya")
        return
    
    txt_files = glob.glob(os.path.join(interview_dir, "*.txt"))
    
    if not txt_files:
        print(f"⚠️ Tidak ada file .txt di {interview_dir}")
        return
    
    all_units = []
    
    for filepath in sorted(txt_files):
        filename = os.path.basename(filepath)
        units = parse_interview_file(filepath)
        print(f"  ✓ {filename}: {len(units)} unit")
        all_units.extend(units)
    
    if not all_units:
        print("⚠️ Tidak ada unit yang valid")
        return
    
    df = pd.DataFrame(all_units)
    
    # Add paragraph_id
    df.insert(0, "paragraph_id", range(1, len(df) + 1))
    
    # Prefix ID with INT_ agar tidak bentrok dengan news data
    df["paragraph_id"] = df["paragraph_id"].apply(lambda x: f"INT_{x:04d}")
    
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(interview_dir))),
        "data", "processed", "interview_dataset.csv"
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print()
    print(f"✅ {len(all_units)} unit dari {len(txt_files)} interview")
    print(f"📁 Output: {output_path}")


if __name__ == "__main__":
    main()
```

---

## 5. Cara Menggabungkan Semua Sumber Data

Setelah semua sumber siap, gabungkan menjadi **satu unified dataset**:

```
DATA SOURCES                         UNIFIED DATASET
━━━━━━━━━━━                         ━━━━━━━━━━━━━━━
News (7,961 paragraf)  ──┐
                         ├──→ combined_public_text.csv
Social Media (~50 text) ─┤     (semua punya kolom yang sama)
                         │
Interview (~50-100 unit)─┤
                         │
Survey open-ended ───────┘
```

### Script Penggabungan

```python
"""
Gabungkan semua sumber ke satu dataset.
Jalankan setelah semua sumber siap.
"""
import pandas as pd
import os

DATA_DIR = "data/processed"

# Load semua sumber
sources = []

# 1. News
news_path = os.path.join(DATA_DIR, "labeled_dataset_final.csv")
if os.path.exists(news_path):
    df_news = pd.read_csv(news_path)
    df_news["data_source"] = "news"
    sources.append(df_news)
    print(f"News: {len(df_news)} rows")

# 2. Interview
interview_path = os.path.join(DATA_DIR, "interview_dataset.csv")
if os.path.exists(interview_path):
    df_int = pd.read_csv(interview_path)
    df_int["data_source"] = "interview"
    sources.append(df_int)
    print(f"Interview: {len(df_int)} rows")

# 3. Social media
social_path = os.path.join(DATA_DIR, "social_media_dataset.csv")
if os.path.exists(social_path):
    df_social = pd.read_csv(social_path)
    df_social["data_source"] = "social_media"
    sources.append(df_social)
    print(f"Social media: {len(df_social)} rows")

# 4. Survey open-ended
survey_path = os.path.join(DATA_DIR, "survey_openended.csv")
if os.path.exists(survey_path):
    df_survey = pd.read_csv(survey_path)
    df_survey["data_source"] = "survey"
    sources.append(df_survey)
    print(f"Survey: {len(df_survey)} rows")

# Gabungkan
df_combined = pd.concat(sources, ignore_index=True)

# Kolom minimum yang harus ada
required_cols = [
    "text", "source_portal", "data_source",
    "topic", "sentiment", "aceh_confidence"
]
for col in required_cols:
    if col not in df_combined.columns:
        df_combined[col] = ""

# Re-index
df_combined["id"] = range(1, len(df_combined) + 1)

output = os.path.join(DATA_DIR, "combined_public_text.csv")
df_combined.to_csv(output, index=False, encoding="utf-8-sig")
print(f"\n✅ Combined: {len(df_combined)} rows → {output}")
```

---

## 6. Mapping Data Sources ke 6 Hypothesis

Ini yang paling penting. Setiap hypothesis harus dijawab oleh **multiple sources** (triangulation):

| Hypothesis | News Data | Interview | Survey | Social Media |
|------------|-----------|-----------|--------|-------------|
| **H1** Funding masalah utama | Topic "funding" frequency | Cerita tentang cari investor | Ranking tantangan | Post tentang fundraising |
| **H2** Talent hambatan | Topic "talent" frequency | Cerita tentang cari developer | Ranking tantangan | Post tentang hiring |
| **H3** Luar BA bergantung kampus | Cross-tab wilayah × topic | Pengalaman founder luar BA | Cross-tab wilayah × program | - |
| **H4** Program kurang follow-up | Topic "ecosystem" + sentiment neg | Cerita tentang pengalaman program | Pertanyaan tentang program | - |
| **H5** Market access hambatan | Topic "market_access" frequency | Cerita tentang cari customer | Ranking tantangan | - |
| **H6** Digital marketing > product dev | Topic distribution analysis | Jenis pelatihan yang pernah diikuti | Pertanyaan jenis pelatihan | - |

### Bagaimana Hasilnya Nanti (Contoh Insight)

```
INSIGHT: Funding adalah salah satu tantangan yang paling sering dirasakan

EVIDENCE:
├── Survey: 62% responden memilih funding dalam top-3 tantangan
├── Text Analysis: "funding" muncul di 23% public text, dengan 68% sentiment negatif  
├── Interview: 3/5 narasumber menyebut kesulitan akses investor
└── Sprint 2: Hanya 2 dari 15 ecosystem actor yang menyediakan funding support

KESIMPULAN: H1 SUPPORTED — Akses funding masih menjadi salah satu 
masalah utama yang dirasakan pelaku ekosistem Aceh.
```

---

## 7. Prioritas: Apa yang Harus Dikerjakan Duluan?

Mengingat deadline minggu depan:

```
HARI 1-2: 🔴 URGENT
├── Jalankan Fase 1-2 (fix scraping + cleaning) — data berita sudah OK
├── Mulai kirim survey (Google Form) — ini PALING KRITIS
└── Kontak 5 orang untuk interview

HARI 3-4: 🔴 URGENT  
├── Jalankan Fase 3 (labeling data berita)
├── Manual collect social media text (1-2 jam, Strategi B)
├── Lakukan 2-3 interview
└── Segmentasi transkrip interview → dataset

HARI 5-6: 🟡 IMPORTANT
├── Gabungkan semua sumber (news + interview + social + survey open-ended)
├── Jalankan Fase 4 (ML model training) pada combined dataset
├── Cross-tab analysis per wilayah
└── Mulai tulis insight (5 per researcher)

HARI 7: 🟢 FINISH
├── Jalankan Fase 5 (dashboard)
├── Finalize 5-7 Grand Insights
├── Bandingkan dengan Sprint 1 & 2
└── Final report
```

### Yang Bisa Di-Skip Kalau Waktu Mepet

```
BISA DISKIP:
❌ Social media scraping otomatis (manual collect sudah cukup)
❌ Fase 1 URL resolver (data berita 660 artikel sudah cukup)
❌ Near-duplicate detection canggih (exact dedup saja OK)

TIDAK BISA DISKIP:
✅ Survey (WAJIB — primary data utama Sprint 3)
✅ Labeling (WAJIB — topic + sentiment)
✅ ML model (WAJIB — "ML baseline dibuat jika dataset mencukupi")
✅ Insight report (WAJIB — "setiap orang minimal 5 insight")
```

---

## 8. Jawaban untuk Keraguan-Keraguanmu

### "Apakah scraping berita sudah sesuai dengan yang diminta mentor?"

**YA, sebagian besar sudah.** Mentor minta "Public Text" yang termasuk berita. Data beritamu (7,961 paragraf) jauh melebihi target 300+. Yang belum ada adalah social media dan survey open-ended — keduanya bisa ditambahkan tanpa mengubah pipeline yang sudah ada.

### "Social media scraping — gimana filternya biar Aceh-specific?"

**Jangan scrape komentar umum.** Ambil caption dari akun Aceh-specific (pemerintah, inkubator, komunitas) dan search keyword "startup Aceh" di LinkedIn/X. Manual collection 1-2 jam sudah cukup.

### "Gimana cara ubah interview jadi dataset?"

**Segmentasi per ide/argumen**, bukan per kalimat. Satu unit = satu ide. Masukkan ke CSV dengan format yang sama dengan data berita. Lihat contoh di Section 4 di atas.

### "Bagaimana kalau saya merasa overwhelmed?"

**Kerjakan survey dulu.** Itu satu-satunya yang tidak bisa dikejar di hari terakhir. Sisanya (cleaning, labeling, ML, dashboard) bisa dikejar dalam 2-3 hari intensif. Data berita sudah ada dan sudah cukup.

---

## 9. Cheatsheet: Format Unified Dataset

Semua sumber data (news, interview, social media, survey) harus punya kolom yang sama:

```
| Kolom | Tipe | Contoh | Sumber |
|-------|------|--------|--------|
| id | int | 1 | All |
| text | str | "Akses ke pendanaan sangat terbatas" | All |
| source_portal | str | "antaranews.com" / "interview" / "instagram" / "survey" | All |
| data_source | str | "news" / "interview" / "social_media" / "survey" | All |
| publish_date | str | "2026-09-15" | All |
| aceh_confidence | str | "high" / "medium" / "low" | All |
| word_count | int | 8 | All |
| topic | str | "funding" | After labeling |
| sentiment | str | "negative" | After labeling |
| collector | str | "Aulia" | All |
```

Dengan format unified ini, semua analisis (topic frequency, sentiment distribution, cross-source comparison) bisa dilakukan pada satu file.
