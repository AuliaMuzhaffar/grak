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
import warnings
warnings.filterwarnings("ignore")
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
# REGEX KOMPILASI (EFISIEN & BEBAS FALSE POSITIVE)
# ============================================================
# Gunakan word boundary \b agar akronim pendek seperti 'usk' tidak cocok di 'termasuk' / 'fokuskan'
ACEH_REGEX = re.compile(
    r"\b(?:" + "|".join(re.escape(k) for k in ACEH_KEYWORDS) + r")\b",
    flags=re.IGNORECASE,
)


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
    - HIGH: text itu sendiri menyebut Aceh/lokasi di Aceh (kata utuh via regex)
    - MEDIUM: judul artikel menyebut Aceh (paragraf bagian dari artikel Aceh)
    - LOW: tidak ada mention Aceh sama sekali
    """
    if not isinstance(text, str):
        return "low"
    
    # HIGH: text mengandung keyword Aceh (Word Boundary \b)
    if ACEH_REGEX.search(text):
        return "high"
    
    # MEDIUM: judul mengandung keyword Aceh (Word Boundary \b)
    if isinstance(article_title, str) and ACEH_REGEX.search(article_title):
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
    
    df = pd.read_csv(PARAGRAPHS_RAW_CSV).copy()
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
    df = df.copy()
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
