# Fase 2: Data Cleaning & Deduplication

> **Estimasi waktu**: 0.5 - 1 hari kerja  
> **Prioritas**: 🔴 P0  
> **Prasyarat**: Fase 1 selesai (articles_database.csv dan paragraphs_raw.csv sudah updated)  
> **Output**: `public_text_news_clean.csv` — Dataset bersih siap labeling  

---

## 🎯 Tujuan Fase Ini

1. **Refactor `04_cleaning.py`** — Perbaiki near-duplicate detection yang sebelumnya di-skip
2. **Bersihkan data lebih agresif** — Tambah pattern boilerplate, hapus noise
3. **Gabungkan data lama + baru** — Merge hasil re-scrape (Fase 1) dengan data existing
4. **Quality assurance** — Validasi dataset final memenuhi standar kualitas

---

## 📋 Daftar File yang Dibuat/Diubah

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/lib/dedup.py` | Near-duplicate detector menggunakan MinHash |
| **[MODIFY]** | `scraping/04_cleaning.py` | Refactor dari `03_cleaning.py` lama |
| **[MODIFY]** | `scraping/config.py` | Tambah boilerplate patterns baru |

---

## Step 1: Install Dependencies

```bash
pip install datasketch   # Untuk MinHash (fast near-duplicate detection)
```

### Kenapa MinHash?

Script lama (`03_cleaning.py`) pakai Jaccard similarity O(n²):
- 7,961 baris → 7961 × 7960 / 2 = **31,6 JUTA perbandingan** 
- Makanya di-skip kalau >2,000 baris

MinHash + LSH (Locality-Sensitive Hashing):
- Kompleksitas ~O(n) — bisa handle 100K+ baris dalam detik
- Akurasi ≥95% dibanding Jaccard exact

---

## Step 2: Buat `lib/dedup.py` — Near-Duplicate Detector

**File**: `sprint-3/materi-4/scraping/lib/dedup.py`

```python
"""
lib/dedup.py — Near-duplicate detection menggunakan MinHash LSH
GRAK 2026 · Sprint 3

Cara pakai:
    from lib.dedup import find_near_duplicates
    
    texts = ["paragraf satu...", "paragraf dua...", ...]
    duplicate_indices = find_near_duplicates(texts, threshold=0.85)
    # duplicate_indices = {3, 7, 15, ...}  ← index yang merupakan duplikat
"""

from datasketch import MinHash, MinHashLSH


def _text_to_shingles(text: str, k: int = 3) -> set[str]:
    """
    Pecah text menjadi k-shingles (subsequence k kata berurutan).
    
    Contoh (k=3):
        "saya suka makan nasi goreng" → {"saya suka makan", "suka makan nasi", "makan nasi goreng"}
    
    Kenapa shingles, bukan words?
        - Shingles menangkap urutan kata (konteks)
        - Lebih akurat daripada bag-of-words untuk deteksi duplikat
    """
    words = text.lower().split()
    if len(words) < k:
        return {text.lower()}
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}


def _create_minhash(shingles: set[str], num_perm: int = 128) -> MinHash:
    """Buat MinHash signature dari set of shingles."""
    m = MinHash(num_perm=num_perm)
    for s in shingles:
        m.update(s.encode("utf-8"))
    return m


def find_near_duplicates(
    texts: list[str],
    threshold: float = 0.85,
    num_perm: int = 128,
) -> set[int]:
    """
    Temukan index-index yang merupakan near-duplicate.
    
    Untuk setiap cluster duplikat, SIMPAN yang pertama (index terkecil),
    dan TANDAI sisanya untuk dihapus.
    
    Args:
        texts: List of text strings
        threshold: Similarity threshold (0.0 - 1.0). Default 0.85 = 85% mirip
        num_perm: Jumlah permutasi MinHash. Lebih tinggi = lebih akurat tapi lambat.
    
    Returns:
        Set of indices yang merupakan duplikat (harus dihapus)
    
    Contoh:
        texts = ["halo dunia", "hello world", "halo dunia ini"]
        duplicates = find_near_duplicates(texts, threshold=0.8)
        # duplicates mungkin = {2} (index 2 mirip dengan index 0)
    """
    if len(texts) < 2:
        return set()
    
    # Step 1: Buat MinHash untuk setiap text
    minhashes = []
    for text in texts:
        shingles = _text_to_shingles(text)
        mh = _create_minhash(shingles, num_perm)
        minhashes.append(mh)
    
    # Step 2: Masukkan ke LSH index
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    for i, mh in enumerate(minhashes):
        try:
            lsh.insert(str(i), mh)
        except ValueError:
            # Duplicate key — text persis sama, tandai untuk hapus
            pass
    
    # Step 3: Query setiap text, cari yang mirip
    to_remove = set()
    
    for i, mh in enumerate(minhashes):
        if i in to_remove:
            continue
        
        # Cari semua text yang mirip dengan text[i]
        candidates = lsh.query(mh)
        
        for candidate_str in candidates:
            j = int(candidate_str)
            if j > i and j not in to_remove:
                # j mirip dengan i → hapus j (simpan yang pertama)
                to_remove.add(j)
    
    return to_remove
