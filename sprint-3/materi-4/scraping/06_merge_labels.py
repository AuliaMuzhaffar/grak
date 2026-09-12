"""
06_merge_labels.py — Konsolidasi Label Auto & Manual ke Dataset Final
GRAK 2026 · Sprint 3

CARA KERJA:
  1. Load auto_labeled.csv (data hasil auto-label terkonfirmasi)
  2. Load needs_review.csv (data yang telah diisi/direview secara manual)
  3. Tandai topic_method = "manual" untuk baris yang diisi pada needs_review.csv
  4. Gabungkan keduanya dan urutkan berdasarkan paragraph_id
  5. Validasi kelengkapan label (topic coverage target >= 90%)
  6. Export ke labeled_dataset_final.csv yang siap dipakai untuk training ML di Fase 4

CARA PAKAI:
  python3 06_merge_labels.py
"""

import os
import sys
import pandas as pd

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

AUTO_CSV = os.path.join(PROCESSED_DIR, "auto_labeled.csv")
REVIEW_CSV = os.path.join(PROCESSED_DIR, "needs_review.csv")
FINAL_CSV = os.path.join(PROCESSED_DIR, "labeled_dataset_final.csv")


def main():
    print("=" * 65)
    print("🔄 KONSOLIDASI DATASET — Merge Auto & Manual Labels")
    print("=" * 65)
    print()

    if not os.path.exists(AUTO_CSV) or not os.path.exists(REVIEW_CSV):
        print("❌ File input tidak lengkap:")
        print(f"   auto_labeled.csv : {'ADA' if os.path.exists(AUTO_CSV) else 'TIDAK ADA'}")
        print(f"   needs_review.csv : {'ADA' if os.path.exists(REVIEW_CSV) else 'TIDAK ADA'}")
        print("   Jalankan 05_labeling.py terlebih dahulu!")
        return

    print("📖 Membaca file data...")
    df_auto = pd.read_csv(AUTO_CSV)
    df_review = pd.read_csv(REVIEW_CSV)

    print(f"   Auto-labeled rows : {len(df_auto)}")
    print(f"   Needs review rows : {len(df_review)}")
    print()

    # Tandai method 'manual' untuk baris yang diisi pada needs_review
    mask_filled = (
        df_review["topic"].notna() &
        (df_review["topic"].astype(str).str.strip() != "") &
        (df_review["topic"].astype(str) != "nan")
    )
    df_review.loc[mask_filled, "topic_method"] = "manual"
    if "topic_score" in df_review.columns:
        df_review.loc[mask_filled, "topic_score"] = -1.0

    # Gabungkan dataset
    df_final = pd.concat([df_auto, df_review], ignore_index=True)
    df_final = df_final.sort_values("paragraph_id").reset_index(drop=True)

    # Validasi kelengkapan
    total = len(df_final)
    empty_topic = (df_final["topic"].isna() | (df_final["topic"].astype(str).str.strip() == "") | (df_final["topic"].astype(str) == "nan")).sum()
    filled_topic = total - empty_topic
    coverage = (filled_topic / total) * 100 if total > 0 else 0

    print("📊 HASIL KONSOLIDASI:")
    print(f"   Total paragraf   : {total}")
    print(f"   Topic terisi     : {filled_topic} ({coverage:.1f}%)")
    print(f"   Topic kosong     : {empty_topic} ({empty_topic/total*100:.1f}%)")
    print()

    # Distribusi Metode
    print("🔍 METODE LABELING:")
    method_counts = df_final["topic_method"].value_counts()
    for method, cnt in method_counts.items():
        pct = cnt / total * 100
        print(f"   {method:20s}: {cnt:5d} ({pct:5.1f}%)")
    print()

    # Distribusi Topik Terisi
    print("📈 DISTRIBUSI TOPIK (FINAL):")
    valid_topics = df_final[~df_final["topic"].isna() & (df_final["topic"].astype(str).str.strip() != "") & (df_final["topic"].astype(str) != "nan")]
    topic_counts = valid_topics["topic"].value_counts()
    for topic, cnt in topic_counts.items():
        pct = cnt / total * 100
        bar = "█" * int(pct / 2)
        print(f"   {topic:20s}: {cnt:5d} ({pct:5.1f}%) {bar}")
    print()

    # Simpan ke CSV final
    df_final.to_csv(FINAL_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ Dataset final berhasil disimpan ke:")
    print(f"   {FINAL_CSV}")
    print("=" * 65)


if __name__ == "__main__":
    main()
