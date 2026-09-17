"""
05_labeling.py — Semi-Automated Labeling Pipeline (2-Pass Cascading)
GRAK 2026 · Sprint 3

CARA KERJA:
  1. Load dataset bersih dari Fase 2 (public_text_news_clean.csv)
  2. PASS 1: Direct Paragraph Auto-labeling menggunakan keyword scoring multi-tier
     (dengan word boundary regex \\b untuk kata pendek <= 3 huruf).
  3. PASS 2: Title & Article-Level Propagation untuk melengkapi paragraf
     yang masih 'needs_review' berdasarkan konsensus artikel dan judul.
  4. Pisahkan: auto-labeled (confident) vs needs_review (uncertain)
  5. Export keduanya untuk human review dan reporting

CARA PAKAI:
  python3 05_labeling.py

INPUT:
  → data/processed/public_text_news_clean.csv (dari 04_cleaning.py)

OUTPUT:
  → data/processed/labeled_dataset.csv   (SEMUA data — auto-labeled + needs_review)
  → data/processed/needs_review.csv      (Data yang PERLU human review)
  → data/processed/auto_labeled.csv      (Data yang SUDAH auto-labeled — untuk spot check)
  → data/processed/label_stats.json      (Statistik distribusi label)

WORKFLOW:
  1. Jalankan script ini: python3 05_labeling.py
  2. Buka needs_review.csv di Google Sheets / Excel
  3. Isi kolom 'topic' dan 'sentiment' secara manual jika perlu
  4. Jika menemukan pattern baru → update labeling_rules.py
  5. Jalankan script ini lagi (safe, idempotent, label manual tidak ditimpa)
"""

import os
import sys
import json
import re
import warnings
import pandas as pd
from datetime import datetime

# Filter chained assignment and future warnings from pandas
warnings.filterwarnings("ignore", category=FutureWarning)

# Import shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.logger import get_logger
from labeling_rules import (
    TOPIC_RULES, SENTIMENT_RULES,
    TOPIC_MIN_SCORE, SENTIMENT_MIN_MATCHES,
)

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

INPUT_CSV = os.path.join(PROCESSED_DIR, "public_text_news_clean.csv")
OUTPUT_LABELED = os.path.join(PROCESSED_DIR, "labeled_dataset.csv")
OUTPUT_NEEDS_REVIEW = os.path.join(PROCESSED_DIR, "needs_review.csv")
OUTPUT_AUTO_LABELED = os.path.join(PROCESSED_DIR, "auto_labeled.csv")
LABEL_STATS = os.path.join(PROCESSED_DIR, "label_stats.json")

log = get_logger("05_labeling")

# Cache precompiled regex patterns for keywords (universal word boundary \b)
KW_PATTERN_CACHE = {}

def matches_keyword(kw: str, text_lower: str) -> bool:
    """
    Cek kecocokan kata kunci dalam teks.
    Semua kata kunci (baik kata tunggal maupun frasa majemuk) wajib menggunakan
    batas kata (\b) agar tidak mencocokkan substring di dalam kata lain:
    - 'uang' TIDAK cocok di 'peluang'
    - 'dana' TIDAK cocok di 'perdana'
    - 'it' TIDAK cocok di 'terkait' / 'aktivitas'
    - 'usk' TIDAK cocok di 'termasuk' / 'fokuskan'
    """
    kw_lower = kw.lower().strip()
    if not kw_lower:
        return False
    if kw_lower not in KW_PATTERN_CACHE:
        KW_PATTERN_CACHE[kw_lower] = re.compile(r'\b' + re.escape(kw_lower) + r'\b', flags=re.IGNORECASE)
    return bool(KW_PATTERN_CACHE[kw_lower].search(text_lower))


# ============================================================
# LABELING FUNCTIONS
# ============================================================

