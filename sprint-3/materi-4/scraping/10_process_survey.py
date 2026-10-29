"""
10_process_survey.py — Pemrosesan Data Survey Google Forms (Sprint 3 GRAK 2026)
==============================================================================
Tujuan:
1. Membaca data mentah Survey Google Forms (N=12 responden, 28 kolom).
2. Menghasilkan Output A: 'data/processed/survey_structured.csv'
   - Mengganti nama kolom panjang menjadi nama pendek yang terstandardisasi.
   - Mengonversi skala Likert teks ("1 - Sangat Tidak Setuju" s/d "5 - Sangat Setuju") menjadi integer 1-5.
   - Memecah kolom tantangan multi-select (Q12) menjadi 'tantangan_1', 'tantangan_2', 'tantangan_3'.
   - Sanitasi PII (Personally Identifiable Information): Nomor HP, Email, dan persetujuan kontak di-drop.
3. Menghasilkan Output B: 'data/processed/survey_text_extracted.csv'
   - Mengekstrak teks open-ended (Q21, Q22, Q23).
   - Memfilter respon kosong/non-informatif.
   - Memberikan ID berformat 'SRV_XXXX'.
   - Melakukan pelabelan topic (8 kategori taksonomi) dan sentiment secara manual terverifikasi.
   - Skema kolom dirancang 100% kompatibel dengan 'labeled_dataset_final.csv'.

Standar Rekayasa: Data-Centric AI (DCAI), Defensive Data Engineering, Data Privacy by Design.
"""

import os
import sys
import pandas as pd
import numpy as np

# Menentukan path direktori secara relatif dan kokoh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

SURVEY_INPUT_FILE = os.path.join(
    DATA_DIR, "Survey GRAK 2026 - Sprint 3 (Responses) - Form Responses 1.csv"
)
OUTPUT_STRUCTURED_FILE = os.path.join(PROCESSED_DIR, "survey_structured.csv")
OUTPUT_TEXT_FILE = os.path.join(PROCESSED_DIR, "survey_text_extracted.csv")

# 1. Definisi Mapping Likert Scale (Teks -> Integer 1-5)
LIKERT_MAP = {
    "1 - Sangat Tidak Setuju": 1,
    "2 - Tidak Setuju": 2,
    "3 - Netral": 3,
    "4 - Setuju": 4,
    "5 - Sangat Setuju": 5,
}