```

### Verifikasi Step 2:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "
from lib.dedup import find_near_duplicates

# Test dengan data dummy
texts = [
    'Pemerintah Aceh mendukung pengembangan startup digital di Banda Aceh',
    'Pemerintah Aceh sangat mendukung pengembangan startup digital di Banda Aceh melalui program',
    'UMKM di Lhokseumawe mengalami pertumbuhan signifikan',
    'Pemerintah Aceh mendukung pengembangan startup digital di Banda Aceh hari ini',
    'Ekonomi kreatif di Aceh terus berkembang pesat',
]

dupes = find_near_duplicates(texts, threshold=0.7)
print(f'Duplikat ditemukan di index: {dupes}')
print(f'Text yang tersisa: {len(texts) - len(dupes)} dari {len(texts)}')
print('✅ Dedup OK')
"
```

**Output yang diharapkan**: Index 1 dan/atau 3 terdeteksi sebagai duplikat dari index 0.

---

## Step 3: Update `config.py` — Tambah Boilerplate Patterns

**File**: `sprint-3/materi-4/scraping/config.py`

### Tambahkan pattern baru ke `BOILERPLATE_PATTERNS`:

```python
# Tambahkan di list BOILERPLATE_PATTERNS yang sudah ada:

BOILERPLATE_PATTERNS = [
    # --- Pattern yang sudah ada (jangan hapus) ---
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
    
    # --- Pattern BARU (tambahan) ---
    "lihat juga",
    "artikel terkait",
    "berita terkait",
    "berita populer",
    "trending",
    "most read",
    "baca berita",
    "share this",
    "bagikan",
    "tweet",
    "whatsapp",
    "telegram",
    "facebook",
    "instagram",
    "tiktok",
    "youtube",
    "podcast",
    "donasi",
    "berlangganan",
    "newsletter",
    "all rights reserved",
    "disclaimer",
    "kebijakan privasi",
    "privacy policy",
    "terms of service",
    "syarat dan ketentuan",
    "hubungi kami",
    "contact us",
    "redaksi",
    "kontak redaksi",
    "alamat redaksi",
    "tentang kami",
    "about us",
    "follow us",
    "gabung channel",
    "join channel",
    "cek berita",
    "pewarta",
    "kontributor",
    "foto:",
    "video:",
    "infografis:",
    "ilustrasi:",
]
```

---

## Step 4: Buat `04_cleaning.py` — Refactored Cleaning Pipeline

**File**: `sprint-3/materi-4/scraping/04_cleaning.py`

### Perbedaan dari versi lama (`03_cleaning.py`):

| Aspek | Lama | Baru |
|-------|------|------|
| Near-duplicate | Jaccard O(n²), skip kalau >2000 | MinHash O(n), handle 100K+ |
| Boilerplate | 30 pattern | 60+ pattern |
| Text cleaning | Regex sederhana | + Hapus emoji, URL dalam text, email |
| Validation | Tidak ada | Validasi: min 5 kata, max 500 kata, ratio huruf vs angka |
| Quality report | Print ringkasan | + Simpan quality_report.json |

### Code lengkap:

```python
"""
04_cleaning.py — Data Cleaning & Deduplication Pipeline (Refactored)
GRAK 2026 · Sprint 3

CARA PAKAI:
  python3 04_cleaning.py

PRASYARAT:
  → Sudah jalankan 03_extraction.py (paragraphs_raw.csv harus ada)
  → pip install datasketch

INPUT:
  → data/paragraphs_raw.csv (dari 03_extraction.py)

OUTPUT:
  → data/processed/public_text_news_clean.csv (DATASET BERSIH ✅)
  → data/processed/quality_report.json (laporan kualitas)

WAKTU: ~1-3 menit (tergantung jumlah data)
"""

import os
import sys
import re
import json
import pandas as pd
from datetime import datetime

# Import shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DATA_DIR, PARAGRAPHS_RAW_CSV, ARTICLES_DB_CSV,
    ACEH_KEYWORDS, BOILERPLATE_PATTERNS, MIN_PARAGRAPH_LENGTH,
)
from lib.dedup import find_near_duplicates
from lib.logger import get_logger

# Output paths
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
CLEAN_CSV = os.path.join(PROCESSED_DIR, "public_text_news_clean.csv")
QUALITY_REPORT = os.path.join(PROCESSED_DIR, "quality_report.json")

# Juga tetap simpan di lokasi lama untuk backward compatibility
LEGACY_CLEAN_CSV = os.path.join(DATA_DIR, "public_text_news_clean.csv")

log = get_logger("04_cleaning")


# ============================================================
# CLEANING FUNCTIONS
# ============================================================

def clean_text(text: str) -> str:
    """
    Bersihkan text dari noise.
    
    Langkah:
    1. Hapus URL (http://..., https://...)
    2. Hapus email addresses  
    3. Hapus emoji
    4. Hapus karakter non-printable
    5. Normalize whitespace
    6. Strip leading/trailing
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Hapus URL
    text = re.sub(r"https?://\S+", "", text)
    
    # 2. Hapus email
    text = re.sub(r"\S+@\S+\.\S+", "", text)
    
    # 3. Hapus emoji (Unicode ranges untuk emoji)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)
    
    # 4. Hapus karakter non-printable (kecuali newline)
    text = re.sub(r"[^\x20-\x7E\u00C0-\u024F\u1E00-\u1EFF\u0100-\u017F\s.,!?;:()\"\'\-/&%@#+=]", "", text)
    
    # 5. Normalize whitespace (multiple spaces → single space)
    text = re.sub(r"\s+", " ", text)
    
    # 6. Strip
    text = text.strip()
    
    return text


def is_boilerplate(text: str) -> bool:
    """
    Cek apakah text adalah boilerplate (konten non-artikel).
    
    Returns: True jika boilerplate (harus dihapus)
    """
    text_lower = text.lower().strip()
    
    # Cek pattern dari config
    for pattern in BOILERPLATE_PATTERNS:
        if pattern in text_lower:
            return True
    
    # Pattern regex tambahan
    regex_patterns = [
        r"^\([\w\s/]+\)$",           # (Reporter/Editor) format
        r"^foto\s*:",                  # Foto: ...
        r"^ilustrasi",                 # Ilustrasi ...
        r"^baca\s*:",                  # Baca: ...
        r"^\*{3,}",                    # *** separator
        r"^-{3,}",                     # --- separator
        r"^halaman\s+\d",             # Halaman 1, 2, ...
        r"^share\s",                   # Share button text
        r"^loading",                   # Loading text
        r"^\d+\s*(menit|jam|hari)\s+lalu",  # "5 menit lalu"
        r"^(senin|selasa|rabu|kamis|jumat|sabtu|minggu),\s+\d",  # Tanggal saja
        r"^\(\d+/\d+\)",              # (1/5) paging
    ]
    
    for pattern in regex_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False


def is_valid_paragraph(text: str) -> bool:
    """
    Validasi apakah paragraf layak masuk dataset.
    
    Criteria:
    1. Minimal 5 kata
    2. Maksimal 500 kata (lebih dari itu kemungkinan error parsing)
    3. Ratio huruf vs total karakter > 50% (bukan deretan angka/simbol)
    4. Ada minimal 3 kata unik (bukan pengulangan)
    5. Panjang minimal 50 karakter
    """
    if not text or len(text) < MIN_PARAGRAPH_LENGTH:
        return False
    
    words = text.split()
    word_count = len(words)
    
    # Min 5 kata
    if word_count < 5:
        return False
    
    # Max 500 kata
    if word_count > 500:
        return False
    
    # Ratio huruf > 50%
    alpha_chars = sum(1 for c in text if c.isalpha())
    total_chars = len(text)
    if total_chars > 0 and (alpha_chars / total_chars) < 0.5:
        return False
    
    # Min 3 kata unik
    unique_words = set(w.lower() for w in words)
    if len(unique_words) < 3:
        return False
    
    return True


def calculate_aceh_confidence(text: str, article_title: str) -> str:
    """
    Tentukan seberapa yakin text ini berkaitan dengan Aceh.
    
    Returns: "high", "medium", atau "low"
    
    Logic:
    - HIGH: text itu sendiri menyebut Aceh/lokasi di Aceh
    - MEDIUM: judul artikel menyebut Aceh (paragraf bagian dari artikel Aceh)
    - LOW: tidak ada mention Aceh sama sekali
    """
    text_lower = text.lower()
    title_lower = article_title.lower() if isinstance(article_title, str) else ""
    
    # HIGH: text mengandung keyword Aceh
    for keyword in ACEH_KEYWORDS:
        if keyword in text_lower:
            return "high"
    
    # MEDIUM: judul mengandung keyword Aceh
    for keyword in ACEH_KEYWORDS:
        if keyword in title_lower:
            return "medium"
    
    return "low"


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    # ===== Cek prasyarat =====
    if not os.path.exists(PARAGRAPHS_RAW_CSV):
        print(f"❌ File tidak ditemukan: {PARAGRAPHS_RAW_CSV}")
        print("   Jalankan 03_extraction.py terlebih dahulu!")
        return
    
    df = pd.read_csv(PARAGRAPHS_RAW_CSV)
    initial_count = len(df)
    
    print("=" * 65)
    print("🧹 CLEANING — Data Cleaning & Deduplication Pipeline")
    print(f"   Total paragraf mentah: {initial_count}")
    print("=" * 65)
    print()
    
    log.info("Starting cleaning pipeline", initial_count=initial_count)
    
    # Track statistics
    stats = {
        "initial_count": initial_count,
        "steps": {},
    }
    
    # ===== STEP 1: Clean text =====
    print("📋 Step 1/6: Membersihkan text (hapus URL, emoji, noise)...")
    df["text"] = df["text"].apply(clean_text)
    
    # Hapus baris kosong
    df = df[df["text"].str.len() > 0].reset_index(drop=True)
    stats["steps"]["1_clean_text"] = len(df)
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 2: Validasi paragraf =====
    print("📋 Step 2/6: Validasi paragraf (min kata, max kata, ratio huruf)...")
    mask_valid = df["text"].apply(is_valid_paragraph)
    removed = (~mask_valid).sum()
    df = df[mask_valid].reset_index(drop=True)
    stats["steps"]["2_validation"] = len(df)
    print(f"   Dihapus: {removed} paragraf invalid")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 3: Hapus boilerplate =====
    print("📋 Step 3/6: Menghapus boilerplate (60+ pattern)...")
    mask_not_bp = ~df["text"].apply(is_boilerplate)
    removed = (~mask_not_bp).sum()
    df = df[mask_not_bp].reset_index(drop=True)
    stats["steps"]["3_boilerplate"] = len(df)
    print(f"   Dihapus: {removed} boilerplate")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 4: Hapus exact duplicates =====
    print("📋 Step 4/6: Menghapus exact duplicates...")
    before = len(df)
    df = df.drop_duplicates(subset=["text"], keep="first").reset_index(drop=True)
    removed = before - len(df)
    stats["steps"]["4_exact_dedup"] = len(df)
    print(f"   Dihapus: {removed} exact duplicates")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 5: Hapus near-duplicates (MinHash) =====
    print("📋 Step 5/6: Menghapus near-duplicates (MinHash LSH)...")
    print("   ⏳ Ini bisa memakan 1-2 menit, tunggu...")
    
    before = len(df)
    texts = df["text"].tolist()
    duplicate_indices = find_near_duplicates(texts, threshold=0.85)
    
    if duplicate_indices:
        df = df.drop(df.index[list(duplicate_indices)]).reset_index(drop=True)
    
    removed = before - len(df)
    stats["steps"]["5_near_dedup"] = len(df)
    print(f"   Dihapus: {removed} near-duplicates")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 6: Tag Aceh confidence =====
    print("📋 Step 6/6: Menandai relevansi Aceh...")
    df["aceh_confidence"] = df.apply(
        lambda row: calculate_aceh_confidence(
            row["text"],
            row.get("article_title", "")
        ),
        axis=1,
    )
    
    confidence_counts = df["aceh_confidence"].value_counts()
    for level in ["high", "medium", "low"]:
        count = confidence_counts.get(level, 0)
        pct = count / len(df) * 100 if len(df) > 0 else 0
        emoji = "🟢" if level == "high" else ("🟡" if level == "medium" else "🔴")
        print(f"   {emoji} {level}: {count} ({pct:.1f}%)")
    
    stats["steps"]["6_aceh_tagged"] = {
        "high": int(confidence_counts.get("high", 0)),
        "medium": int(confidence_counts.get("medium", 0)),
        "low": int(confidence_counts.get("low", 0)),
    }
    
    # ===== FINALIZE =====
    # Update word_count
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    
    # Re-index
    df = df.reset_index(drop=True)
    df["paragraph_id"] = range(1, len(df) + 1)
    
    # Tambah kolom untuk labeling (kosong, diisi di Fase 3)
    for col in ["topic", "sentiment", "labeling_notes"]:
        if col not in df.columns:
            df[col] = ""
    
    # Reorder kolom
    output_columns = [
        "paragraph_id",
        "text",
        "article_title",
        "article_url",
        "source_portal",
        "publish_date",
        "aceh_confidence",
        "word_count",
        "query_used",
        "collector",
        "topic",
        "sentiment",
        "labeling_notes",
    ]
    
    for col in output_columns:
        if col not in df.columns:
            df[col] = ""
    
    df_output = df[output_columns]
    
    # Simpan ke processed/
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_output.to_csv(CLEAN_CSV, index=False, encoding="utf-8-sig")
    
    # Juga simpan ke lokasi lama (backward compatibility)
    df_output.to_csv(LEGACY_CLEAN_CSV, index=False, encoding="utf-8-sig")
    
    # ===== Quality Report =====
    stats["final_count"] = len(df_output)
    stats["reduction_pct"] = round((1 - len(df_output) / initial_count) * 100, 1)
    stats["word_count_stats"] = {
        "mean": round(df_output["word_count"].mean(), 1),
        "median": round(df_output["word_count"].median(), 1),
        "min": int(df_output["word_count"].min()),
        "max": int(df_output["word_count"].max()),
    }
    stats["unique_articles"] = int(df_output["article_url"].nunique())
    stats["unique_portals"] = int(df_output["source_portal"].nunique())
    stats["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(QUALITY_REPORT, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # ===== RINGKASAN =====
    print()
    print("=" * 65)
    print("✅ CLEANING SELESAI!")
    print("=" * 65)
    print()
    print(f"📊 Ringkasan:")
    print(f"   Paragraf awal      : {initial_count}")
    print(f"   Paragraf final     : {len(df_output)}")
    print(f"   Dihapus total      : {initial_count - len(df_output)}")
    print(f"   Reduction rate     : {stats['reduction_pct']}%")
    print()
    print(f"📊 Statistik text:")
    print(f"   Rata-rata kata     : {stats['word_count_stats']['mean']}")
    print(f"   Median kata        : {stats['word_count_stats']['median']}")
    print(f"   Min / Max kata     : {stats['word_count_stats']['min']} / {stats['word_count_stats']['max']}")
    print()
    print(f"📊 Coverage:")
    print(f"   Artikel unik       : {stats['unique_articles']}")
    print(f"   Portal unik        : {stats['unique_portals']}")
    print()
    print(f"📁 DATASET BERSIH  : {CLEAN_CSV}")
    print(f"📁 Quality Report  : {QUALITY_REPORT}")
    print()
    print("▶️  Langkah selanjutnya: jalankan 'python3 05_labeling.py'")
    print("=" * 65)
    
    log.info(
        "Cleaning completed",
        initial=initial_count,
        final=len(df_output),
        reduction_pct=stats["reduction_pct"],
    )


if __name__ == "__main__":
    main()
```

