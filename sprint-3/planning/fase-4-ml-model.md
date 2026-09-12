# Fase 4: Machine Learning Model Training

> **Estimasi waktu**: 1.5 - 2 hari kerja  
> **Prioritas**: 🔴 P0  
> **Prasyarat**: Fase 3 selesai (`labeled_dataset_final.csv` ada, coverage ≥90%)  
> **Output**: Trained ML model + evaluation report + prediction script  

---

## 🎯 Tujuan Fase Ini

1. **EDA (Exploratory Data Analysis)** — Pahami distribusi data sebelum training
2. **Feature Engineering** — Transform text ke representasi numerik (TF-IDF)
3. **Train Model** — Text classification untuk topic + sentiment
4. **Evaluate** — Precision, recall, F1-score per class
5. **Export** — Model siap pakai untuk predict data baru

---

## 📋 Daftar File yang Dibuat

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/06_eda.py` | Exploratory Data Analysis + visualisasi |
| **[NEW]** | `scraping/07_model_training.py` | Feature engineering + model training |
| **[NEW]** | `scraping/08_predict.py` | Script untuk predict data baru |
| **Output** | `data/processed/eda_report/` | Folder berisi grafik EDA |
| **Output** | `data/models/` | Folder berisi model .pkl |
| **Output** | `data/models/evaluation_report.json` | Metrics evaluasi |

---

## Step 0: Install Dependencies

```bash
pip install scikit-learn matplotlib seaborn wordcloud
```

### Library yang dipakai dan kenapa:

| Library | Untuk apa | Kenapa dipilih |
|---------|-----------|----------------|
| `scikit-learn` | TF-IDF + model training | Standard, mature, cukup untuk text classification sederhana |
| `matplotlib` + `seaborn` | Visualisasi | Standard Python plotting |
| `wordcloud` | Word cloud visualization | Visual yang bagus untuk presentasi |

### Kenapa BUKAN deep learning (BERT, GPT, etc)?

- Dataset kecil (~7,000 baris) → deep learning overfitting
- Text classification 8 kelas → TF-IDF + traditional ML sudah cukup
- Training time <5 menit vs hours untuk deep learning
- Tidak perlu GPU

---

## Step 1: Buat `06_eda.py` — Exploratory Data Analysis

**File**: `sprint-3/materi-4/scraping/06_eda.py`

```python
"""
06_eda.py — Exploratory Data Analysis untuk dataset labeled
GRAK 2026 · Sprint 3

CARA PAKAI:
  python3 06_eda.py

INPUT:
  → data/processed/labeled_dataset_final.csv

OUTPUT:
  → data/processed/eda_report/ (folder berisi grafik PNG)
  → Console: statistik ringkas

WAKTU: ~1-2 menit
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (bisa jalan tanpa display)
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.logger import get_logger

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
INPUT_CSV = os.path.join(PROCESSED_DIR, "labeled_dataset_final.csv")
EDA_DIR = os.path.join(PROCESSED_DIR, "eda_report")

log = get_logger("06_eda")

# Style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


def plot_topic_distribution(df: pd.DataFrame, output_dir: str):
    """Bar chart distribusi topic."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    topic_counts = df["topic"].value_counts()
    colors = sns.color_palette("husl", len(topic_counts))
    
    bars = ax.barh(topic_counts.index, topic_counts.values, color=colors)
    ax.set_xlabel("Jumlah Paragraf")
    ax.set_title("Distribusi Topic dalam Dataset", fontsize=14, fontweight="bold")
    
    # Tambah label di bar
    for bar, count in zip(bars, topic_counts.values):
        pct = count / len(df) * 100
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                f"{count} ({pct:.1f}%)", va="center", fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_topic_distribution.png"), dpi=150)
    plt.close()
    print("   ✓ 01_topic_distribution.png")


