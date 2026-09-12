# Fase 3: Semi-Automated Labeling Pipeline

> **Estimasi waktu**: 1 - 1.5 hari kerja (termasuk human review)  
> **Prioritas**: 🔴 P0  
> **Prasyarat**: Fase 2 selesai (`data/processed/public_text_news_clean.csv` ada)  
> **Output**: `data/processed/labeled_dataset.csv` — Dataset berlabel siap ML  

---

## 🎯 Tujuan Fase Ini

1. **Auto-label ~60-70% data** — Menggunakan keyword rules (5 menit)
2. **Human review ~30-40% sisanya** — Yang tidak bisa di-auto-label (2-3 jam)
3. **Iterate rules** — Perbaiki rules berdasarkan temuan manual (30 menit)
4. **Validasi distribusi label** — Pastikan tidak terlalu skewed

---

## 📋 Label Categories

### Topic (8 kategori) — Sudah disetujui

| # | Topic | Deskripsi | Contoh keyword |
|---|-------|-----------|----------------|
| 1 | `funding` | Pendanaan, investasi, modal | pendanaan, investasi, modal, hibah, grant, fundraising, angel investor |
| 2 | `talent` | SDM, pelatihan, skill | talent, SDM, programmer, developer, pelatihan, bootcamp, training |
| 3 | `infrastructure` | Infrastruktur digital & fisik | infrastruktur, internet, jaringan, server, co-working, data center |
| 4 | `regulation` | Kebijakan, perizinan, regulasi | regulasi, kebijakan, peraturan, perizinan, OJK, izin usaha |
| 5 | `market_access` | Akses pasar, ekspansi | pasar, market, konsumen, customer, ekspansi, distribusi |
| 6 | `ecosystem` | Inkubator, komunitas, mentoring | inkubator, akselerator, komunitas, mentoring, co-working, hub |
| 7 | `digitalization` | Transformasi digital, adopsi | digitalisasi, transformasi digital, e-commerce, UMKM digital, online |
| 8 | `success_story` | Kisah sukses, pencapaian | berhasil, sukses, tumbuh, berkembang, penghargaan, inovasi |

### Sentiment (3 kategori) — Sudah disetujui

| Sentiment | Deskripsi | Contoh keyword |
|-----------|-----------|----------------|
| `positive` | Berita baik, peluang, pertumbuhan | berhasil, tumbuh, inovasi, peluang, potensi, dukungan, optimis |
| `negative` | Hambatan, masalah, kekurangan | hambatan, kendala, sulit, kurang, gagal, terbatas, tantangan, masalah |
| `neutral` | Berita informatif, deskriptif | (default — jika tidak match positive atau negative) |

---

## 📋 Daftar File yang Dibuat

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/05_labeling.py` | Script auto-labeling |
| **[NEW]** | `scraping/labeling_rules.py` | Rule definitions (terpisah agar mudah di-edit) |
| **Output** | `data/processed/labeled_dataset.csv` | Dataset final berlabel |
| **Output** | `data/processed/label_stats.json` | Statistik distribusi label |
| **Output** | `data/processed/needs_review.csv` | Baris yang perlu human review |

---

## Step 1: Buat `labeling_rules.py` — Definisi Rules

**File**: `sprint-3/materi-4/scraping/labeling_rules.py`

### Kenapa file terpisah?
- Rules akan sering di-update setelah human review
- Memisahkan rules dari logic membuat iterasi lebih cepat
- Agent lain / rekan bisa edit rules tanpa menyentuh logic

```python
"""
labeling_rules.py — Definisi rules untuk auto-labeling
GRAK 2026 · Sprint 3

Rules ini dipakai oleh 05_labeling.py untuk auto-label topic dan sentiment.

CARA UPDATE:
  1. Jalankan 05_labeling.py pertama kali
  2. Cek needs_review.csv → review manual
  3. Temukan pattern baru → tambahkan keyword di sini
  4. Jalankan 05_labeling.py lagi (idempotent, aman di-run ulang)
"""