### Verifikasi Step 4:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 04_cleaning.py
```

**Output yang diharapkan**:
- 6 step cleaning berurutan
- Near-duplicate detection berjalan (tidak di-skip)
- `data/processed/public_text_news_clean.csv` terbuat
- `data/processed/quality_report.json` terbuat

---

## Step 5: Verifikasi Kualitas Dataset

### 5.1 Cek statistik dasar

```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "
import pandas as pd, json

df = pd.read_csv('../data/processed/public_text_news_clean.csv')
print(f'Total baris: {len(df)}')
print(f'Unique articles: {df[\"article_url\"].nunique()}')
print(f'Unique portals: {df[\"source_portal\"].nunique()}')
print()

print('=== ACEH CONFIDENCE ===')
print(df['aceh_confidence'].value_counts())
print()

print('=== WORD COUNT DISTRIBUTION ===')
print(df['word_count'].describe())
print()

# Cek quality report
with open('../data/processed/quality_report.json') as f:
    report = json.load(f)
print(f'Reduction rate: {report[\"reduction_pct\"]}%')
"
```

### 5.2 Spot check — Baca 10 baris random

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('../data/processed/public_text_news_clean.csv')
sample = df.sample(10, random_state=42)
for _, row in sample.iterrows():
    print(f'[{row[\"aceh_confidence\"]}] [{row[\"source_portal\"]}]')
    print(f'  {row[\"text\"][:150]}...')
    print()
"
```

