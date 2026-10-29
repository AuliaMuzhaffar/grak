"""
10c_process_social_media.py — Harmonisasi & Ingesti Data Social Media (Pilar ke-4)
==================================================================================
Tujuan:
1. Membaca dataset media sosial yang dikurasi oleh rekan tim dari:
   'data/dataset_aceh_sprint3.csv' (311 baris).
2. Harmonisasi Taksonomi Topik ke 8 Kategori Standar Korpus GRAK Sprint 3:
   - Technology -> digitalization
   - Campus_Ecosystem -> ecosystem
   - Funding -> funding
   - Market -> market_access
   - Program -> ecosystem
   - Talent -> talent
   - Infrastructure -> infrastructure
3. Standarisasi Nilai Sentimen ke Lowercase:
   - Positive -> positive
   - Neutral -> neutral
   - Negative -> negative
4. Standarisasi Metadata & Penyelarasan Skema Kolom Terpadu:
   - paragraph_id: SOC_0001 s/d SOC_0311 (sequential zero-padded)
   - data_source: "social_media"
   - source_portal: platform (X/Twitter, YouTube, LinkedIn)
   - article_url: url
   - location: region
   - interviewee: author
   - role: type (POST, TRANSCRIPT)
   - collector: "Rekan Tim"
   - word_count, topic_score (3.0), topic_method ("manual_verified"), sentiment_method ("manual_verified")
   - labeling_notes: jejak provenance (original topic, sentiment, engagement stats)
5. Defensive Data Engineering:
   - Assertions: tepat 311 baris, zero-null pada kolom primer, idempotensi referensial.
6. Menyimpan Output: 'data/processed/social_media_labeled.csv'.

Standar Rekayasa: Data-Centric AI (DCAI), Defensive Data Engineering, Schema Harmonization.
"""

import os
import sys
import pandas as pd
import numpy as np

# Konfigurasi Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "dataset_aceh_sprint3.csv")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "social_media_labeled.csv")

# 1. Mapping Taksonomi Topik (Ontology Harmonization)
TOPIC_MAPPING = {
    "Technology": "digitalization",
    "Campus_Ecosystem": "ecosystem",
    "Funding": "funding",
    "Market": "market_access",
    "Program": "ecosystem",
    "Talent": "talent",
    "Infrastructure": "infrastructure",
}

# 8 Topik Standar Korpus
VALID_TOPICS = {
    "funding",
    "talent",
    "infrastructure",
    "regulation",
    "market_access",
    "ecosystem",
    "digitalization",
    "success_story",
}

VALID_SENTIMENTS = {"positive", "neutral", "negative"}