# ============================================================
# TOPIC RULES — Keyword matching untuk auto-label topic
# ============================================================
# Setiap topic punya 3 tier keyword:
#   - strong: Kata-kata yang PASTI menunjukkan topic ini (confidence tinggi)
#   - medium: Kata-kata yang MUNGKIN menunjukkan topic ini (perlu konteks)
#   - weak: Kata-kata yang LEMAH, hanya sebagai pendukung
#
# Logic scoring:
#   score = (jumlah strong × 3) + (jumlah medium × 2) + (jumlah weak × 1)
#   Topic dipilih berdasarkan score tertinggi.
#   Minimum score = 3 untuk dianggap auto-labeled.

TOPIC_RULES = {
    "funding": {
        "strong": [
            "pendanaan", "investasi", "modal ventura", "venture capital",
            "fundraising", "angel investor", "seed funding", "hibah",
            "grant", "pinjaman modal", "kredit usaha", "KUR",
            "modal usaha", "dana bergulir",
        ],
        "medium": [
            "modal", "dana", "biaya", "anggaran", "subsidi",
            "permodalan", "kapitalisasi", "valuasi",
        ],
        "weak": [
            "uang", "rupiah", "miliar", "juta", "bisnis",
        ],
    },
    
    "talent": {
        "strong": [
            "talent digital", "sumber daya manusia", "SDM digital",
            "programmer", "developer", "software engineer",
            "bootcamp", "pelatihan coding", "pelatihan digital",
            "training IT", "sertifikasi", "fresh graduate",
            "digital marketer", "UI/UX designer",
        ],
        "medium": [
            "pelatihan", "training", "keterampilan", "skill",
            "lulusan", "mahasiswa", "kampus", "universitas",
            "dosen", "tenaga kerja", "SDM",
        ],
        "weak": [
            "belajar", "pendidikan", "sekolah", "kursus",
        ],
    },
    
    "infrastructure": {
        "strong": [
            "infrastruktur digital", "infrastruktur internet",
            "co-working space", "coworking", "data center",
            "pusat data", "server", "cloud computing",
            "jaringan internet", "fiber optik", "broadband",
            "BTS", "telekomunikasi",
        ],
        "medium": [
            "infrastruktur", "internet", "jaringan", "koneksi",
            "sinyal", "bandwidth", "akses internet",
            "ruang kerja", "gedung", "fasilitas",
        ],
        "weak": [
            "online", "wifi", "4G", "5G",
        ],
    },
    
    "regulation": {
        "strong": [
            "regulasi", "kebijakan pemerintah", "peraturan daerah",
            "perizinan usaha", "izin usaha", "SIUP", "NIB",
            "OSS", "OJK", "BKPM", "Kemenkumham",
            "perda", "qanun", "moratorium",
        ],
        "medium": [
            "kebijakan", "peraturan", "perizinan", "birokrasi",
            "aturan", "legalitas", "hukum", "undang-undang",
            "pemerintah daerah", "pemda",
        ],
        "weak": [
            "pemerintah", "dinas", "kementerian", "resmi",
        ],
    },
    
    "market_access": {
        "strong": [
            "akses pasar", "market access", "penetrasi pasar",
            "pangsa pasar", "target market", "ekspansi pasar",
            "distribusi produk", "supply chain",
            "export", "ekspor", "import",
        ],
        "medium": [
            "pasar", "market", "konsumen", "customer", "pelanggan",
            "penjualan", "revenue", "omzet", "transaksi",
            "produk", "jasa", "layanan",
        ],
        "weak": [
            "jual", "beli", "harga", "toko",
        ],
    },
    
    "ecosystem": {
        "strong": [
            "inkubator bisnis", "akselerator startup", "incubator",
            "accelerator", "mentoring startup", "mentor bisnis",
            "komunitas startup", "komunitas teknologi",
            "innovation hub", "startup hub", "tech community",
            "ekosistem startup", "ekosistem digital",
            "garuda spark", "startup weekend",
        ],
        "medium": [
            "inkubator", "akselerator", "mentor", "mentoring",
            "komunitas", "networking", "kolaborasi",
            "ekosistem", "hub", "co-creation",
        ],
        "weak": [
            "acara", "event", "workshop", "seminar", "webinar",
        ],
    },
    
    "digitalization": {
        "strong": [
            "transformasi digital", "digitalisasi UMKM",
            "UMKM digital", "go digital", "adopsi digital",
            "e-commerce", "marketplace", "toko online",
            "fintech", "payment gateway", "digital banking",
            "aplikasi mobile", "platform digital",
        ],
        "medium": [
            "digitalisasi", "digital", "teknologi informasi",
            "IT", "aplikasi", "platform", "website",
            "online", "elektronik",
        ],
        "weak": [
            "modern", "inovasi", "teknologi",
        ],
    },
    
    "success_story": {
        "strong": [
            "kisah sukses", "success story", "startup sukses",
            "penghargaan", "award", "juara", "pemenang",
            "berhasil meraih", "tumbuh pesat",
            "meraih pendanaan", "berhasil ekspansi",
            "unicorn", "centaur",
        ],
        "medium": [
            "berhasil", "sukses", "tumbuh", "berkembang",
            "meningkat", "naik", "pertumbuhan",
            "prestasi", "capaian", "pencapaian",
        ],
        "weak": [
            "positif", "baik", "bagus", "hebat",
        ],
    },
}


