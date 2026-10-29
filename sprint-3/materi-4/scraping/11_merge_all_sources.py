"""
11_merge_all_sources.py — Penggabungan Seluruh Sumber Teks (Multi-Source Merge)
================================================================================
Tujuan:
1. Menggabungkan seluruh korpus teks dari berbagai sumber ke dalam satu unified dataset:
   - Data Berita Scraping: 'data/processed/labeled_dataset_final.csv' (13.840 baris) -> data_source="news"
   - Data Survey Open-Ended: 'data/processed/survey_text_extracted.csv' (25 baris) -> data_source="survey"
   - Data Wawancara: 'data/processed/interview_dataset.csv' (113 baris) -> data_source="interview"
   - Data Social Media (Opsional/Non-blocking): 'data/processed/social_media_labeled.csv' -> data_source="social_media"
2. Menjamin Schema Consistency (Keselarasan Skema):
   - Standarisasi nama kolom dan tipe data antar sumber yang heterogen.
   - Mengisi nilai default yang aman untuk missing non-critical columns.
3. Re-indexing:
   - Memberikan ID integer sekuensial (1 s/d N) pada kolom 'id' sebagai primary key terpadu.
   - Mempertahankan 'paragraph_id' asli (NEWS_XXXX / SRV_XXXX / INT_XXXX).
4. Menghasilkan Output: 'data/processed/combined_text.csv' (~13.978 baris).

Standar Rekayasa: Data-Centric AI (DCAI), Defensive Data Engineering, Schema Idempotence.
"""

import os
import sys
import pandas as pd
import numpy as np

# Import Master Dictionary dari labeling_rules (Single Source of Truth)
from labeling_rules import ECOSYSTEM_KEYWORDS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

NEWS_FILE = os.path.join(PROCESSED_DIR, "labeled_dataset_final.csv")
SURVEY_FILE = os.path.join(PROCESSED_DIR, "survey_text_extracted.csv")
INTERVIEW_FILE = os.path.join(PROCESSED_DIR, "interview_dataset.csv")
SOCIAL_MEDIA_FILE = os.path.join(PROCESSED_DIR, "social_media_labeled.csv")

OUTPUT_COMBINED_FILE = os.path.join(PROCESSED_DIR, "combined_text.csv")

# Skema Kolom Terpadu (Unified Schema)
UNIFIED_COLUMNS = [
    "id",
    "paragraph_id",
    "text",
    "article_title",
    "article_url",
    "source_portal",
    "data_source",
    "publish_date",
    "aceh_confidence",
    "word_count",
    "query_used",
    "collector",
    "interviewee",
    "role",
    "location",
    "topic",
    "topic_score",
    "topic_method",
    "sentiment",
    "sentiment_pos_count",
    "sentiment_neg_count",
    "sentiment_method",
    "labeling_notes",
]


def load_source(filepath, source_name, default_portal):
    """Membaca dan menstandardisasi dataframe sumber data secara defensif."""
    if not os.path.exists(filepath):
        print(f"⚠️ Sumber [{source_name}] tidak ditemukan di: {filepath} (Dilewati/Opsional).")
        return None

    df = pd.read_csv(filepath).copy()
    print(f"📄 Memuat [{source_name}]: {len(df)} baris dari {os.path.basename(filepath)}")

    # Pastikan data_source terisi
    # Standardisasi kolom jika ada perbedaan penamaan
    cols_to_update = {
        "data_source": source_name,
        "source_portal": df["source_portal"].fillna(default_portal) if "source_portal" in df.columns else default_portal,
        "article_url": df["article_url"].fillna("") if "article_url" in df.columns else "",
        "article_title": df["article_title"].fillna(f"Untitled {source_name.capitalize()}") if "article_title" in df.columns else f"Untitled {source_name.capitalize()}",
        "aceh_confidence": df["aceh_confidence"].fillna("high") if "aceh_confidence" in df.columns else "high",
        "collector": df["collector"].fillna("Aulia") if "collector" in df.columns else "Aulia",
        "word_count": df["text"].astype(str).apply(lambda x: len(x.split())),
        "topic_score": df["topic_score"].fillna(1.0) if "topic_score" in df.columns else 3.0,
        "topic_method": df["topic_method"].fillna("semi_auto") if "topic_method" in df.columns else "semi_auto",
        "sentiment_pos_count": df["sentiment_pos_count"].fillna(0).astype(int) if "sentiment_pos_count" in df.columns else 0,
        "sentiment_neg_count": df["sentiment_neg_count"].fillna(0).astype(int) if "sentiment_neg_count" in df.columns else 0,
        "sentiment_method": df["sentiment_method"].fillna("semi_auto") if "sentiment_method" in df.columns else "semi_auto",
        "labeling_notes": df["labeling_notes"].fillna("") if "labeling_notes" in df.columns else "",
    }
    df = df.assign(**cols_to_update)

    # Pastikan format paragraph_id konsisten
    if source_name == "news":
        df["paragraph_id"] = df["paragraph_id"].apply(
            lambda x: f"NEWS_{int(x):05d}" if str(x).isdigit() else str(x)
        )

    return df