def plot_sentiment_distribution(df: pd.DataFrame, output_dir: str):
    """Pie chart distribusi sentiment."""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    sentiment_counts = df["sentiment"].value_counts()
    colors = {"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"}
    chart_colors = [colors.get(s, "#bdc3c7") for s in sentiment_counts.index]
    
    ax.pie(
        sentiment_counts.values,
        labels=sentiment_counts.index,
        autopct="%1.1f%%",
        colors=chart_colors,
        startangle=90,
        textprops={"fontsize": 12},
    )
    ax.set_title("Distribusi Sentiment", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_sentiment_distribution.png"), dpi=150)
    plt.close()
    print("   ✓ 02_sentiment_distribution.png")


def plot_topic_x_sentiment(df: pd.DataFrame, output_dir: str):
    """Stacked bar chart: topic × sentiment."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    cross_tab = pd.crosstab(df["topic"], df["sentiment"])
    
    colors = {"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"}
    
    cross_tab.plot(
        kind="barh",
        stacked=True,
        ax=ax,
        color=[colors.get(col, "#bdc3c7") for col in cross_tab.columns],
    )
    
    ax.set_xlabel("Jumlah Paragraf")
    ax.set_title("Topic × Sentiment Matrix", fontsize=14, fontweight="bold")
    ax.legend(title="Sentiment", loc="lower right")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_topic_x_sentiment.png"), dpi=150)
    plt.close()
    print("   ✓ 03_topic_x_sentiment.png")


def plot_word_count_distribution(df: pd.DataFrame, output_dir: str):
    """Histogram word count per paragraf."""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.hist(df["word_count"], bins=50, color="#3498db", alpha=0.7, edgecolor="white")
    ax.axvline(df["word_count"].mean(), color="red", linestyle="--",
               label=f"Mean: {df['word_count'].mean():.0f}")
    ax.axvline(df["word_count"].median(), color="green", linestyle="--",
               label=f"Median: {df['word_count'].median():.0f}")
    
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribusi Word Count per Paragraf", fontsize=14, fontweight="bold")
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "04_word_count_dist.png"), dpi=150)
    plt.close()
    print("   ✓ 04_word_count_dist.png")


def plot_portal_distribution(df: pd.DataFrame, output_dir: str):
    """Top 15 portal berita."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    portal_counts = df["source_portal"].value_counts().head(15)
    
    ax.barh(portal_counts.index[::-1], portal_counts.values[::-1], color="#9b59b6")
    ax.set_xlabel("Jumlah Paragraf")
    ax.set_title("Top 15 Portal Berita", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "05_portal_distribution.png"), dpi=150)
    plt.close()
    print("   ✓ 05_portal_distribution.png")