# ============================================================
# SENTIMENT RULES — Keyword matching untuk auto-label sentiment
# ============================================================
# Logic:
#   positive_score = jumlah keyword positive yang ditemukan
#   negative_score = jumlah keyword negative yang ditemukan
#   
#   Jika positive_score > negative_score dan positive_score >= 2 → "positive"
#   Jika negative_score > positive_score dan negative_score >= 2 → "negative"
#   Else → "neutral"

SENTIMENT_RULES = {
    "positive": [
        # Achievement / Success
        "berhasil", "sukses", "tumbuh", "berkembang", "meningkat",
        "prestasi", "pencapaian", "terobosan", "inovasi",
        "penghargaan", "juara", "terbaik", "unggul",
        
        # Opportunity / Potential
        "peluang", "potensi", "prospek", "harapan", "optimis",
        "menjanjikan", "potensial", "strategis",
        
        # Support / Enablement
        "dukungan", "mendukung", "mendorong", "memfasilitasi",
        "bantuan", "kolaborasi", "kerja sama", "kemitraan",
        "pemberdayaan", "pengembangan",
        
        # Growth / Impact
        "pertumbuhan", "perkembangan", "kemajuan", "progres",
        "dampak positif", "kontribusi", "manfaat",
    ],
    
    "negative": [
        # Barriers / Obstacles
        "hambatan", "kendala", "tantangan", "masalah", "kesulitan",
        "rintangan", "bottleneck", "barrier",
        
        # Limitation / Scarcity
        "kurang", "terbatas", "minim", "sedikit", "langka",
        "kekurangan", "keterbatasan", "tidak memadai",
        "tidak cukup", "belum tersedia",
        
        # Failure / Decline
        "gagal", "kegagalan", "menurun", "turun", "merosot",
        "bangkrut", "gulung tikar", "tutup",
        
        # Negative sentiment
        "sulit", "berat", "rumit", "kompleks", "mahal",
        "lambat", "tertinggal", "terbelakang",
        "pesimis", "khawatir", "cemas",
    ],
}


# ============================================================
# SCORING THRESHOLDS — Minimum score untuk auto-label
# ============================================================

# Topic: minimum total score agar dianggap auto-labeled
TOPIC_MIN_SCORE = 3  # Misal: 1 strong match (3 poin) sudah cukup

# Sentiment: minimum keyword match
SENTIMENT_MIN_MATCHES = 2  # Minimal 2 keyword match

# Jika score di bawah threshold → masuk needs_review.csv
```

### Verifikasi Step 1:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "
from labeling_rules import TOPIC_RULES, SENTIMENT_RULES
print(f'Topics: {list(TOPIC_RULES.keys())}')
print(f'Total topic keywords: {sum(len(v[\"strong\"]) + len(v[\"medium\"]) + len(v[\"weak\"]) for v in TOPIC_RULES.values())}')
print(f'Sentiment keywords: {sum(len(v) for v in SENTIMENT_RULES.values())}')
print('✅ Rules loaded OK')
"
```

---

## Step 2: Buat `05_labeling.py` — Auto-Labeling Script

**File**: `sprint-3/materi-4/scraping/05_labeling.py`