**Yang harus dicek manual**:
- Apakah text bermakna? (bukan boilerplate / noise)
- Apakah aceh_confidence benar? (text tentang Aceh → "high")
- Apakah ada text rusak / aneh?

### 5.3 Quality gate — Minimum criteria sebelum lanjut Fase 3

| Metric | Minimum | Target |
|--------|---------|--------|
| Total paragraf | ≥5,000 | ≥8,000 |
| Aceh confidence high+medium | ≥60% | ≥75% |
| Rata-rata kata per paragraf | ≥15 | ≥25 |
| Unique portals | ≥10 | ≥20 |
| Boilerplate leaks (spot check) | <5% | <1% |

**Jika tidak memenuhi minimum**: Review cleaning rules, mungkin terlalu agresif atau kurang agresif.

---

## ✅ Checklist Fase 2 Selesai

Semua item di bawah harus ✓ sebelum lanjut ke Fase 3:

- [ ] `lib/dedup.py` — Bisa di-import, test dedup berjalan
- [ ] `04_cleaning.py` — Jalan tanpa error, semua 6 step selesai
- [ ] `data/processed/public_text_news_clean.csv` — File terbuat
- [ ] `data/processed/quality_report.json` — File terbuat
- [ ] Near-duplicate detection **tidak** di-skip (MinHash dipakai)
- [ ] Spot check: ≥95% baris bermakna (bukan noise/boilerplate)
- [ ] Quality gate: semua minimum criteria terpenuhi

