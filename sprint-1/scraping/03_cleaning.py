"""
03_cleaning.py — Membersihkan dan memvalidasi dataset paragraf
GRAK 2026 · Sprint 3 · Materi 4

CARA PAKAI:
  python3 03_cleaning.py

PRASYARAT:
  → Sudah jalankan 02_extraction.py (paragraphs_raw.csv harus ada)

HASIL:
  → data/public_text_news_clean.csv  (DATASET FINAL ✅ siap labeling)

WAKTU: ~1-2 menit
"""

import pandas as pd
import re
import os
import sys
from collections import Counter

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DATA_DIR, PARAGRAPHS_RAW_CSV, PARAGRAPHS_CLEAN_CSV,
    ARTICLES_DB_CSV, ACEH_KEYWORDS, BOILERPLATE_PATTERNS,
    MIN_PARAGRAPH_LENGTH,
)


def clean_text(text: str) -> str:
    """Bersihkan text dari noise."""
    if not isinstance(text, str):
        return ""
    
    # Hapus multiple whitespace
    text = re.sub(r"\s+", " ", text)
    
    # Hapus leading/trailing whitespace
    text = text.strip()
    
    # Hapus karakter aneh tapi pertahankan tanda baca Indonesia
    # (titik, koma, tanda tanya, tanda seru, kurung, petik, dll)
    text = re.sub(r"[^\w\s.,!?;:()\"'\-/&%@#+=]", "", text)
    
    return text


def is_boilerplate(text: str) -> bool:
    """Cek apakah text adalah boilerplate."""
    text_lower = text.lower().strip()
    
    for pattern in BOILERPLATE_PATTERNS:
        if pattern in text_lower:
            return True
    
    # Pattern tambahan yang sering muncul di berita Indonesia
    extra_patterns = [
        r"^\(\w+/\w+\)$",       # (Reporter/Editor) format
        r"^foto:",               # Caption foto
        r"^ilustrasi",           # Ilustrasi  
        r"^baca:",               # Baca: xxx
        r"^\*\*\*",              # Separator
        r"^halaman \d",          # Halaman 1, 2, dst
        r"^share\s",             # Share button text
        r"^loading",             # Loading text
    ]
    
    for pattern in extra_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False


def calculate_aceh_confidence(text: str, article_title: str) -> str:
    """
    Tentukan seberapa yakin text ini berkaitan dengan Aceh.
    
    Returns: "high", "medium", atau "low"
    """
    text_lower = text.lower()
    title_lower = article_title.lower() if isinstance(article_title, str) else ""
    
    # HIGH: text itu sendiri menyebut Aceh/lokasi di Aceh
    for keyword in ACEH_KEYWORDS:
        if keyword in text_lower:
            return "high"
    
    # MEDIUM: judul artikel menyebut Aceh (text-nya bagian dari artikel Aceh)
    for keyword in ACEH_KEYWORDS:
        if keyword in title_lower:
            return "medium"
    
    # LOW: tidak ada mention Aceh sama sekali
    return "low"


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Hitung similarity sederhana antara 2 text berdasarkan overlap kata.
    Returns: float 0.0 - 1.0
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)  # Jaccard similarity