def score_topic(text: str) -> tuple[str, float, dict, str]:
    """
    Scoring topic berdasarkan keyword rules.
    
    Args:
        text: Text paragraf atau judul yang akan di-label
    
    Returns:
        Tuple of:
        - topic: nama topic dengan score tertinggi (atau "unclassified")
        - score: score tertinggi
        - all_scores: dict semua topic dan scorenya
        - tie_notes: catatan string jika terjadi skor imbang
    
    Scoring:
        strong keyword match = 3 poin
        medium keyword match = 2 poin
        weak keyword match   = 1 poin
        
    Topic dengan score tertinggi dipilih jika score >= TOPIC_MIN_SCORE.
    Jika ada skor seri (tie) di posisi teratas -> "unclassified" (Opsi B: Active Learning).
    Jika score < TOPIC_MIN_SCORE -> "unclassified".
    """
    text_lower = text.lower()
    all_scores = {}
    
    for topic_name, keywords in TOPIC_RULES.items():
        score = 0
        
        # Count strong matches (3 poin each)
        for kw in keywords["strong"]:
            if matches_keyword(kw, text_lower):
                score += 3
        
        # Count medium matches (2 poin each)
        for kw in keywords["medium"]:
            if matches_keyword(kw, text_lower):
                score += 2
        
        # Count weak matches (1 poin each)
        for kw in keywords["weak"]:
            if matches_keyword(kw, text_lower):
                score += 1
        
        all_scores[topic_name] = score
    
    if not all_scores:
        return "unclassified", 0.0, all_scores, ""
    
    max_score = max(all_scores.values())
    
    # Check minimum threshold
    if max_score < TOPIC_MIN_SCORE:
        return "unclassified", float(max_score), all_scores, ""
    
    # Check for ties among top topics (Opsi B: Active Learning)
    top_topics = [t for t, s in all_scores.items() if s == max_score]
    if len(top_topics) > 1:
        # Terjadi persaingan seimbang -> ambigu -> simpan info tie untuk annotator
        tie_notes = "TIE: " + " vs ".join(f"{t}({max_score})" for t in top_topics)
        return "unclassified", float(max_score), all_scores, tie_notes
    
    best_topic = top_topics[0]
    return best_topic, float(max_score), all_scores, ""


def score_sentiment(text: str) -> tuple[str, int, int]:
    """
    Scoring sentiment berdasarkan keyword rules.
    
    Args:
        text: Text paragraf
    
    Returns:
        Tuple of:
        - sentiment: "positive", "negative", atau "neutral"
        - positive_count: jumlah positive keyword match
        - negative_count: jumlah negative keyword match
    """
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in SENTIMENT_RULES["positive"] if matches_keyword(kw, text_lower))
    negative_count = sum(1 for kw in SENTIMENT_RULES["negative"] if matches_keyword(kw, text_lower))
    
    # Determine sentiment
    if positive_count > negative_count and positive_count >= SENTIMENT_MIN_MATCHES:
        return "positive", positive_count, negative_count
    elif negative_count > positive_count and negative_count >= SENTIMENT_MIN_MATCHES:
        return "negative", positive_count, negative_count
    else:
        return "neutral", positive_count, negative_count


def label_single_row(row: pd.Series) -> pd.Series:
    """
    Label satu baris data untuk PASS 1 (Direct Text Matching).
    
    Menambahkan kolom:
    - topic: hasil auto-label topic
    - topic_score: score confidence
    - topic_method: "auto" atau "needs_review"
    - sentiment: hasil auto-label sentiment
    - sentiment_pos_count: jumlah positive matches
    - sentiment_neg_count: jumlah negative matches
    - sentiment_method: "auto" atau "needs_review"
    - labeling_notes: catatan tie-break jika terjadi skor imbang
    """
    text = str(row.get("text", ""))
    
    # === Topic ===
    topic, topic_score, _, tie_notes = score_topic(text)
    
    if topic == "unclassified":
        topic_method = "needs_review"
        notes = tie_notes
    else:
        topic_method = "auto"
        notes = ""
    
    # === Sentiment ===
    sentiment, pos_count, neg_count = score_sentiment(text)
    sentiment_method = "auto"
    
    # === Update row ===
    result = row.copy()
    result["topic"] = topic if topic != "unclassified" else ""
    result["topic_score"] = topic_score
    result["topic_method"] = topic_method
    result["sentiment"] = sentiment
    result["sentiment_pos_count"] = pos_count
    result["sentiment_neg_count"] = neg_count
    result["sentiment_method"] = sentiment_method
    result["labeling_notes"] = notes
    
    return result


# ============================================================
# MAIN
# ============================================================