# 2. Definisi Mapping Manual Ground-Truth untuk Open-Ended Responses (Q21, Q22, Q23)
# Taksonomi Topik: funding, talent, regulation, infrastructure, market_access, ecosystem, digitalization, success_story
# Taksonomi Sentimen: positive, negative, neutral
MANUAL_OPEN_ENDED_LABELS = {
    # Q21: Hal yang ingin diubah dari ekosistem startup/bisnis digital Aceh dan alasannya
    ("Q21", 1): {
        "topic": "ecosystem",
        "sentiment": "positive",
        "notes": "Dorongan inovasi berkelanjutan dan sinergi dengan Bank Indonesia",
    },
    ("Q21", 2): {
        "topic": "ecosystem",
        "sentiment": "negative",
        "notes": "Keluhan ekosistem: banyak ide layu sebelum berkembang",
    },
    ("Q21", 3): {
        "topic": "regulation",
        "sentiment": "negative",
        "notes": "Kekecewaan terhadap minimnya perhatian pemerintah daerah",
    },
    ("Q21", 4): {
        "topic": "regulation",
        "sentiment": "neutral",
        "notes": "Harapan regulasi pemerintah mempermudah pertumbuhan startup",
    },
    ("Q21", 7): {
        "topic": "ecosystem",
        "sentiment": "negative",
        "notes": "Keluhan mentalitas daerah/kultur lokal yang kurang kolaboratif",
    },
    ("Q21", 8): {
        "topic": "ecosystem",
        "sentiment": "neutral",
        "notes": "Pandangan fokus mencari solusi dibanding mengeluh",
    },
    ("Q21", 9): {
        "topic": "ecosystem",
        "sentiment": "positive",
        "notes": "Membangun kultur launch, validate, iterate menuju product-market fit",
    },
    ("Q21", 10): {
        "topic": "market_access",
        "sentiment": "negative",
        "notes": "Tantangan penetrasi pasar dan rendahnya literasi digital publik",
    },
    ("Q21", 11): {
        "topic": "regulation",
        "sentiment": "negative",
        "notes": "Ketidakjelasan dan ambiguitas regulasi",
    },
    ("Q21", 12): {
        "topic": "talent",
        "sentiment": "neutral",
        "notes": "Peningkatan kesiapan kerja dan etos kerja SDM",
    },
    # Q22: Kebutuhan utama yang belum terpenuhi bagi pelaku startup di Aceh
    ("Q22", 1): {
        "topic": "regulation",
        "sentiment": "negative",
        "notes": "Kebutuhan dukungan pemerintah belum terpenuhi",
    },
    ("Q22", 2): {
        "topic": "market_access",
        "sentiment": "negative",
        "notes": "Kebutuhan akses pasar belum terpenuhi",
    },
    ("Q22", 4): {
        "topic": "ecosystem",
        "sentiment": "negative",
        "notes": "Ketiadaan ekosistem yang terhubung dari ide hingga scaling",
    },
    ("Q22", 6): {
        "topic": "ecosystem",
        "sentiment": "negative",
        "notes": "Kebutuhan mentoring marketing efektif dengan budget minim",
    },
    ("Q22", 7): {
        "topic": "funding",
        "sentiment": "negative",
        "notes": "Kebutuhan pendanaan belum terpenuhi",
    },
    ("Q22", 8): {
        "topic": "funding",
        "sentiment": "negative",
        "notes": "Kebutuhan connecting the dots, infrastruktur, dan pendanaan non-pemerintah",
    },
    ("Q22", 9): {
        "topic": "funding",
        "sentiment": "neutral",
        "notes": "Kebutuhan expert mentor, market luar Aceh (Jawa), dan hibah/grant",
    },
    ("Q22", 10): {
        "topic": "funding",
        "sentiment": "negative",
        "notes": "Kebutuhan akses pendanaan modal kerja",
    },
    ("Q22", 11): {
        "topic": "talent",
        "sentiment": "negative",
        "notes": "Kurangnya inkubator dan sulitnya mencari talent/SDM",
    },
    ("Q22", 12): {
        "topic": "funding",
        "sentiment": "negative",
        "notes": "Kebutuhan kepastian skema pendanaan",
    },
    # Q23: Pengalaman positif atau negatif yang paling berkesan
    ("Q23", 1): {
        "topic": "funding",
        "sentiment": "positive",
        "notes": "Pengalaman positif mendapat dukungan Bank Indonesia Aceh",
    },
    ("Q23", 5): {
        "topic": "infrastructure",
        "sentiment": "positive",
        "notes": "Efisiensi operasional terbantu adopsi teknologi AI",
    },
    ("Q23", 9): {
        "topic": "ecosystem",
        "sentiment": "negative",
        "notes": "Kritik seremonial pejabat vs apresiasi pasar lokal yang enggan berbayar",
    },
    ("Q23", 10): {
        "topic": "market_access",
        "sentiment": "positive",
        "notes": "Peluang pasar terbuka lebar karena minimnya kompetitor lokal",
    },
    ("Q23", 12): {
        "topic": "market_access",
        "sentiment": "negative",
        "notes": "Hambatan adopsi teknologi masyarakat dan kegagalan validasi minat produk",
    },
}