```python
"""
05_labeling.py — Semi-Automated Labeling Pipeline
GRAK 2026 · Sprint 3

CARA KERJA:
  1. Load dataset bersih dari Fase 2
  2. Auto-label topic menggunakan keyword scoring
  3. Auto-label sentiment menggunakan keyword matching
  4. Pisahkan: auto-labeled (confident) vs needs_review (uncertain)
  5. Export keduanya untuk human review

CARA PAKAI:
  python3 05_labeling.py

INPUT:
  → data/processed/public_text_news_clean.csv (dari 04_cleaning.py)

OUTPUT:
  → data/processed/labeled_dataset.csv   (SEMUA data — auto-labeled + empty labels)
  → data/processed/needs_review.csv      (Data yang PERLU human review)
  → data/processed/auto_labeled.csv      (Data yang SUDAH auto-labeled — untuk spot check)
  → data/processed/label_stats.json      (Statistik distribusi label)

WORKFLOW:
  1. Jalankan script ini: python3 05_labeling.py
  2. Buka needs_review.csv di Google Sheets / Excel
  3. Isi kolom 'topic' dan 'sentiment' secara manual
  4. Jika menemukan pattern baru → update labeling_rules.py
  5. Jalankan script ini lagi (safe, idempotent)
  6. Ulangi sampai needs_review.csv < 5% dari total
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

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


# ============================================================
# LABELING FUNCTIONS
# ============================================================

def score_topic(text: str) -> tuple[str, float, dict]:
    """
    Scoring topic berdasarkan keyword rules.
    
    Args:
        text: Text paragraf yang akan di-label
    
    Returns:
        Tuple of:
        - topic: nama topic dengan score tertinggi (atau "unclassified")
        - score: score tertinggi
        - all_scores: dict semua topic dan scorenya
    
    Scoring:
        strong keyword match = 3 poin
        medium keyword match = 2 poin
        weak keyword match   = 1 poin
        
    Topic dengan score tertinggi dipilih.
    Jika score < TOPIC_MIN_SCORE → "unclassified"
    """
    text_lower = text.lower()
    all_scores = {}
    
    for topic_name, keywords in TOPIC_RULES.items():
        score = 0
        
        # Count strong matches (3 poin each)
        for kw in keywords["strong"]:
            if kw in text_lower:
                score += 3
        
        # Count medium matches (2 poin each)
        for kw in keywords["medium"]:
            if kw in text_lower:
                score += 2
        
        # Count weak matches (1 poin each)
        for kw in keywords["weak"]:
            if kw in text_lower:
                score += 1
        
        all_scores[topic_name] = score
    
    # Pilih topic dengan score tertinggi
    if not all_scores:
        return "unclassified", 0, all_scores
    
    best_topic = max(all_scores, key=all_scores.get)
    best_score = all_scores[best_topic]
    
    # Check minimum threshold
    if best_score < TOPIC_MIN_SCORE:
        return "unclassified", best_score, all_scores
    
    return best_topic, best_score, all_scores


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
    
    positive_count = sum(1 for kw in SENTIMENT_RULES["positive"] if kw in text_lower)
    negative_count = sum(1 for kw in SENTIMENT_RULES["negative"] if kw in text_lower)
    
    # Determine sentiment
    if positive_count > negative_count and positive_count >= SENTIMENT_MIN_MATCHES:
        return "positive", positive_count, negative_count
    elif negative_count > positive_count and negative_count >= SENTIMENT_MIN_MATCHES:
        return "negative", positive_count, negative_count
    else:
        return "neutral", positive_count, negative_count


def label_single_row(row: pd.Series) -> pd.Series:
    """
    Label satu baris data.
    
    Menambahkan kolom:
    - topic: hasil auto-label topic
    - topic_score: score confidence
    - topic_method: "auto" atau "needs_review"
    - sentiment: hasil auto-label sentiment
    - sentiment_pos_count: jumlah positive matches
    - sentiment_neg_count: jumlah negative matches
    - sentiment_method: "auto" atau "needs_review"
    """
    text = str(row.get("text", ""))
    
    # === Topic ===
    topic, topic_score, _ = score_topic(text)
    
    if topic == "unclassified":
        topic_method = "needs_review"
    else:
        topic_method = "auto"
    
    # === Sentiment ===
    sentiment, pos_count, neg_count = score_sentiment(text)
    
    # Sentiment "neutral" bisa auto (karena neutral = default yang valid)
    if sentiment == "neutral" and pos_count == 0 and neg_count == 0:
        sentiment_method = "auto"  # Genuinely neutral — no sentiment words
    elif sentiment in ["positive", "negative"]:
        sentiment_method = "auto"
    else:
        sentiment_method = "auto"  # Neutral as fallback is fine
    
    # === Update row ===
    result = row.copy()
    result["topic"] = topic if topic != "unclassified" else ""
    result["topic_score"] = topic_score
    result["topic_method"] = topic_method
    result["sentiment"] = sentiment
    result["sentiment_pos_count"] = pos_count
    result["sentiment_neg_count"] = neg_count
    result["sentiment_method"] = sentiment_method
    
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
    print("🏷️  LABELING — Semi-Automated Labeling Pipeline")
    print(f"   Total paragraf: {total}")
    print(f"   Topics: {list(TOPIC_RULES.keys())}")
    print(f"   Sentiments: positive, negative, neutral")
    print("=" * 65)
    print()
    
    log.info("Starting labeling pipeline", total=total)
    
    # ===== STEP 1: Check for existing manual labels =====
    # Jika user sudah manual-label beberapa baris di CSV sebelumnya,
    # JANGAN overwrite label manual mereka.
    
    has_manual_topic = 0
    has_manual_sentiment = 0
    
    if "topic" in df.columns:
        has_manual_topic = df["topic"].notna().sum()
        has_manual_topic = (df["topic"] != "").sum()
    
    if "sentiment" in df.columns:
        has_manual_sentiment = df["sentiment"].notna().sum()
        has_manual_sentiment = (df["sentiment"] != "").sum()
    
    if has_manual_topic > 0 or has_manual_sentiment > 0:
        print(f"📋 Ditemukan label manual existing:")
        print(f"   Topic sudah diisi: {has_manual_topic} baris")
        print(f"   Sentiment sudah diisi: {has_manual_sentiment} baris")
        print(f"   → Label manual ini TIDAK akan di-overwrite")
        print()
    
    # ===== STEP 2: Auto-label =====
    print("🤖 Auto-labeling sedang berjalan...")
    
    results = []
    for idx, row in df.iterrows():
        # Skip jika sudah punya label manual
        existing_topic = str(row.get("topic", "")).strip()
        existing_sentiment = str(row.get("sentiment", "")).strip()
        
        labeled_row = label_single_row(row)
        
        # Preserve manual labels
        if existing_topic and existing_topic != "nan":
            labeled_row["topic"] = existing_topic
            labeled_row["topic_method"] = "manual"
            labeled_row["topic_score"] = -1  # -1 = manual
        
        if existing_sentiment and existing_sentiment != "nan":
            labeled_row["sentiment"] = existing_sentiment
            labeled_row["sentiment_method"] = "manual"
        
        results.append(labeled_row)
    
    df_labeled = pd.DataFrame(results)
    
    # ===== STEP 3: Statistics =====
    # Topic distribution
    auto_topics = df_labeled[df_labeled["topic_method"] == "auto"]
    needs_review_topics = df_labeled[df_labeled["topic_method"] == "needs_review"]
    manual_topics = df_labeled[df_labeled["topic_method"] == "manual"]
    
    print()
    print(f"📊 HASIL AUTO-LABELING:")
    print(f"   Auto-labeled  : {len(auto_topics)} ({len(auto_topics)/total*100:.1f}%)")
    print(f"   Needs review  : {len(needs_review_topics)} ({len(needs_review_topics)/total*100:.1f}%)")
    print(f"   Manual (kept) : {len(manual_topics)} ({len(manual_topics)/total*100:.1f}%)")
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
    
    # ===== STEP 4: Split & Save =====
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Output columns
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
    
    # 4a. Full labeled dataset
    df_labeled[output_cols].to_csv(OUTPUT_LABELED, index=False, encoding="utf-8-sig")
    
    # 4b. Needs review (topic kosong)
    df_review = df_labeled[df_labeled["topic_method"] == "needs_review"][output_cols]
    df_review.to_csv(OUTPUT_NEEDS_REVIEW, index=False, encoding="utf-8-sig")
    
    # 4c. Auto-labeled (untuk spot check)
    df_auto = df_labeled[df_labeled["topic_method"] == "auto"][output_cols]
    df_auto.to_csv(OUTPUT_AUTO_LABELED, index=False, encoding="utf-8-sig")
    
    # 4d. Statistics JSON
    stats = {
        "total_rows": total,
        "auto_labeled": len(auto_topics),
        "needs_review": len(needs_review_topics),
        "manual_kept": len(manual_topics),
        "auto_label_pct": round(len(auto_topics) / total * 100, 1),
        "topic_distribution": topic_counts.to_dict(),
        "sentiment_distribution": sentiment_counts.to_dict(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    with open(LABEL_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # ===== RINGKASAN =====
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
    print("  1. BUKA needs_review.csv di Google Sheets atau Excel")
    print("  2. SORT berdasarkan 'article_title' untuk konteks")
    print("  3. ISI kolom 'topic' dengan salah satu:")
    print(f"     {list(TOPIC_RULES.keys())}")
    print("  4. ISI kolom 'sentiment' dengan: positive / negative / neutral")
    print("  5. SIMPAN file")
    print()
    print("  6. JIKA menemukan pattern baru yang bisa di-automate:")
    print("     → Edit labeling_rules.py → tambah keyword baru")
    print("     → Jalankan ulang: python3 05_labeling.py")
    print()
    print("  7. SPOT CHECK auto_labeled.csv:")
    print("     → Buka file, cek 50-100 baris random")
    print("     → Jika ada yang salah → perbaiki rules → re-run")
    print()
    print("  8. JIKA SUDAH SELESAI review manual:")
    print("     → Gabungkan: copy label dari needs_review.csv ke labeled_dataset.csv")
    print("     → Atau jalankan: python3 06_merge_labels.py (jika tersedia)")
    print("=" * 65)
    
    log.info(
        "Labeling completed",
        auto_labeled=len(auto_topics),
        needs_review=len(needs_review_topics),
        auto_label_pct=round(len(auto_topics) / total * 100, 1),
    )


if __name__ == "__main__":
    main()
```