def plot_confidence_distribution(df: pd.DataFrame, output_dir: str):
    """Distribusi Aceh confidence level."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    conf_counts = df["aceh_confidence"].value_counts()
    colors = {"high": "#27ae60", "medium": "#f39c12", "low": "#e74c3c"}
    chart_colors = [colors.get(c, "#bdc3c7") for c in conf_counts.index]
    
    ax.bar(conf_counts.index, conf_counts.values, color=chart_colors)
    ax.set_ylabel("Jumlah Paragraf")
    ax.set_title("Distribusi Aceh Confidence Level", fontsize=14, fontweight="bold")
    
    for i, (idx, val) in enumerate(conf_counts.items()):
        ax.text(i, val + 50, str(val), ha="center", fontsize=12, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "06_aceh_confidence.png"), dpi=150)
    plt.close()
    print("   ✓ 06_aceh_confidence.png")


def generate_word_frequency_report(df: pd.DataFrame, output_dir: str):
    """Top 50 kata paling sering muncul per topic."""
    # Stopwords Indonesia sederhana
    stopwords_id = {
        "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "dari",
        "pada", "adalah", "ke", "akan", "juga", "tidak", "dalam",
        "ada", "bisa", "sudah", "oleh", "atau", "saat", "agar",
        "telah", "lebih", "mereka", "kami", "kita", "saya", "ia",
        "dia", "tersebut", "para", "serta", "menjadi", "secara",
        "bahwa", "masih", "dapat", "harus", "bagi", "lain",
        "antara", "setelah", "hingga", "tanpa", "sama", "begitu",
        "sebagai", "melalui", "sehingga", "namun", "seperti", "karena",
        "sangat", "semua", "setiap", "yakni", "terhadap", "satu",
        "dua", "tiga", "hal", "nya", "pun", "maupun",
    }
    
    report_lines = []
    
    for topic in df["topic"].unique():
        if not topic or pd.isna(topic):
            continue
        
        topic_texts = df[df["topic"] == topic]["text"].str.lower().str.cat(sep=" ")
        words = topic_texts.split()
        words_filtered = [w for w in words if w not in stopwords_id and len(w) > 2]
        
        counter = Counter(words_filtered)
        top_20 = counter.most_common(20)
        
        report_lines.append(f"\n=== TOPIC: {topic} ===")
        for word, count in top_20:
            report_lines.append(f"  {word}: {count}")
    
    report_text = "\n".join(report_lines)
    
    with open(os.path.join(output_dir, "word_frequency_per_topic.txt"), "w") as f:
        f.write(report_text)
    
    print("   ✓ word_frequency_per_topic.txt")


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ File tidak ditemukan: {INPUT_CSV}")
        print("   Jalankan labeling dulu (Fase 3)!")
        return
    
    df = pd.read_csv(INPUT_CSV)
    
    # Filter hanya yang sudah punya label
    df_labeled = df[df["topic"].notna() & (df["topic"] != "")].copy()
    
    print("=" * 65)
    print("📊 EDA — Exploratory Data Analysis")
    print(f"   Total baris (all)    : {len(df)}")
    print(f"   Total baris (labeled): {len(df_labeled)}")
    print("=" * 65)
    print()
    
    if len(df_labeled) < 100:
        print("⚠️ Dataset terlalu kecil untuk EDA yang bermakna (<100 baris labeled)")
        print("   Lakukan labeling dulu di Fase 3!")
        return
    
    os.makedirs(EDA_DIR, exist_ok=True)
    
    print("📈 Generating visualisasi...")
    plot_topic_distribution(df_labeled, EDA_DIR)
    plot_sentiment_distribution(df_labeled, EDA_DIR)
    plot_topic_x_sentiment(df_labeled, EDA_DIR)
    plot_word_count_distribution(df_labeled, EDA_DIR)
    plot_portal_distribution(df_labeled, EDA_DIR)
    plot_confidence_distribution(df_labeled, EDA_DIR)
    generate_word_frequency_report(df_labeled, EDA_DIR)
    
    print()
    print(f"📁 Grafik disimpan di: {EDA_DIR}")
    print()
    
    # Quick stats
    print("📊 Quick Stats:")
    print(f"   Unique topics     : {df_labeled['topic'].nunique()}")
    print(f"   Unique portals    : {df_labeled['source_portal'].nunique()}")
    print(f"   Unique articles   : {df_labeled['article_url'].nunique()}")
    print(f"   Avg word count    : {df_labeled['word_count'].mean():.1f}")
    print(f"   Date range        : {df_labeled['publish_date'].min()} → {df_labeled['publish_date'].max()}")
    print()
    
    print("▶️  Langkah selanjutnya: jalankan 'python3 07_model_training.py'")


if __name__ == "__main__":
    main()
```

### Verifikasi Step 1:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 06_eda.py
ls -la ../data/processed/eda_report/
```

**Output yang diharapkan**: 6 file PNG + 1 file TXT di `eda_report/`.

---

## Step 2: Buat `07_model_training.py` — ML Model Training ⭐

**File**: `sprint-3/materi-4/scraping/07_model_training.py`

### Arsitektur Model:

```
Text Input
    │
    ▼
┌──────────────────────┐
│   TF-IDF Vectorizer  │  Text → angka (sparse matrix)
│   max_features=5000  │
│   ngram_range=(1,2)  │  Unigram + Bigram
│   sublinear_tf=True  │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Model 1: Topic       │  LinearSVC (Support Vector Machine)
│ 8-class classifier   │  → Fast, good with high-dim sparse data
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Model 2: Sentiment   │  LogisticRegression  
│ 3-class classifier   │  → Simple, interpretable, good baseline
└──────────────────────┘
```

### Kenapa arsitektur ini?

| Pilihan | Alasan |
|---------|--------|
| TF-IDF | Lebih baik dari BoW karena mengurangi bobot kata common |
| Bigram | Menangkap "modal ventura", "transformasi digital" (2 kata) |
| LinearSVC | Terbaik untuk text classification high-dimensional sparse |
| Logistic Regression | Interpretable, bisa lihat coefficient per kata per class |
| Bukan BERT/LLM | Dataset <10K terlalu kecil, overfitting, butuh GPU |

### Code lengkap:

```python
"""
07_model_training.py — ML Model Training untuk Text Classification
GRAK 2026 · Sprint 3