def main():
    # ===== Load data =====
    if not os.path.exists(INPUT_CSV):
        print(f"❌ File tidak ditemukan: {INPUT_CSV}")
        print("   Jalankan 04_cleaning.py terlebih dahulu!")
        return
    
    df = pd.read_csv(INPUT_CSV)
    total = len(df)
    
    print("=" * 65)
    print("🏷️  LABELING — Semi-Automated Labeling Pipeline (2-Pass)")
    print(f"   Total paragraf : {total}")
    print(f"   Topics         : {list(TOPIC_RULES.keys())}")
    print(f"   Sentiments     : positive, negative, neutral")
    print("=" * 65)
    print()
    
    log.info("Starting labeling pipeline (2-pass)", total=total)
    
    # ===== STEP 1: Check for existing manual labels =====
    # Jika user sudah manual-label beberapa baris di needs_review.csv / CSV sebelumnya,
    # JANGAN overwrite label manual mereka.
    
    manual_cache = {}
    
    # 1. Cek dari needs_review.csv yang sudah diisi user
    if os.path.exists(OUTPUT_NEEDS_REVIEW):
        try:
            prev_rev = pd.read_csv(OUTPUT_NEEDS_REVIEW)
            if "paragraph_id" in prev_rev.columns and "topic" in prev_rev.columns:
                filled_rev = prev_rev[
                    (prev_rev["topic"].notna()) &
                    (prev_rev["topic"].astype(str).str.strip() != "") &
                    (prev_rev["topic"].astype(str) != "nan")
                ]
                for _, r in filled_rev.iterrows():
                    manual_cache[r["paragraph_id"]] = {
                        "topic": str(r["topic"]).strip(),
                        "sentiment": str(r.get("sentiment", "")).strip() if pd.notna(r.get("sentiment")) else "",
                    }
        except Exception as e:
            log.warning("Gagal membaca existing needs_review.csv", error=str(e))
            if os.path.getsize(OUTPUT_NEEDS_REVIEW) > 1024:
                print(f"❌ PERINGATAN KRITIS: Gagal membaca {OUTPUT_NEEDS_REVIEW} ({e}).")
                print("   File memiliki data manual namun gagal dibaca. Abort untuk mencegah kehilangan data!")
                return
            
    # 2. Cek dari input df itu sendiri
    if "topic" in df.columns:
        filled_df = df[
            (df["topic"].notna()) &
            (df["topic"].astype(str).str.strip() != "") &
            (df["topic"].astype(str) != "nan")
        ]
        for _, r in filled_df.iterrows():
            if r["paragraph_id"] not in manual_cache:
                manual_cache[r["paragraph_id"]] = {
                    "topic": str(r["topic"]).strip(),
                    "sentiment": str(r.get("sentiment", "")).strip() if pd.notna(r.get("sentiment")) else "",
                }
    
    if manual_cache:
        print(f"📋 Ditemukan label manual existing:")
        print(f"   Jumlah label manual diamankan: {len(manual_cache)} baris")
        print(f"   → Label manual ini TIDAK akan di-overwrite oleh auto-label")
        print()
    
    # ===== STEP 2: PASS 1 - Direct Paragraph Auto-labeling =====
    print("🤖 PASS 1: Direct Paragraph Matching sedang berjalan...")
    
    results = []
    for idx, row in df.iterrows():
        p_id = row.get("paragraph_id")
        
        labeled_row = label_single_row(row)
        
        # Preserve manual labels jika ada di cache
        if p_id in manual_cache:
            m_data = manual_cache[p_id]
            labeled_row["topic"] = m_data["topic"]
            labeled_row["topic_method"] = "manual"
            labeled_row["topic_score"] = -1.0  # -1 = manual
            if m_data.get("sentiment") and m_data["sentiment"] != "nan":
                labeled_row["sentiment"] = m_data["sentiment"]
                labeled_row["sentiment_method"] = "manual"
        
        results.append(labeled_row)
    
    df_labeled = pd.DataFrame(results)
    
    pass1_auto_count = (df_labeled["topic_method"] == "auto").sum()
    pass1_review_count = (df_labeled["topic_method"] == "needs_review").sum()
    print(f"   ├── Pass 1 Auto-labeled : {pass1_auto_count} ({pass1_auto_count/total*100:.1f}%)")
    print(f"   └── Pass 1 Needs Review : {pass1_review_count} ({pass1_review_count/total*100:.1f}%)")
    print()
    
    # ===== STEP 3: PASS 2 - Title-Context & Article-Level Propagation =====
    print("🔄 PASS 2: Title-Context & Article-Level Propagation sedang berjalan...")
    
    # 1. Precompute Article Majority dari baris berlabel confident di Pass 1
    article_majority = {}
    for title, group in df_labeled.groupby("article_title"):
        auto_group = group[group["topic_method"] == "auto"]
        if len(auto_group) >= 1:
            top_counts = auto_group["topic"].value_counts()
            if len(top_counts) > 0:
                top_topic = top_counts.index[0]
                # Dominan jika memegang >= 50% paragraf berlabel di artikel tersebut
                if top_counts.iloc[0] / len(auto_group) >= 0.5:
                    median_score = auto_group[auto_group["topic"] == top_topic]["topic_score"].median()
                    article_majority[title] = (top_topic, median_score)
    
    # 2. Precompute Title Scoring untuk fallback
    title_topics = {}
    for title in df_labeled["article_title"].dropna().unique():
        t_topic, t_score, *_ = score_topic(str(title))
        if t_topic != "unclassified":
            title_topics[title] = (t_topic, float(t_score))
    
    # Pastikan topic_score bertipe float agar kompatibel dengan nilai median
    df_labeled["topic_score"] = df_labeled["topic_score"].astype(float)
    
    # 3. Terapkan propagasi HANYA pada baris yang masih 'needs_review'
    propagated_article_cnt = 0
    propagated_title_cnt = 0
    
    for idx in df_labeled.index:
        if df_labeled.at[idx, "topic_method"] == "needs_review":
            title = df_labeled.at[idx, "article_title"]
            if title in article_majority:
                topic_prop, score_prop = article_majority[title]
                df_labeled.at[idx, "topic"] = topic_prop
                df_labeled.at[idx, "topic_score"] = float(score_prop)
                df_labeled.at[idx, "topic_method"] = "article_propagated"
                propagated_article_cnt += 1
            elif title in title_topics:
                topic_prop, score_prop = title_topics[title]
                df_labeled.at[idx, "topic"] = topic_prop
                df_labeled.at[idx, "topic_score"] = float(score_prop)
                df_labeled.at[idx, "topic_method"] = "title_propagated"
                propagated_title_cnt += 1
    
    print(f"   ├── Propagated from Article Majority : +{propagated_article_cnt} baris ({propagated_article_cnt/total*100:.1f}%)")
    print(f"   ├── Propagated from Title Fallback   : +{propagated_title_cnt} baris ({propagated_title_cnt/total*100:.1f}%)")
    print()
    
    # ===== STEP 4: Statistics & Reporting =====
    auto_direct = df_labeled[df_labeled["topic_method"] == "auto"]
    auto_article = df_labeled[df_labeled["topic_method"] == "article_propagated"]
    auto_title = df_labeled[df_labeled["topic_method"] == "title_propagated"]
    needs_review_topics = df_labeled[df_labeled["topic_method"] == "needs_review"]
    manual_topics = df_labeled[df_labeled["topic_method"] == "manual"]
    
    total_auto_labeled = len(auto_direct) + len(auto_article) + len(auto_title)
    
    print("=" * 65)
    print(f"📊 HASIL AKHIR LABELING (PASS 1 + PASS 2):")
    print(f"   Total Auto-labeled    : {total_auto_labeled} ({total_auto_labeled/total*100:.1f}%) ✅")
    print(f"     ├── Direct (Pass 1) : {len(auto_direct)} ({len(auto_direct)/total*100:.1f}%)")
    print(f"     ├── Article Majority: {len(auto_article)} ({len(auto_article)/total*100:.1f}%)")
    print(f"     └── Title Fallback  : {len(auto_title)} ({len(auto_title)/total*100:.1f}%)")
    print(f"   Needs Review (Sisa)   : {len(needs_review_topics)} ({len(needs_review_topics)/total*100:.1f}%) 🎯")
    print(f"   Manual (Kept)         : {len(manual_topics)} ({len(manual_topics)/total*100:.1f}%)")
    print("=" * 65)
    print()
    
    # Topic breakdown
    print("📊 DISTRIBUSI TOPIC:")
    topic_counts = df_labeled[df_labeled["topic"] != ""]["topic"].value_counts()
    for topic, count in topic_counts.items():
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"   {topic:20s} {count:5d} ({pct:5.1f}%) {bar}")
    
    unclassified = (df_labeled["topic"] == "").sum()
    pct_unclassified = unclassified / total * 100
    print(f"   {'(unclassified)':20s} {unclassified:5d} ({pct_unclassified:5.1f}%)")
    print()
    
    # Sentiment breakdown
    print("📊 DISTRIBUSI SENTIMENT:")
    sentiment_counts = df_labeled["sentiment"].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = count / total * 100
        emoji = "😊" if sentiment == "positive" else ("😞" if sentiment == "negative" else "😐")
        print(f"   {emoji} {sentiment:12s} {count:5d} ({pct:5.1f}%)")
    print()
    
    # ===== STEP 5: Split & Save =====
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Output columns sesuai spek dokumen planning
    output_cols = [
        "paragraph_id", "text", "article_title", "article_url",
        "source_portal", "publish_date", "aceh_confidence",
        "word_count", "query_used", "collector",
        "topic", "topic_score", "topic_method",
        "sentiment", "sentiment_pos_count", "sentiment_neg_count", "sentiment_method",
        "labeling_notes",
    ]
    
    # Pastikan semua kolom ada
    for col in output_cols:
        if col not in df_labeled.columns:
            df_labeled[col] = ""
    
    # 5a. Full labeled dataset
    df_labeled[output_cols].to_csv(OUTPUT_LABELED, index=False, encoding="utf-8-sig")
    
    # 5b. Needs review (topic kosong) — buat auto-backup jika file existing ada isinya
    if os.path.exists(OUTPUT_NEEDS_REVIEW) and os.path.getsize(OUTPUT_NEEDS_REVIEW) > 0:
        backup_file = OUTPUT_NEEDS_REVIEW + ".bak"
        try:
            import shutil
            shutil.copyfile(OUTPUT_NEEDS_REVIEW, backup_file)
            log.info("Auto-backup needs_review.csv created", backup=backup_file)
        except Exception as e:
            log.warning("Gagal membuat auto-backup needs_review.csv", error=str(e))
            
    df_review = df_labeled[df_labeled["topic_method"] == "needs_review"][output_cols]
    df_review.to_csv(OUTPUT_NEEDS_REVIEW, index=False, encoding="utf-8-sig")
    
    # 5c. Auto-labeled (semua yang confident untuk spot check)
    df_auto = df_labeled[df_labeled["topic_method"].isin(["auto", "article_propagated", "title_propagated"])][output_cols]
    df_auto.to_csv(OUTPUT_AUTO_LABELED, index=False, encoding="utf-8-sig")
    
    # 5d. Statistics JSON
    stats = {
        "total_rows": total,
        "auto_labeled_total": total_auto_labeled,
        "auto_labeled_direct": len(auto_direct),
        "auto_labeled_article_propagated": len(auto_article),
        "auto_labeled_title_propagated": len(auto_title),
        "needs_review": len(needs_review_topics),
        "manual_kept": len(manual_topics),
        "auto_label_pct": round(total_auto_labeled / total * 100, 1),
        "topic_distribution": topic_counts.to_dict(),
        "sentiment_distribution": sentiment_counts.to_dict(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    with open(LABEL_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # ===== RINGKASAN & LANGKAH SELANJUTNYA =====
    print("=" * 65)
    print("✅ LABELING SELESAI!")
    print("=" * 65)
    print()
    print(f"📁 Full dataset    : {OUTPUT_LABELED}")
    print(f"📁 Needs review    : {OUTPUT_NEEDS_REVIEW} ({len(df_review)} baris)")
    print(f"📁 Auto-labeled    : {OUTPUT_AUTO_LABELED} ({len(df_auto)} baris)")
    print(f"📁 Label stats     : {LABEL_STATS}")
    print()
    print("=" * 65)
    print("🎯 LANGKAH SELANJUTNYA (Human Review):")
    print("=" * 65)
    print()
    print(f"  1. BUKA needs_review.csv ({len(df_review)} baris) di Google Sheets atau Excel")
    print("  2. SORT berdasarkan 'article_title' untuk konteks")
    print("  3. ISI kolom 'topic' dengan salah satu:")
    print(f"     {list(TOPIC_RULES.keys())}")
    print("  4. ISI kolom 'sentiment' dengan: positive / negative / neutral")
    print("  5. SIMPAN file")
    print("=" * 65)
    
    log.info(
        "Labeling completed (2-pass)",
        total_auto_labeled=total_auto_labeled,
        needs_review=len(needs_review_topics),
        auto_label_pct=round(total_auto_labeled / total * 100, 1),
    )


if __name__ == "__main__":
    main()