### Verifikasi Step 2:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 05_labeling.py
```

**Output yang diharapkan**:
- Auto-label rate ≥60%
- Distribusi topic dan sentiment terlihat
- 3 file CSV terbuat di `data/processed/`

---

## Step 3: Human Review Workflow ⭐ PALING PENTING

### 3.1 Review `needs_review.csv` (2-3 jam)

```
LANGKAH DETAIL:

1. Buka file: data/processed/needs_review.csv
   → Bisa pakai Google Sheets (upload) atau Excel

2. Sort berdasarkan kolom 'article_title'
   → Alasan: paragraf dari artikel yang sama biasanya punya topic yang sama
   → Ini mempercepat labeling karena tinggal copy-paste label

3. Untuk setiap baris:
   a. Baca kolom 'text'
   b. Tentukan 'topic' dari 8 pilihan:
      funding | talent | infrastructure | regulation | 
      market_access | ecosystem | digitalization | success_story
   
   c. Tentukan 'sentiment':
      positive | negative | neutral
   
   d. Tips cepat:
      - Jika ragu antara 2 topic → pilih yang lebih dominan
      - Jika benar-benar tidak relevan → tulis "irrelevant" di labeling_notes
      - Batch edit: select multiple rows yang topicnya sama → isi sekaligus