---

## 🚨 Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `ModuleNotFoundError: datasketch` | Belum install | `pip install datasketch` |
| Near-dedup sangat lambat (>10 menit) | Dataset terlalu besar | Turunkan `num_perm` dari 128 ke 64 di `lib/dedup.py` |
| Terlalu banyak data dihapus (>50%) | Threshold terlalu rendah | Naikkan threshold di `find_near_duplicates` dari 0.85 ke 0.90 |
| Boilerplate masih lolos | Pattern belum lengkap | Tambah pattern baru ke `BOILERPLATE_PATTERNS` di `config.py` |
| `KeyError: 'text'` | Kolom CSV tidak sesuai | Cek header `paragraphs_raw.csv`: `head -1 ../data/paragraphs_raw.csv` |

---

## 📝 Catatan untuk Agent / Rekan

1. **Jangan hapus file lama** — `03_cleaning.py` tetap ada sebagai backup, file baru adalah `04_cleaning.py`
2. **Lokasi output berubah** — Sekarang di `data/processed/`, bukan langsung di `data/`
3. **Backward compatibility** — File juga di-copy ke `data/public_text_news_clean.csv` (lokasi lama)
4. **MinHash threshold 0.85** — Artinya text yang 85% mirip dianggap duplikat. Kalau mau lebih ketat, naikkan ke 0.90
5. **Quality report** — Selalu cek `quality_report.json` setelah cleaning untuk pastikan kualitas OK