# Skema Kolom Terpadu
UNIFIED_COLUMNS = [
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


def process_social_media():
    print("=" * 75)
    print("🚀 MEMULAI HARMONISASI & INGESTI DATA SOCIAL MEDIA (10c_process_social_media.py)")
    print("=" * 75)

    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERROR: File input rekan tim tidak ditemukan di: {INPUT_FILE}")
        sys.exit(1)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df_raw = pd.read_csv(INPUT_FILE)
    print(f"📄 Berhasil memuat data mentah rekan tim: {len(df_raw)} baris dari {os.path.basename(INPUT_FILE)}")

    # Validasi kelengkapan kolom input awal
    required_raw_cols = [
        "content_id", "publish_date", "platform", "type", "region",
        "topic", "sentiment", "author", "username", "text",
        "likes", "retweets", "replies", "url", "query_used"
    ]
    missing_cols = [c for c in required_raw_cols if c not in df_raw.columns]
    if missing_cols:
        print(f"❌ ERROR: Kolom input tidak lengkap! Kolom hilang: {missing_cols}")
        sys.exit(1)

    print("\n[1/3] Melakukan Harmonisasi Taksonomi Topik & Standarisasi Sentimen...")
    # Validasi pemetaan topik
    unmapped_topics = set(df_raw["topic"].unique()) - set(TOPIC_MAPPING.keys())
    if unmapped_topics:
        raise ValueError(f"Ditemukan topik yang belum terpetakan dalam kamus harmonisasi: {unmapped_topics}")

    data_dict = {
        "paragraph_id": [f"SOC_{i+1:04d}" for i in range(len(df_raw))],
        "text": df_raw["text"].astype(str).str.strip(),
        "article_title": [
            f"[{plat}] {str(auth)[:60]}" for plat, auth in zip(df_raw["platform"], df_raw["author"])
        ],
        "article_url": df_raw["url"].fillna("").astype(str),
        "source_portal": df_raw["platform"].astype(str),
        "data_source": "social_media",
        "publish_date": df_raw["publish_date"].astype(str),
        "aceh_confidence": "high",
        "word_count": df_raw["text"].astype(str).str.strip().apply(lambda t: len(t.split())),
        "query_used": df_raw["query_used"].fillna("social_media_harvest").astype(str),
        "collector": "Rekan Tim",
        "interviewee": df_raw["author"].fillna("Anonymous").astype(str),
        "role": df_raw["type"].fillna("POST").astype(str),
        "location": df_raw["region"].fillna("Aceh").astype(str),
        "topic": df_raw["topic"].map(TOPIC_MAPPING),
        "topic_score": 3.0,
        "topic_method": "manual_verified",
        "sentiment": df_raw["sentiment"].astype(str).str.strip().str.lower(),
        "sentiment_pos_count": (df_raw["sentiment"].astype(str).str.strip().str.lower() == "positive").astype(int),
        "sentiment_neg_count": (df_raw["sentiment"].astype(str).str.strip().str.lower() == "negative").astype(int),
        "sentiment_method": "manual_verified",
        "labeling_notes": [
            f"OrigTopic={row['topic']} | OrigSent={row['sentiment']} | "
            f"User=@{row['username']} | Likes={row['likes']} | RT={row['retweets']} | Replies={row['replies']}"
            for _, row in df_raw.iterrows()
        ],
    }

    df_processed = pd.DataFrame(data_dict)

    # Susun ulang kolom sesuai skema terpadu
    df_final = df_processed[UNIFIED_COLUMNS].copy()

    print("[2/3] Menjalankan Defensive Quality Assertions...")
    # Assertions
    assert len(df_final) == 311, f"Expected 311 rows, got {len(df_final)}"
    assert df_final["paragraph_id"].is_unique, "Duplicate paragraph_id found!"
    assert df_final["paragraph_id"].str.startswith("SOC_").all(), "paragraph_id must start with 'SOC_'"
    assert df_final["text"].isna().sum() == 0, "Null values detected in 'text' column!"
    assert (df_final["text"].str.len() > 0).all(), "Empty text detected!"
    assert set(df_final["topic"].unique()).issubset(VALID_TOPICS), f"Invalid topics: {set(df_final['topic']) - VALID_TOPICS}"
    assert set(df_final["sentiment"].unique()).issubset(VALID_SENTIMENTS), f"Invalid sentiments: {set(df_final['sentiment']) - VALID_SENTIMENTS}"
    assert (df_final["word_count"] > 0).all(), "Found records with zero word count!"

    print(f"[3/3] Menyimpan hasil harmonisasi ke: {OUTPUT_FILE}")
    df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"✅ File berhasil disimpan: {OUTPUT_FILE} ({len(df_final)} baris, {len(df_final.columns)} kolom)")

    # Logging statistik
    print("\n📊 RINGKASAN DATASET SOCIAL MEDIA HARMONIZED:")
    print(f"- Total baris        : {len(df_final)} postingan")
    print(f"- Platform Breakdown : {df_final['source_portal'].value_counts().to_dict()}")
    print(f"- Distribusi Topik   : {df_final['topic'].value_counts().to_dict()}")
    print(f"- Distribusi Sentimen: {df_final['sentiment'].value_counts().to_dict()}")
    print(f"- Rata-rata Kata     : {df_final['word_count'].mean():.1f} kata/post")

    print("\n📈 KROS-TABULASI TOPIK x SENTIMEN:")
    ct = pd.crosstab(df_final["topic"], df_final["sentiment"], margins=True)
    print(ct.to_string())

    print("\n✨ Harmonisasi data social media selesai 100% tanpa celah!")


if __name__ == "__main__":
    process_social_media()