4. Simpan file setelah selesai review
```

### 3.2 Spot Check `auto_labeled.csv` (30-60 menit)

```
LANGKAH DETAIL:

1. Buka file: data/processed/auto_labeled.csv

2. Random sampling:
   → Sort random (atau ambil setiap baris ke-10)
   → Cek 50-100 baris

3. Untuk setiap baris yang dicek:
   a. Baca 'text'
   b. Bandingkan dengan 'topic' yang di-assign
   c. Tandai yang SALAH:
      → Ubah topic ke yang benar
      → Tulis di 'labeling_notes': "corrected from X to Y"

4. Hitung error rate:
   → Jika error > 10% → ada rules yang perlu diperbaiki
   → Jika error < 5% → rules sudah bagus
```

### 3.3 Iterate Rules (30 menit)

```
Jika ditemukan pattern yang salah atau missing:

1. Buka labeling_rules.py

2. Contoh fixes:
   
   # Kalau banyak text tentang "program inkubasi" masuk "unclassified":
   # → Tambah ke ecosystem.strong:
   "program inkubasi", "program akselerasi"
   
   # Kalau banyak text tentang "marketplace" salah masuk "ecosystem":
   # → Pindah "marketplace" dari ecosystem ke digitalization
   
   # Kalau banyak text netral salah masuk "positive":
   # → Naikkan SENTIMENT_MIN_MATCHES dari 2 ke 3