def merge_all_sources():
    print("=" * 75)
    print("🚀 MEMULAI PENGGABUNGAN MULTI-SOURCE DATASET (11_merge_all_sources.py)")
    print("=" * 75)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    sources_dfs = []

    # 1. Berita Scraping (Wajib)
    df_news = load_source(NEWS_FILE, "news", "news_media")
    if df_news is not None:
        sources_dfs.append(df_news)
    else:
        print("❌ ERROR: File data scraping wajib tidak ditemukan! Jalankan Fase 3 terlebih dahulu.")
        sys.exit(1)

    # 2. Survey Teks Open-Ended (Wajib)
    df_survey = load_source(SURVEY_FILE, "survey", "survey")
    if df_survey is not None:
        sources_dfs.append(df_survey)
    else:
        print("❌ ERROR: File teks survei tidak ditemukan! Jalankan 10_process_survey.py terlebih dahulu.")
        sys.exit(1)

    # 3. Wawancara Mendalam (Wajib)
    df_interview = load_source(INTERVIEW_FILE, "interview", "interview")
    if df_interview is not None:
        sources_dfs.append(df_interview)
    else:
        print("❌ ERROR: File wawancara tidak ditemukan! Jalankan 10b_process_interviews.py terlebih dahulu.")
        sys.exit(1)

    # 4. Social Media (Opsional / Non-blocking)
    df_social = load_source(SOCIAL_MEDIA_FILE, "social_media", "social_media")
    if df_social is not None:
        sources_dfs.append(df_social)
    else:
        print("ℹ️ Info: Data social media saat ini belum tersedia (non-blocking). Penggabungan dilanjutkan.")

    print(f"\n[1/3] Menggabungkan {len(sources_dfs)} sumber data teks...")
    df_combined = pd.concat(sources_dfs, ignore_index=True)

    # =========================================================================
    # INGESTION SHIELD V2 (Adversarial Rejection + Ecosystem Keyword Filter)
    # =========================================================================
    print("🛡️ Menerapkan Ingestion Shield V2 (Ecosystem Keyword Filter)...")
    before_shield = len(df_combined)
    
    # Import Master Dictionary dipindahkan ke atas (Global)
    
    # Fungsi filter untuk mengecek keyword pada Medium confidence
    def is_valid_medium(text):
        if not isinstance(text, str):
            return False
        text_lower = text.lower()
        return any(kw in text_lower for kw in ECOSYSTEM_KEYWORDS)

    # 1. Buang semua 'low'
    # 2. Untuk 'medium', wajib lolos is_valid_medium
    # 3. 'high' selalu lolos
    # 4. Buang yang sudah dilabel 'out_of_domain' oleh 05_labeling.py (Propagated noise)
    mask_low = df_combined["aceh_confidence"] == "low"
    mask_high = df_combined["aceh_confidence"] == "high"
    mask_medium_valid = (df_combined["aceh_confidence"] == "medium") & (df_combined["text"].apply(is_valid_medium))
    mask_not_ood = df_combined["topic"] != "out_of_domain"
    
    # Kombinasi valid: (High ATAU Medium-Valid) DAN Bukan OOD
    mask_valid = (mask_high | mask_medium_valid) & mask_not_ood
    
    # Hitung rincian yang akan dibuang
    low_dropped = mask_low.sum()
    medium_dropped = (df_combined["aceh_confidence"] == "medium").sum() - mask_medium_valid.sum()
    propagated_dropped = (~mask_not_ood & (mask_high | mask_medium_valid)).sum()
    
    # -------------------------------------------------------------------------
    # EKSPOR DATA YANG DITOLAK (Untuk Audit & Tracking Mentor)
    # -------------------------------------------------------------------------
    df_rejected = df_combined[~mask_valid].copy()
    df_rejected['rejection_reason'] = "Unknown"
    
    # Berikan alasan berdasarkan hukum Ingestion Shield V2
    df_rejected.loc[mask_low, 'rejection_reason'] = "Low Confidence (Otomatis dibuang karena skor relevansi wilayah Aceh sangat rendah)"
    
    mask_medium_dropped = (df_combined["aceh_confidence"] == "medium") & (~df_combined["text"].apply(is_valid_medium))
    df_rejected.loc[mask_medium_dropped, 'rejection_reason'] = "Medium Confidence (Gagal menemukan satupun Keyword Ekosistem yang diwajibkan)"
    
    mask_propagated = (~mask_not_ood & (mask_high | mask_medium_valid))
    df_rejected.loc[mask_propagated, 'rejection_reason'] = "Propagated Noise (Teks ini mungkin membicarakan startup, tapi mayoritas (>50%) artikel aslinya terdeteksi sebagai out of domain/sampah)"
    
    REJECTED_FILE = os.path.join(PROCESSED_DIR, "rejected_dataset.csv")
    df_rejected.to_csv(REJECTED_FILE, index=False, encoding="utf-8")
    # -------------------------------------------------------------------------
    
    # BARU di-overwrite dengan data yang lolos (Valid)
    df_combined = df_combined[mask_valid].copy()
    
    after_shield = len(df_combined)
    rejected_count = before_shield - after_shield
    
    print(f"   Ditolak (True Negative) : {rejected_count} paragraf.")
    print(f"     - Low confidence      : {low_dropped} dibuang")
    print(f"     - Medium (No Keyword) : {medium_dropped} dibuang")
    print(f"     - Propagated Noise    : {propagated_dropped} dibuang")
    print(f"   Lolos (True Positive)   : {after_shield} paragraf (Siap Model).")
    print(f"   Rekam jejak {rejected_count} data yang ditolak disimpan ke: {REJECTED_FILE}")
    # =========================================================================

    print(f"[2/3] Menerapkan standarisasi skema dan re-indexing...")
    # Pastikan seluruh kolom dalam UNIFIED_COLUMNS ada
    for col in UNIFIED_COLUMNS:
        if col not in df_combined.columns and col != "id":
            df_combined[col] = ""

    # Re-index id sekuensial (1, 2, ..., N)
    df_combined["id"] = range(1, len(df_combined) + 1)

    # Pilih dan urutkan sesuai skema terpadu
    df_final = df_combined[UNIFIED_COLUMNS].copy()

    # Bersihkan NaN pada kolom teks penting
    df_final = df_final.assign(
        text=df_final["text"].fillna("").astype(str).str.strip(),
        topic=df_final["topic"].fillna("ecosystem").astype(str),
        sentiment=df_final["sentiment"].fillna("neutral").astype(str),
    )

    # Simpan ke CSV
    df_final.to_csv(OUTPUT_COMBINED_FILE, index=False, encoding="utf-8")
    print(f"✅ File terpadu berhasil disimpan: {OUTPUT_COMBINED_FILE}")

    # -------------------------------------------------------------
    # QUALITY ASSERTIONS & STATISTIK
    # -------------------------------------------------------------
    print("\n[3/3] Menjalankan Quality Assertion...")
    assert df_final.shape[0] >= 7000, f"Jumlah data kurang dari baseline setelah Ingestion Shield V2! ({df_final.shape[0]})"
    assert df_final["id"].is_unique, "Kolom 'id' tidak unik!"
    assert df_final["paragraph_id"].is_unique, "Kolom 'paragraph_id' terdeteksi memiliki duplikasi!"
    assert df_final["text"].isna().sum() == 0, "Ada nilai null di kolom text!"
    assert df_final["topic"].isna().sum() == 0, "Ada nilai null di kolom topic!"
    assert df_final["sentiment"].isna().sum() == 0, "Ada nilai null di kolom sentiment!"

    print("\n📊 RINGKASAN DATASET TERPADU (COMBINED_TEXT):")
    print(f"- Total baris teks : {len(df_final):,} baris")
    print(f"- Sebaran Sumber   : {df_final['data_source'].value_counts().to_dict()}")
    print(f"- Sebaran Topik    : {df_final['topic'].value_counts().to_dict()}")
    print(f"- Sebaran Sentimen : {df_final['sentiment'].value_counts().to_dict()}")

    print("\n📈 PERBANDINGAN SENTIMEN ANTAR SUMBER:")
    cross_tab = pd.crosstab(df_final["data_source"], df_final["sentiment"], normalize="index") * 100
    print(cross_tab.round(1).to_string())

    print("\n✨ Penggabungan seluruh sumber teks sukses 100%!")


if __name__ == "__main__":
    merge_all_sources()