def process_survey():
    print("=" * 70)
    print("🚀 MEMULAI PEMROSESAN SURVEY GOOGLE FORMS (10_process_survey.py)")
    print("=" * 70)

    if not os.path.exists(SURVEY_INPUT_FILE):
        print(f"❌ ERROR: File input survey tidak ditemukan di: {SURVEY_INPUT_FILE}")
        sys.exit(1)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df_raw = pd.read_csv(SURVEY_INPUT_FILE)
    n_rows, n_cols = df_raw.shape
    print(f"📄 Berhasil membaca survey mentah: {n_rows} responden × {n_cols} kolom.")

    # -------------------------------------------------------------
    # BAGIAN A: PROSES DATA TERSTRUKTUR (survey_structured.csv)
    # -------------------------------------------------------------
    print("\n[1/3] Memproses data terstruktur & konversi Likert...")

    structured_rows = []

    for idx, row in df_raw.iterrows():
        resp_id = idx + 1

        # Pecah Q12 (Tantangan multi-select)
        q12_raw = str(row.iloc[14]) if pd.notna(row.iloc[14]) else ""
        tantangan_list = [t.strip() for t in q12_raw.split(",") if t.strip()]
        tantangan_1 = tantangan_list[0] if len(tantangan_list) > 0 else None
        tantangan_2 = tantangan_list[1] if len(tantangan_list) > 1 else None
        tantangan_3 = tantangan_list[2] if len(tantangan_list) > 2 else None

        # Konversi Likert Q15 - Q20
        def parse_likert(val):
            if pd.isna(val):
                return None
            s_val = str(val).strip()
            if s_val in LIKERT_MAP:
                return LIKERT_MAP[s_val]
            # Jika sudah integer string
            try:
                i = int(s_val[0])
                if 1 <= i <= 5:
                    return i
            except Exception:
                pass
            return None

        p_ekosistem = parse_likert(row.iloc[17])
        p_pendanaan = parse_likert(row.iloc[18])
        p_mentor = parse_likert(row.iloc[19])
        p_pemerintah = parse_likert(row.iloc[20])
        p_optimis = parse_likert(row.iloc[21])
        p_infra = parse_likert(row.iloc[22])

        # Skala 1-5 Q11, Q13, Q14
        def parse_int_scale(val):
            try:
                return int(val)
            except Exception:
                return None

        kemungkinan_bertahan = parse_int_scale(row.iloc[13])
        kemudahan_talent = parse_int_scale(row.iloc[15])
        kemudahan_pasar = parse_int_scale(row.iloc[16])

        # PII Sanitasi: Kolom 26 (Opt-in) dan Kolom 27 (WhatsApp/Email) DI-DROP
        record = {
            "respondent_id": resp_id,
            "timestamp": row.iloc[0],
            "wilayah": row.iloc[1],
            "wilayah_lainnya": row.iloc[2] if pd.notna(row.iloc[2]) else None,
            "peran": row.iloc[3],
            "lama_terlibat": row.iloc[4],
            "sektor": row.iloc[5],
            "status_bisnis": row.iloc[6],
            "pernah_inkubasi": row.iloc[7],
            "sumber_program": row.iloc[8] if pd.notna(row.iloc[8]) else None,
            "jenis_dukungan": row.iloc[9] if pd.notna(row.iloc[9]) else None,
            "followup_program": row.iloc[10] if pd.notna(row.iloc[10]) else None,
            "pernah_event": row.iloc[11],
            "pernah_pendanaan": row.iloc[12],
            "kemungkinan_bertahan": kemungkinan_bertahan,
            "tantangan_1": tantangan_1,
            "tantangan_2": tantangan_2,
            "tantangan_3": tantangan_3,
            "kemudahan_talent": kemudahan_talent,
            "kemudahan_pasar": kemudahan_pasar,
            "persepsi_ekosistem": p_ekosistem,
            "persepsi_pendanaan": p_pendanaan,
            "persepsi_mentor": p_mentor,
            "persepsi_pemerintah": p_pemerintah,
            "persepsi_optimis": p_optimis,
            "persepsi_infra": p_infra,
        }
        structured_rows.append(record)

    df_structured = pd.DataFrame(structured_rows)
    df_structured.to_csv(OUTPUT_STRUCTURED_FILE, index=False, encoding="utf-8")
    print(f"✅ Output A tersimpan: {OUTPUT_STRUCTURED_FILE} ({df_structured.shape[0]} baris, {df_structured.shape[1]} kolom)")

    # -------------------------------------------------------------
    # BAGIAN B: EKSTRAKSI TEKS OPEN-ENDED (Q21, Q22, Q23)
    # -------------------------------------------------------------
    print("\n[2/3] Mengekstrak teks respon open-ended & menerapkan label terverifikasi...")

    text_rows = []
    text_counter = 1

    question_configs = [
        ("Q21", 23, "Survey Q21 (Visi Perubahan Ekosistem)"),
        ("Q22", 24, "Survey Q22 (Kebutuhan Belum Terpenuhi)"),
        ("Q23", 25, "Survey Q23 (Pengalaman Paling Berkesan)"),
    ]

    for q_code, col_idx, q_title_prefix in question_configs:
        for idx, row in df_raw.iterrows():
            resp_id = idx + 1
            raw_text = row.iloc[col_idx]

            if pd.isna(raw_text):
                continue

            text_cleaned = str(raw_text).strip()
            # Filter respon tidak bermakna / non-informatif
            if text_cleaned.lower() in ["belum tahu", "belum kepikiran", "sesuai kebutuhan masing-masing", "nan", "-"]:
                continue

            # Periksa apakah ada di ground-truth mapping
            mapping_key = (q_code, resp_id)
            if mapping_key not in MANUAL_OPEN_ENDED_LABELS:
                continue

            meta = MANUAL_OPEN_ENDED_LABELS[mapping_key]
            word_count = len(text_cleaned.split())

            paragraph_id = f"SRV_{text_counter:04d}"
            text_counter += 1

            record_text = {
                "paragraph_id": paragraph_id,
                "text": text_cleaned,
                "article_title": f"{q_title_prefix} - Responden {resp_id}",
                "article_url": "",
                "source_portal": "survey",
                "data_source": "survey",
                "publish_date": str(row.iloc[0]),
                "aceh_confidence": "high",
                "word_count": word_count,
                "query_used": "survey_primary",
                "collector": "Aulia",
                "topic": meta["topic"],
                "topic_score": 3.0,
                "topic_method": "manual",
                "sentiment": meta["sentiment"],
                "sentiment_pos_count": 1 if meta["sentiment"] == "positive" else 0,
                "sentiment_neg_count": 1 if meta["sentiment"] == "negative" else 0,
                "sentiment_method": "manual",
                "labeling_notes": meta["notes"],
            }
            text_rows.append(record_text)

    df_text = pd.DataFrame(text_rows)
    df_text.to_csv(OUTPUT_TEXT_FILE, index=False, encoding="utf-8")
    print(f"✅ Output B tersimpan: {OUTPUT_TEXT_FILE} ({df_text.shape[0]} baris teks, {df_text.shape[1]} kolom)")

    # -------------------------------------------------------------
    # BAGIAN C: QUALITY ASSERTIONS & RINGKASAN
    # -------------------------------------------------------------
    print("\n[3/3] Melakukan Quality Assertion...")
    assert df_structured.shape[0] == 12, f"Expected 12 structured rows, got {df_structured.shape[0]}"
    assert "Nomor WhatsApp atau Email yang dapat dihubungi" not in df_structured.columns, "PII leak detected!"
    assert df_structured["persepsi_ekosistem"].isna().sum() == 0, "Null found in Likert ekosistem!"
    assert df_text.shape[0] == 25, f"Expected 25 valid text rows, got {df_text.shape[0]}"
    assert df_text["topic"].isna().sum() == 0, "Missing topic labels in text extraction!"

    print("\n📊 RINGKASAN DATASET SURVEY TERSTRUKTUR:")
    print(f"- Total responden : {df_structured.shape[0]}")
    print(f"- Sebaran Wilayah  : {df_structured['wilayah'].value_counts().to_dict()}")
    print(f"- Rata-rata Likert:")
    likert_cols = [c for c in df_structured.columns if c.startswith("persepsi_")]
    for col in likert_cols:
        print(f"  * {col:20s}: mean={df_structured[col].mean():.2f}, median={df_structured[col].median():.1f}")

    print("\n📊 RINGKASAN EKSTRAKSI TEKS OPEN-ENDED:")
    print(f"- Total baris teks : {df_text.shape[0]}")
    print(f"- Distribusi Topik : {df_text['topic'].value_counts().to_dict()}")
    print(f"- Distribusi Sentimen: {df_text['sentiment'].value_counts().to_dict()}")
    print("\n✨ Pemrosesan survey selesai dengan sukses 100%!")


if __name__ == "__main__":
    process_survey()