3. Simpan labeling_rules.py

4. Jalankan ulang: python3 05_labeling.py
   → Script idempotent (aman di-run berulang kali)
   → Label manual yang sudah di-review TIDAK akan di-overwrite
```

---

## Step 4: Merge Manual Labels ke Dataset Final

Setelah human review selesai, gabungkan hasilnya:

```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "
import pandas as pd

# Load auto-labeled (sudah punya topic)
df_auto = pd.read_csv('../data/processed/auto_labeled.csv')

# Load reviewed (sudah diisi manual)
df_reviewed = pd.read_csv('../data/processed/needs_review.csv')

# Gabungkan
df_final = pd.concat([df_auto, df_reviewed], ignore_index=True)

# Sort by paragraph_id
df_final = df_final.sort_values('paragraph_id').reset_index(drop=True)

# Cek kelengkapan
empty_topic = (df_final['topic'] == '').sum() + df_final['topic'].isna().sum()
print(f'Total baris: {len(df_final)}')
print(f'Topic kosong: {empty_topic}')
print(f'Topic coverage: {(len(df_final) - empty_topic) / len(df_final) * 100:.1f}%')

# Simpan final
df_final.to_csv('../data/processed/labeled_dataset_final.csv', index=False, encoding='utf-8-sig')
print(f'✅ Saved to labeled_dataset_final.csv')
"
```

---

## ✅ Checklist Fase 3 Selesai

Semua item di bawah harus ✓ sebelum lanjut ke Fase 4:

- [ ] `labeling_rules.py` — Rules ada dan bisa di-import
- [ ] `05_labeling.py` — Jalan tanpa error, auto-label ≥60%
- [ ] `needs_review.csv` — Sudah di-review manual (topic + sentiment diisi)
- [ ] `auto_labeled.csv` — Sudah di-spot-check (error rate <10%)
- [ ] Rules sudah di-iterate minimal 1x (update `labeling_rules.py` → re-run)
- [ ] `labeled_dataset_final.csv` — File terbuat, topic coverage ≥90%
- [ ] Distribusi topic tidak terlalu skewed (tidak ada 1 topic yang >50%)
- [ ] Distribusi sentiment masuk akal (positive+neutral biasanya >70% untuk berita)

---

## 🚨 Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| Auto-label rate <40% | Keywords kurang lengkap | Tambah keyword di `labeling_rules.py`, terutama di tier `strong` |
| Satu topic mendominasi (>50%) | Keywords terlalu broad | Pindahkan keyword yang terlalu umum dari `strong` ke `weak` |
| Banyak salah label sentiment | Berita Indonesia sering "positif framing negatif" | Naikkan `SENTIMENT_MIN_MATCHES` ke 3; review rules |
| `KeyError` saat merge | Kolom tidak konsisten | Cek header CSV konsisten antar file |
| Label manual hilang setelah re-run | Bug di preserve logic | Pastikan `05_labeling.py` cek `existing_topic` sebelum overwrite |

---

## 📝 Catatan untuk Agent / Rekan

1. **Script idempotent** — `05_labeling.py` aman di-run berkali-kali. Label manual yang sudah diisi di CSV TIDAK akan di-overwrite.
2. **Review manual WAJIB** — Auto-label bukan pengganti human review. Selalu spot-check hasilnya.
3. **Rules bisa di-update** — `labeling_rules.py` terpisah dari logic. Edit rules → re-run script.
4. **Scoring transparan** — Setiap baris punya `topic_score` yang menunjukkan confidence. Score tinggi = lebih yakin.
5. **Urutan optimal untuk human review**: Sort by `article_title` → paragraf dari artikel sama biasanya satu topic → batch label.