def remove_near_duplicates(df: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    """
    Hapus near-duplicate paragraf (similarity > threshold).
    Ini lebih lambat untuk dataset besar, tapi penting untuk kualitas.
    """
    if len(df) < 2:
        return df
    
    to_remove = set()
    texts = df["text"].tolist()
    
    # Untuk efisiensi, hanya cek pasangan yang panjangnya mirip
    for i in range(len(texts)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(texts)):
            if j in to_remove:
                continue
            
            # Skip jika panjang sangat berbeda (pasti bukan duplikat)
            len_i = len(texts[i])
            len_j = len(texts[j])
            if abs(len_i - len_j) > max(len_i, len_j) * 0.3:
                continue
            
            similarity = calculate_similarity(texts[i], texts[j])
            if similarity > threshold:
                to_remove.add(j)  # Hapus yang kedua
    
    if to_remove:
        df = df.drop(df.index[list(to_remove)]).reset_index(drop=True)
    
    return df


def main():
    # Cek prasyarat
    if not os.path.exists(PARAGRAPHS_RAW_CSV):
        print(f"❌ File tidak ditemukan: {PARAGRAPHS_RAW_CSV}")
        print("   Jalankan 02_extraction.py terlebih dahulu!")
        return
    
    df = pd.read_csv(PARAGRAPHS_RAW_CSV)
    initial_count = len(df)
    
    print("=" * 60)
    print("CLEANING — Membersihkan dan memvalidasi dataset")
    print(f"Total paragraf mentah: {initial_count}")
    print("=" * 60)
    print()
    
    # ===== STEP 1: Clean text =====
    print("🧹 Step 1: Membersihkan text...")
    df["text"] = df["text"].apply(clean_text)
    
    # Hapus baris dengan text kosong setelah cleaning
    df = df[df["text"].str.len() >= MIN_PARAGRAPH_LENGTH].reset_index(drop=True)
    print(f"   Setelah hapus text pendek: {len(df)} paragraf")
    
    # ===== STEP 2: Hapus boilerplate =====
    print("🧹 Step 2: Menghapus boilerplate...")
    mask_not_boilerplate = ~df["text"].apply(is_boilerplate)
    df = df[mask_not_boilerplate].reset_index(drop=True)
    print(f"   Setelah hapus boilerplate: {len(df)} paragraf")
    
    # ===== STEP 3: Hapus exact duplicates =====
    print("🧹 Step 3: Menghapus exact duplicates...")
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["text"], keep="first").reset_index(drop=True)
    print(f"   Dihapus: {before_dedup - len(df)} exact duplicates")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 4: Hapus near-duplicates =====
    print("🧹 Step 4: Menghapus near-duplicates (similarity > 85%)...")
    print("   (ini bisa lambat jika dataset besar, tunggu...)")
    before_near = len(df)
    
    # Batasi near-duplicate check untuk performa
    if len(df) > 2000:
        print(f"   ⚠️ Dataset besar ({len(df)} baris), skip near-duplicate check")
        print("   Gunakan exact duplicate saja")
    else:
        df = remove_near_duplicates(df, threshold=0.85)
    
    print(f"   Dihapus: {before_near - len(df)} near-duplicates")
    print(f"   Tersisa: {len(df)} paragraf")
    
    # ===== STEP 5: Tag Aceh confidence =====
    print("🏷️  Step 5: Menandai relevansi Aceh...")
    df["aceh_confidence"] = df.apply(
        lambda row: calculate_aceh_confidence(
            row["text"], 
            row.get("article_title", "")
        ),
        axis=1
    )
    
    confidence_counts = df["aceh_confidence"].value_counts()
    for level in ["high", "medium", "low"]:
        count = confidence_counts.get(level, 0)
        pct = count / len(df) * 100 if len(df) > 0 else 0
        print(f"   {level}: {count} ({pct:.1f}%)")
    
    # ===== STEP 6: Update word_count =====
    print("📏 Step 6: Menghitung word count...")
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    
    # ===== STEP 7: Re-index =====
    print("🔢 Step 7: Re-indexing...")
    df = df.reset_index(drop=True)
    df["paragraph_id"] = range(1, len(df) + 1)
    
    # ===== STEP 8: Tambahkan kolom untuk labeling nanti =====
    # Kolom kosong yang akan diisi saat manual labeling
    df["topic"] = ""
    df["sentiment"] = ""
    df["labeling_notes"] = ""
    
    # ===== SIMPAN =====
    # Reorder kolom untuk kemudahan
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
        "topic",          # akan diisi saat labeling
        "sentiment",      # akan diisi saat labeling
        "labeling_notes", # catatan tambahan saat labeling
    ]
    
    # Pastikan semua kolom ada
    for col in output_columns:
        if col not in df.columns:
            df[col] = ""
    
    df_output = df[output_columns]
    
    os.makedirs(DATA_DIR, exist_ok=True)
    df_output.to_csv(PARAGRAPHS_CLEAN_CSV, index=False, encoding="utf-8-sig")
    
    # ===== RINGKASAN =====
    print()
    print("=" * 60)
    print("✅ CLEANING SELESAI!")
    print("=" * 60)
    print()
    print(f"📊 Ringkasan:")
    print(f"   Paragraf awal:      {initial_count}")
    print(f"   Paragraf final:     {len(df_output)}")
    print(f"   Dihapus total:      {initial_count - len(df_output)}")
    print(f"   Reduction rate:     {(1 - len(df_output)/initial_count)*100:.1f}%")
    print()
    
    print(f"📊 Statistik text:")
    print(f"   Rata-rata kata/paragraf: {df_output['word_count'].mean():.0f}")
    print(f"   Minimum kata:            {df_output['word_count'].min()}")
    print(f"   Maximum kata:            {df_output['word_count'].max()}")
    print()
    
    print(f"📊 Aceh relevance:")
    for level in ["high", "medium", "low"]:
        count = (df_output["aceh_confidence"] == level).sum()
        pct = count / len(df_output) * 100 if len(df_output) > 0 else 0
        emoji = "🟢" if level == "high" else ("🟡" if level == "medium" else "🔴")
        print(f"   {emoji} {level}: {count} ({pct:.1f}%)")
    print()
    
    if "source_portal" in df_output.columns:
        print(f"📊 Per portal:")
        portal_counts = df_output["source_portal"].value_counts()
        for portal, count in portal_counts.head(10).items():
            print(f"   {portal}: {count} paragraf")
    print()
    
    print(f"📁 DATASET FINAL: {PARAGRAPHS_CLEAN_CSV}")
    print(f"📁 ARTIKEL (ref): {ARTICLES_DB_CSV}")
    print()
    print("📋 Kolom 'topic', 'sentiment', dan 'labeling_notes' sudah disiapkan")
    print("   untuk diisi saat manual labeling nanti.")
    print()
    
    # Cek kualitas
    high_medium_pct = ((df_output["aceh_confidence"] == "high").sum() + 
                       (df_output["aceh_confidence"] == "medium").sum()) / len(df_output) * 100 if len(df_output) > 0 else 0
    
    if high_medium_pct >= 70:
        print("✅ KUALITAS BAIK: ≥70% data punya relevansi Aceh tinggi/medium")
    else:
        print(f"⚠️  PERHATIAN: Hanya {high_medium_pct:.0f}% data punya relevansi Aceh tinggi/medium")
        print("   Pertimbangkan untuk review data dengan confidence 'low'")
        print("   dan hapus yang memang tidak relevan.")
    
    print()
    print("=" * 60)
    print("🎯 Langkah selanjutnya:")
    print("   1. Buka public_text_news_clean.csv")
    print("   2. Review 20-30 baris secara random")
    print("   3. Jika kualitas OK → mulai manual labeling")
    print("   4. Isi kolom 'topic' dan 'sentiment' untuk setiap baris")
    print("=" * 60)


if __name__ == "__main__":
    main()