CARA PAKAI:
  python3 07_model_training.py

INPUT:
  → data/processed/labeled_dataset_final.csv (dari Fase 3)

OUTPUT:
  → data/models/topic_model.pkl           (Topic classifier)
  → data/models/sentiment_model.pkl       (Sentiment classifier)
  → data/models/tfidf_vectorizer.pkl      (TF-IDF vectorizer, shared)
  → data/models/evaluation_report.json    (Metrics evaluasi)
  → data/models/confusion_matrix_topic.png
  → data/models/confusion_matrix_sentiment.png
  → data/models/top_features_per_topic.txt

WAKTU: ~1-3 menit (tergantung ukuran dataset)
"""

import os
import sys
import json
import pickle
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
)
from sklearn.pipeline import Pipeline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.logger import get_logger

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")
INPUT_CSV = os.path.join(PROCESSED_DIR, "labeled_dataset_final.csv")

log = get_logger("07_model_training")
plt.style.use("seaborn-v0_8-whitegrid")


# ============================================================
# STOPWORDS INDONESIA — Untuk TF-IDF
# ============================================================
STOPWORDS_ID = [
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "dari",
    "pada", "adalah", "ke", "akan", "juga", "tidak", "dalam",
    "ada", "bisa", "sudah", "oleh", "atau", "saat", "agar",
    "telah", "lebih", "mereka", "kami", "kita", "saya", "ia",
    "dia", "tersebut", "para", "serta", "menjadi", "secara",
    "bahwa", "masih", "dapat", "harus", "bagi", "lain",
    "antara", "setelah", "hingga", "tanpa", "sama", "begitu",
    "sebagai", "melalui", "sehingga", "namun", "seperti", "karena",
    "sangat", "semua", "setiap", "yakni", "terhadap", "satu",
    "dua", "tiga", "hal", "nya", "pun", "maupun", "sejak",
    "sedang", "belum", "lalu", "kemudian", "bukan", "hanya",
]


def plot_confusion_matrix(
    y_true, y_pred, labels, title: str, output_path: str
):
    """Buat confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title, fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def extract_top_features(vectorizer, model, class_names, top_n=10):
    """
    Extract top TF-IDF features (kata paling berpengaruh) per class.
    Hanya works untuk model linear (SVC, LogReg).
    """
    feature_names = vectorizer.get_feature_names_out()
    report_lines = []
    
    if hasattr(model, "coef_"):
        for i, class_name in enumerate(class_names):
            if i < len(model.coef_):
                coef = model.coef_[i]
                top_indices = np.argsort(coef)[-top_n:][::-1]
                top_features = [(feature_names[j], round(coef[j], 4)) for j in top_indices]
                
                report_lines.append(f"\n=== {class_name} ===")
                for feat, weight in top_features:
                    report_lines.append(f"  {feat}: {weight}")
    
    return "\n".join(report_lines)


def main():
    # ===== Load Data =====
    if not os.path.exists(INPUT_CSV):
        print(f"❌ File tidak ditemukan: {INPUT_CSV}")
        print("   Jalankan labeling dulu (Fase 3)!")
        return
    
    df = pd.read_csv(INPUT_CSV)
    
    # Filter: hanya baris yang punya topic DAN sentiment
    df = df.dropna(subset=["topic", "sentiment"])
    df = df[(df["topic"] != "") & (df["sentiment"] != "")]
    
    if len(df) < 200:
        print(f"⚠️ Dataset terlalu kecil ({len(df)} baris) untuk training yang bermakna")
        print("   Minimal 200 baris labeled diperlukan!")
        return
    
    print("=" * 65)
    print("🤖 ML MODEL TRAINING — Text Classification")
    print(f"   Dataset size     : {len(df)} baris berlabel")
    print(f"   Unique topics    : {df['topic'].nunique()}")
    print(f"   Unique sentiments: {df['sentiment'].nunique()}")
    print(f"   Train/Test split : 80% / 20%")
    print("=" * 65)
    print()
    
    log.info("Starting model training", dataset_size=len(df))
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    X = df["text"].values
    y_topic = df["topic"].values
    y_sentiment = df["sentiment"].values
    
    # ===== STEP 1: TF-IDF Vectorization =====
    print("📊 Step 1/5: TF-IDF Vectorization...")
    
    tfidf = TfidfVectorizer(
        max_features=5000,       # Top 5000 kata
        ngram_range=(1, 2),      # Unigram + Bigram
        sublinear_tf=True,       # Logarithmic TF scaling
        min_df=3,                # Minimal muncul di 3 dokumen
        max_df=0.85,             # Maks 85% dokumen (terlalu common = tidak informatif)
        strip_accents="unicode",
        stop_words=STOPWORDS_ID,
    )
    
    X_tfidf = tfidf.fit_transform(X)
    
    print(f"   Vocabulary size  : {len(tfidf.vocabulary_)}")
    print(f"   Matrix shape     : {X_tfidf.shape}")
    print()
    
    # Simpan vectorizer
    with open(os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    
    evaluation = {
        "dataset_size": len(df),
        "vocabulary_size": len(tfidf.vocabulary_),
        "tfidf_shape": list(X_tfidf.shape),
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # ===== STEP 2: Train Topic Classifier =====
    print("🏷️  Step 2/5: Training Topic Classifier (LinearSVC)...")
    
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_tfidf, y_topic, test_size=0.2, random_state=42, stratify=y_topic
    )
    
    topic_model = LinearSVC(
        max_iter=10000,
        C=1.0,
        class_weight="balanced",  # Handle class imbalance
    )
    topic_model.fit(X_train_t, y_train_t)
    
    # Evaluate
    y_pred_topic = topic_model.predict(X_test_t)
    topic_accuracy = accuracy_score(y_test_t, y_pred_topic)
    topic_f1_macro = f1_score(y_test_t, y_pred_topic, average="macro")
    topic_report = classification_report(y_test_t, y_pred_topic, output_dict=True)
    
    print(f"   Accuracy  : {topic_accuracy:.3f}")
    print(f"   F1 (macro): {topic_f1_macro:.3f}")
    print()
    
    # Cross-validation
    cv_scores = cross_val_score(
        LinearSVC(max_iter=10000, C=1.0, class_weight="balanced"),
        X_tfidf, y_topic, cv=5, scoring="f1_macro"
    )
    print(f"   5-Fold CV F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print()
    
    # Per-class report
    print("   Per-class report:")
    report_text = classification_report(y_test_t, y_pred_topic)
    for line in report_text.split("\n"):
        print(f"   {line}")
    print()
    
    # Confusion matrix
    topic_labels = sorted(df["topic"].unique())
    plot_confusion_matrix(
        y_test_t, y_pred_topic, topic_labels,
        "Topic Classifier — Confusion Matrix",
        os.path.join(MODELS_DIR, "confusion_matrix_topic.png")
    )
    print("   ✓ confusion_matrix_topic.png")
    
    # Top features per topic
    feature_report = extract_top_features(tfidf, topic_model, topic_labels)
    with open(os.path.join(MODELS_DIR, "top_features_per_topic.txt"), "w") as f:
        f.write(feature_report)
    print("   ✓ top_features_per_topic.txt")
    
    # Save model
    with open(os.path.join(MODELS_DIR, "topic_model.pkl"), "wb") as f:
        pickle.dump(topic_model, f)
    
    evaluation["topic"] = {
        "model": "LinearSVC",
        "accuracy": round(topic_accuracy, 4),
        "f1_macro": round(topic_f1_macro, 4),
        "cv_f1_mean": round(cv_scores.mean(), 4),
        "cv_f1_std": round(cv_scores.std(), 4),
        "per_class": topic_report,
    }
    
    # ===== STEP 3: Train Sentiment Classifier =====
    print("😊 Step 3/5: Training Sentiment Classifier (LogisticRegression)...")
    
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X_tfidf, y_sentiment, test_size=0.2, random_state=42, stratify=y_sentiment
    )
    
    sentiment_model = LogisticRegression(
        max_iter=10000,
        C=1.0,
        class_weight="balanced",
        multi_class="multinomial",
        solver="lbfgs",
    )
    sentiment_model.fit(X_train_s, y_train_s)
    
    # Evaluate
    y_pred_sent = sentiment_model.predict(X_test_s)
    sent_accuracy = accuracy_score(y_test_s, y_pred_sent)
    sent_f1_macro = f1_score(y_test_s, y_pred_sent, average="macro")
    sent_report = classification_report(y_test_s, y_pred_sent, output_dict=True)
    
    print(f"   Accuracy  : {sent_accuracy:.3f}")
    print(f"   F1 (macro): {sent_f1_macro:.3f}")
    print()
    
    # Per-class report
    print("   Per-class report:")
    report_text = classification_report(y_test_s, y_pred_sent)
    for line in report_text.split("\n"):
        print(f"   {line}")
    print()
    
    # Confusion matrix
    sentiment_labels = sorted(df["sentiment"].unique())
    plot_confusion_matrix(
        y_test_s, y_pred_sent, sentiment_labels,
        "Sentiment Classifier — Confusion Matrix",
        os.path.join(MODELS_DIR, "confusion_matrix_sentiment.png")
    )
    print("   ✓ confusion_matrix_sentiment.png")
    
    # Save model
    with open(os.path.join(MODELS_DIR, "sentiment_model.pkl"), "wb") as f:
        pickle.dump(sentiment_model, f)
    
    evaluation["sentiment"] = {
        "model": "LogisticRegression",
        "accuracy": round(sent_accuracy, 4),
        "f1_macro": round(sent_f1_macro, 4),
        "per_class": sent_report,
    }
    
    # ===== STEP 4: Save Evaluation Report =====
    print("📊 Step 4/5: Saving evaluation report...")
    
    with open(os.path.join(MODELS_DIR, "evaluation_report.json"), "w") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False, default=str)
    print("   ✓ evaluation_report.json")
    
    # ===== STEP 5: Quick Prediction Test =====
    print()
    print("🧪 Step 5/5: Quick prediction test...")
    
    test_texts = [
        "Startup di Banda Aceh mendapat pendanaan dari investor sebesar 5 miliar",
        "Kurangnya akses internet menjadi kendala utama UMKM digital di pedalaman Aceh",
        "Program inkubator bisnis Garuda Spark meluncurkan batch kedua di Aceh",
    ]
    
    for text in test_texts:
        X_test = tfidf.transform([text])
        pred_topic = topic_model.predict(X_test)[0]
        pred_sent = sentiment_model.predict(X_test)[0]
        print(f"   Text: \"{text[:80]}...\"")
        print(f"   → Topic: {pred_topic} | Sentiment: {pred_sent}")
        print()
    
    # ===== RINGKASAN =====
    print("=" * 65)
    print("✅ MODEL TRAINING SELESAI!")
    print("=" * 65)
    print()
    print(f"📊 Topic Model:")
    print(f"   Accuracy: {topic_accuracy:.3f} | F1: {topic_f1_macro:.3f}")
    print(f"   5-Fold CV: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print()
    print(f"📊 Sentiment Model:")
    print(f"   Accuracy: {sent_accuracy:.3f} | F1: {sent_f1_macro:.3f}")
    print()
    print(f"📁 Models  : {MODELS_DIR}")
    print(f"📁 Report  : {os.path.join(MODELS_DIR, 'evaluation_report.json')}")
    print()
    print("▶️  Langkah selanjutnya: jalankan 'python3 08_predict.py'")
    print("=" * 65)
    
    log.info(
        "Training completed",
        topic_f1=round(topic_f1_macro, 4),
        sentiment_f1=round(sent_f1_macro, 4),
    )


if __name__ == "__main__":
    main()
```

### Verifikasi Step 2:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 07_model_training.py
```

**Output yang diharapkan**:
- Topic accuracy ≥0.70 (70%)
- Sentiment accuracy ≥0.65 (65%)
- Model files tersimpan di `data/models/`
- Confusion matrix PNG terbuat

---

## Step 3: Buat `08_predict.py` — Prediction Script

**File**: `sprint-3/materi-4/scraping/08_predict.py`

### Fungsi:
- Load model yang sudah di-train
- Predict topic + sentiment untuk data baru
- Bisa dipakai untuk data wilayah lain (Anum, Neni, Taris)

```python
"""
08_predict.py — Predict topic & sentiment untuk data baru
GRAK 2026 · Sprint 3

CARA PAKAI:
  # Predict satu text:
  python3 08_predict.py --text "Startup di Aceh mendapat pendanaan"
  
  # Predict dari CSV:
  python3 08_predict.py --input data/new_data.csv --output data/new_data_predicted.csv

INPUT:
  → data/models/*.pkl (dari 07_model_training.py)

PRASYARAT:
  → Sudah jalankan 07_model_training.py
"""

import os
import sys
import pickle
import argparse
import pandas as pd

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)
MODELS_DIR = os.path.join(DATA_DIR, "models")


def load_models():
    """Load TF-IDF vectorizer + models."""
    with open(os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
        tfidf = pickle.load(f)
    with open(os.path.join(MODELS_DIR, "topic_model.pkl"), "rb") as f:
        topic_model = pickle.load(f)
    with open(os.path.join(MODELS_DIR, "sentiment_model.pkl"), "rb") as f:
        sentiment_model = pickle.load(f)
    
    return tfidf, topic_model, sentiment_model


def predict_single(text: str, tfidf, topic_model, sentiment_model) -> dict:
    """Predict topic + sentiment untuk satu text."""
    X = tfidf.transform([text])
    topic = topic_model.predict(X)[0]
    sentiment = sentiment_model.predict(X)[0]
    return {"topic": topic, "sentiment": sentiment}


def predict_batch(df: pd.DataFrame, tfidf, topic_model, sentiment_model) -> pd.DataFrame:
    """Predict topic + sentiment untuk DataFrame."""
    X = tfidf.transform(df["text"].values)
    df = df.copy()
    df["predicted_topic"] = topic_model.predict(X)
    df["predicted_sentiment"] = sentiment_model.predict(X)
    return df


def main():
    parser = argparse.ArgumentParser(description="Predict topic & sentiment")
    parser.add_argument("--text", type=str, help="Single text to predict")
    parser.add_argument("--input", type=str, help="Input CSV file path")
    parser.add_argument("--output", type=str, help="Output CSV file path")
    args = parser.parse_args()
    
    # Load models
    tfidf, topic_model, sentiment_model = load_models()
    print("✅ Models loaded")
    
    if args.text:
        # Single prediction
        result = predict_single(args.text, tfidf, topic_model, sentiment_model)
        print(f"Text: {args.text[:100]}...")
        print(f"Topic: {result['topic']}")
        print(f"Sentiment: {result['sentiment']}")
    
    elif args.input:
        # Batch prediction
        df = pd.read_csv(args.input)
        print(f"Input: {len(df)} rows")
        
        df_predicted = predict_batch(df, tfidf, topic_model, sentiment_model)
        
        output_path = args.output or args.input.replace(".csv", "_predicted.csv")
        df_predicted.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ Predictions saved to: {output_path}")
        
        # Quick stats
        print(f"\nTopic distribution:")
        print(df_predicted["predicted_topic"].value_counts())
        print(f"\nSentiment distribution:")
        print(df_predicted["predicted_sentiment"].value_counts())
    
    else:
        # Interactive mode
        print("Mode interaktif. Ketik text untuk predict (ketik 'exit' untuk keluar):")
        while True:
            text = input("\n📝 Text: ").strip()
            if text.lower() == "exit":
                break
            result = predict_single(text, tfidf, topic_model, sentiment_model)
            print(f"   🏷️  Topic    : {result['topic']}")
            print(f"   😊 Sentiment: {result['sentiment']}")


if __name__ == "__main__":
    main()
```

---

## Step 4: Verifikasi Model

### 4.1 Cek model files

```bash
ls -la /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/data/models/
# Harus ada:
#   tfidf_vectorizer.pkl
#   topic_model.pkl
#   sentiment_model.pkl
#   evaluation_report.json
#   confusion_matrix_topic.png
#   confusion_matrix_sentiment.png
#   top_features_per_topic.txt
```

### 4.2 Test prediction

```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 08_predict.py --text "Program inkubator bisnis di Banda Aceh berhasil melahirkan 10 startup baru"
```

### 4.3 Quality gate

| Metric | Minimum | Target |
|--------|---------|--------|
| Topic accuracy | ≥0.60 | ≥0.75 |
| Topic F1 (macro) | ≥0.55 | ≥0.70 |
| Sentiment accuracy | ≥0.55 | ≥0.65 |
| No class with F1 < 0.3 | ✓ | ✓ |

**Jika accuracy di bawah minimum**:
1. Cek distribusi label — mungkin terlalu imbalanced
2. Cek kualitas label — mungkin banyak yang salah label
3. Tambahkan data — scrape lebih banyak artikel
4. Coba model lain — RandomForest, atau naïve bayes

---

## ✅ Checklist Fase 4 Selesai

- [ ] `06_eda.py` — Jalan, 6 grafik PNG terbuat
- [ ] `07_model_training.py` — Jalan, 3 model .pkl tersimpan
- [ ] `08_predict.py` — Bisa predict single text dan batch CSV
- [ ] Topic accuracy ≥0.60
- [ ] Sentiment accuracy ≥0.55
- [ ] `evaluation_report.json` — Ada dan lengkap
- [ ] Confusion matrix — Visual masuk akal (diagonal dominan)
- [ ] Quick prediction test — Hasil prediction masuk akal

---

## 🚨 Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `ModuleNotFoundError: sklearn` | Belum install | `pip install scikit-learn` |
| Accuracy sangat rendah (<50%) | Label tidak konsisten | Review labeling di Fase 3 |
| Satu class punya F1 = 0 | Terlalu sedikit sampel | Gabung class kecil, atau tambah data |
| `ValueError: could not convert` | Data NaN / kosong | Filter `df.dropna(subset=["topic"])` |
| Model terlalu besar (>100MB) | Vocabulary terlalu besar | Turunkan `max_features` TF-IDF dari 5000 ke 3000 |
| Overfitting (train acc tinggi, test rendah) | Dataset kecil | Naikkan `C` di SVC, atau pakai regularization |

---

## 📝 Catatan untuk Agent / Rekan

1. **Model bersifat domain-specific** — Hanya untuk data ekosistem startup Aceh. Tidak bisa dipakai untuk domain lain tanpa re-train.
2. **Re-train jika data berubah signifikan** — Setelah tambah data dari wilayah lain, re-run `07_model_training.py`.
3. **Pickle files** — Model disimpan sebagai `.pkl`. Hati-hati dengan versi scikit-learn — pickle tidak backward compatible jika sklearn di-upgrade major version.
4. **Interactive mode** — `python3 08_predict.py` tanpa argumen masuk mode interaktif untuk quick testing.
5. **Batch prediction** — Untuk predict data tim lain: `python3 08_predict.py --input data/wilayah_barat.csv --output data/wilayah_barat_predicted.csv`
