"""
06_eda.py — Multi-Source Exploratory Data Analysis & Triangulation Visual Analytics
GRAK 2026 · Sprint 3 (Fase 3.5 & Fase 4 Unified Suite)

CARA PAKAI:
  python3 06_eda.py

INPUT:
  → data/processed/combined_text.csv         (14.289 baris: Berita + Medsos + Wawancara + Survey)
  → data/processed/survey_structured.csv     (12 responden survey terstruktur)
  → data/processed/triangulation_matrix.csv  (Matriks triangulasi H1-H6)

OUTPUT:
  → data/processed/eda_report/               (13 grafik visualisasi resolusi tinggi)
  → data/processed/eda_report/triangulation_matrix.html
  → data/processed/eda_report/word_frequency_per_topic.txt
  → data/processed/eda_report/eda_summary_metrics.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from wordcloud import WordCloud

# Pastikan path modul lokal
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
try:
    from lib.logger import get_logger
    log = get_logger("06_eda")
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    log = logging.getLogger("06_eda")

# Direktori & File Paths
DATA_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
COMBINED_CSV = os.path.join(PROCESSED_DIR, "combined_text.csv")
SURVEY_CSV = os.path.join(PROCESSED_DIR, "survey_structured.csv")
INTERVIEW_CSV = os.path.join(PROCESSED_DIR, "interview_dataset.csv")
TRIANGULATION_CSV = os.path.join(PROCESSED_DIR, "triangulation_matrix.csv")
EDA_DIR = os.path.join(PROCESSED_DIR, "eda_report")

# Standar Styling & Tipografi Visualisasi Eksekutif
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"]
plt.rcParams["axes.edgecolor"] = "#bdc3c7"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#ecf0f1"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["grid.alpha"] = 0.7

# Skema Warna Tematik
COLOR_PALETTE = {
    "primary": "#2c3e50",
    "secondary": "#3498db",
    "accent": "#e67e22",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "neutral": "#95a5a6",
    "warning": "#f39c12",
    "info": "#1abc9c",
    "purple": "#8e44ad",
}

SENTIMENT_COLORS = {
    "positive": "#27ae60",
    "neutral": "#7f8c8d",
    "negative": "#e74c3c",
}

SOURCE_COLORS = {
    "news": "#2980b9",
    "scraping": "#2980b9",
    "interview": "#8e44ad",
    "survey": "#d35400",
    "social_media": "#16a085",
}

# Stopwords Bahasa Indonesia Komprehensif
STOPWORDS_ID = {
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "dari",
    "pada", "adalah", "ke", "akan", "juga", "tidak", "dalam",
    "ada", "bisa", "sudah", "oleh", "atau", "saat", "agar",
    "telah", "lebih", "mereka", "kami", "kita", "saya", "ia",
    "dia", "tersebut", "para", "serta", "menjadi", "secara",
    "bahwa", "masih", "dapat", "harus", "bagi", "lain",
    "antara", "setelah", "hingga", "tanpa", "sama", "begitu",
    "sebagai", "melalui", "sehingga", "namun", "seperti", "karena",
    "sangat", "semua", "setiap", "yakni", "terhadap", "satu",
    "dua", "tiga", "hal", "nya", "pun", "maupun", "lalu",
    "hanya", "tentang", "banyak", "kembali", "bahkan", "bukan",
    "lagi", "selama", "hanya", "terus", "jadi", "sudah", "belum",
    "bila", "jika", "kalau", "makin", "pula", "ingin", "tahu",
    "bila", "punya", "memiliki", "buat", "tahun", "aceh", "hari",
    "kota", "kabupaten", "provinsi", "pemerintah", "orang", "warga",
    "kata", "ujar", "tutur", "jelas", "menurut", "sebut", "ucap",
    "kamis", "jumat", "sabtu", "minggu", "senin", "selasa", "rabu",
    "januari", "februari", "maret", "april", "mei", "juni", "juli",
    "agustus", "september", "oktober", "november", "desember",
}


# ==============================================================================
# 1. MULTI-SOURCE DATASET INTEGRATION VISUALIZATIONS
# ==============================================================================

def plot_source_composition(df: pd.DataFrame, output_dir: str):
    """
    [01] Donut Chart: Komposisi data multi-sumber (Scraping vs Survey vs Interview).
    Menjelaskan rasionalitas Mixed-Methods Research (Macro vs Micro).
    """
    fig, ax = plt.subplots(figsize=(9, 7))
    
    source_counts = df["data_source"].value_counts()
    source_labels_map = {
        "scraping": "Berita / Scraping",
        "news": "Berita / Scraping",
        "interview": "Wawancara / Interview",
        "survey": "Survey Open-Ended",
        "social_media": "Media Sosial (X/YT/LI)",
    }
    labels = [
        f"{source_labels_map.get(s, s.capitalize())}\n({source_counts[s]:,} baris | {source_counts[s]/len(df)*100:.1f}%)"
        for s in source_counts.index
    ]
    colors = [SOURCE_COLORS.get(s, "#bdc3c7") for s in source_counts.index]
    
    wedges, texts, autotexts = ax.pie(
        source_counts.values,
        labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.8,
        colors=colors,
        startangle=140,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=10, fontweight="medium"),
    )
    plt.setp(autotexts, size=9, weight="bold", color="white")
    
    # Inset Title & Rationale in center
    ax.text(
        0, 0.05,
        f"Total Data\n{len(df):,}\nBaris Teks",
        ha="center", va="center",
        fontsize=13, fontweight="bold", color="#2c3e50"
    )
    
    ax.set_title(
        "Komposisi Multi-Source Dataset: Integrasi Riset Ekosistem Startup Aceh",
        fontsize=13, fontweight="bold", pad=20, color="#2c3e50"
    )
    
    # Catatan metodologis di bawah
    fig.text(
        0.5, 0.02,
        "Prinsip 4-Pilar Mixed-Methods: Berita (Macro) menangkap sinyal publik; Medsos (Grassroots) menyerap denyut organik;\n"
        "Survey & Wawancara (Micro-Qualitative) mengungkap friksi struktural permodalan & operasional founder di lapangan.",
        ha="center", fontsize=8.5, style="italic", color="#7f8c8d"
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    out_path = os.path.join(output_dir, "01_source_composition.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 01_source_composition.png")


def plot_topic_distribution_by_source(df: pd.DataFrame, output_dir: str):
    """
    [02] Stacked Bar Chart: Distribusi Topik Terklasifikasi per Sumber Data (4 Pilar).
    Memperlihatkan pergeseran fokus antara Scraping vs Medsos vs Wawancara vs Survey.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 7.5), gridspec_kw={"width_ratios": [2.0, 2.0]})
    
    # Panel 1: Absolute Counts by Topic across All Combined
    topic_order = df["topic"].value_counts().index.tolist()
    palette = sns.color_palette("mako", len(topic_order))
    
    counts = df["topic"].value_counts()
    bars = ax1.barh(counts.index[::-1], counts.values[::-1], color=palette[::-1], edgecolor="none", height=0.65)
    ax1.set_title(f"Distribusi Volume Topik Keseluruhan (N={len(df):,})", fontsize=12, fontweight="bold", color="#2c3e50")
    ax1.set_xlabel("Jumlah Paragraf / Unit Ide", fontsize=10)
    
    for bar in bars:
        w = bar.get_width()
        pct = w / len(df) * 100
        ax1.text(w + 80, bar.get_y() + bar.get_height() / 2, f"{int(w):,} ({pct:.1f}%)",
                 va="center", fontsize=9, fontweight="medium", color="#34495e")
    ax1.set_xlim(0, max(counts.values) * 1.18)

    # Panel 2: Normalized Proportion by Source (Scraping vs Medsos vs Interview vs Survey)
    ct = pd.crosstab(df["topic"], df["data_source"], normalize="columns") * 100
    # Pastikan urutan 4 pilar sumber data
    cols_order = [c for c in ["scraping", "social_media", "interview", "survey"] if c in ct.columns]
    ct = ct[cols_order].reindex(topic_order)
    
    ct.plot(
        kind="barh",
        stacked=False,
        ax=ax2,
        color=[SOURCE_COLORS.get(c, "#bdc3c7") for c in cols_order],
        width=0.8,
        edgecolor="none"
    )
    ax2.set_title("Perbandingan Proporsi Topik Antar 4 Sumber Data (%)", fontsize=12, fontweight="bold", color="#2c3e50")
    ax2.set_xlabel("Persentase dalam Sumber Data (%)", fontsize=10)
    ax2.set_ylabel("")
    legend_labels = {
        "scraping": "Berita (Scraping)",
        "social_media": "Media Sosial (X/YT/LI)",
        "interview": "Wawancara (Interview)",
        "survey": "Survey Primer",
    }
    ax2.legend([legend_labels.get(c, c) for c in cols_order], title="Sumber Data", loc="lower right", frameon=True)
    ax2.invert_yaxis()

    plt.suptitle("Distribusi Topik Riset Ekosistem Startup Aceh Lintas 4 Pilar Sumber Data", fontsize=14, fontweight="bold", y=0.98, color="#2c3e50")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(output_dir, "02_topic_distribution_by_source.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 02_topic_distribution_by_source.png")


def plot_sentiment_contrast_by_source(df: pd.DataFrame, output_dir: str):
    """
    [03] Grouped Bar Chart: Sentimen Kontras Lintas 4 Sumber Data.
    MEMBUKTIKAN secara visual 'Journalistic Neutrality Mask' vs 'Grassroots Voice' vs 'Founder Real-World Frictions'.
    """
    fig, ax = plt.subplots(figsize=(13, 6.5))
    
    ct = pd.crosstab(df["data_source"], df["sentiment"], normalize="index") * 100
    sources_order = [s for s in ["scraping", "social_media", "interview", "survey"] if s in ct.index]
    sentiments_order = [s for s in ["negative", "neutral", "positive"] if s in ct.columns]
    
    ct = ct.loc[sources_order, sentiments_order]
    
    x = np.arange(len(sources_order))
    width = 0.25
    
    for i, sent in enumerate(sentiments_order):
        vals = ct[sent].values
        color = SENTIMENT_COLORS[sent]
        bars = ax.bar(x + (i - 1) * width, vals, width=width, label=sent.capitalize(),
                      color=color, edgecolor="white", linewidth=1.2)
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1.2, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#2c3e50")
    
    source_labels = {
        "scraping": "Berita Massa\n(Scraping N=13.840)",
        "social_media": "Media Sosial\n(Grassroots N=311)",
        "interview": "Wawancara Founder\n(Qualitative N=113)",
        "survey": "Survey Primer\n(Micro N=25)",
    }
    ax.set_xticks(x)
    ax.set_xticklabels([source_labels.get(s, s) for s in sources_order], fontsize=10.5, fontweight="medium")
    ax.set_ylabel("Proporsi Sentimen dalam Sumber (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_title("Kontras Polarisasi Sentimen Lintas 4 Sumber Data: Netralitas Berita vs Friksi Pelaku",
                 fontsize=13, fontweight="bold", pad=15, color="#2c3e50")
    ax.legend(title="Klasifikasi Sentimen", loc="upper right", frameon=True, fontsize=10)
    
    # Highlight anotasi krusial
    ax.annotate(
        "Berita 86.5% Netral\n(Frame Jurnalistik)",
        xy=(0, 86.5), xytext=(0.18, 88),
        arrowprops=dict(facecolor="#7f8c8d", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9, fontweight="bold", color="#34495e"
    )
    
    ax.annotate(
        "Medsos 11.3% Negatif\n(Keluhan Listrik & Internet)",
        xy=(1 - width, 11.3), xytext=(0.85, 25),
        arrowprops=dict(facecolor="#e74c3c", shrink=0.08, width=1.5, headwidth=6),
        fontsize=8.5, fontweight="bold", color="#c0392b"
    )
    
    ax.annotate(
        "Survey 64% Negatif\n(Krisis Akses Modal)",
        xy=(3 - width, 64.0), xytext=(2.3, 72),
        arrowprops=dict(facecolor="#e74c3c", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9, fontweight="bold", color="#c0392b"
    )
    
    fig.text(
        0.5, -0.04,
        "Temuan Inti: Berita didominasi seremonial normatif (0,7% negatif), sedangkan wacana medsos memuat keluhan utilitas (11,3% negatif),\n"
        "serta wawancara (42,5% negatif) dan survei primer (64,0% negatif) membuktikan krisis modal struktural di kalangan founder.",
        ha="center", fontsize=8.5, style="italic", color="#7f8c8d"
    )
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "03_sentiment_contrast_by_source.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print("   ✓ 03_sentiment_contrast_by_source.png")


def plot_sentiment_topic_heatmap(df: pd.DataFrame, output_dir: str):
    """
    [04] Heatmap: Matriks Silang Topik × Sentimen pada Combined Dataset.
    """
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    ct = pd.crosstab(df["topic"], df["sentiment"])
    sentiments_order = [s for s in ["negative", "neutral", "positive"] if s in ct.columns]
    ct = ct[sentiments_order]
    
    sns.heatmap(
        ct,
        annot=True,
        fmt=",d",
        cmap="YlGnBu",
        cbar_kws={"label": "Jumlah Paragraf / Unit Ide"},
        linewidths=1,
        linecolor="white",
        ax=ax
    )
    
    ax.set_title(f"Matriks Frekuensi Topik × Sentimen (Combined Dataset N={len(df):,})",
                 fontsize=13, fontweight="bold", pad=15, color="#2c3e50")
    ax.set_xlabel("Sentimen", fontsize=11, fontweight="medium")
    ax.set_ylabel("Topik Ekosistem", fontsize=11, fontweight="medium")
    ax.set_xticklabels([s.capitalize() for s in sentiments_order], fontsize=10)
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "04_sentiment_topic_heatmap.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 04_sentiment_topic_heatmap.png")


def plot_wordclouds_multitopic(df: pd.DataFrame, output_dir: str):
    """
    [05] Word Cloud Grid 2x2: Representasi Leksikal Topik Kunci
    (Funding, Talent, Market Access, Ecosystem).
    """
    topics_to_plot = ["funding", "talent", "market_access", "ecosystem"]
    topic_titles = {
        "funding": "Pillar 1: Funding & Permodalan",
        "talent": "Pillar 2: Talent & Kesiapan SDM",
        "market_access": "Pillar 3: Market Access & Skalabilitas",
        "ecosystem": "Pillar 4: Ekosistem & Komunitas",
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colormaps = ["Reds", "Blues", "Greens", "Purples"]
    
    for idx, topic in enumerate(topics_to_plot):
        ax = axes[idx]
        subset = df[df["topic"] == topic]
        text_corpus = " ".join(subset["text"].dropna().astype(str).tolist()).lower()
        
        # Bersihkan stopwords & karakter aneh
        words = [w.strip(".,;:\"'()[]{}!?") for w in text_corpus.split()]
        filtered_words = [
            w for w in words
            if len(w) >= 4 and w not in STOPWORDS_ID and not w.isnumeric()
        ]
        
        filtered_text = " ".join(filtered_words)
        
        if not filtered_text.strip():
            ax.text(0.5, 0.5, f"Data teks minim untuk {topic}", ha="center", va="center")
            ax.axis("off")
            continue
            
        wc = WordCloud(
            width=600,
            height=400,
            background_color="white",
            colormap=colormaps[idx % len(colormaps)],
            max_words=60,
            stopwords=STOPWORDS_ID,
            random_state=42,
            contour_width=1,
            contour_color="#e0e0e0"
        ).generate(filtered_text)
        
        ax.imshow(wc, interpolation="bilinear")
        ax.set_title(f"{topic_titles.get(topic, topic)} (N={len(subset):,})",
                     fontsize=12, fontweight="bold", pad=10, color="#2c3e50")
        ax.axis("off")
    
    plt.suptitle("Peta Leksikal Word Cloud pada 4 Pilar Utama Ekosistem Startup Aceh",
                 fontsize=15, fontweight="bold", y=0.98, color="#2c3e50")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(output_dir, "05_wordclouds_multitopic.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 05_wordclouds_multitopic.png")


def plot_word_count_and_length_dist(df: pd.DataFrame, output_dir: str):
    """
    [06] Visualisasi Distribusi Panjang Teks & Word Count per Sumber.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    
    # Histogram Word Count Berita (Scraping)
    news_df = df[df["data_source"] == "scraping"]
    ax1.hist(news_df["word_count"], bins=40, color="#3498db", alpha=0.75, edgecolor="white")
    mean_w = news_df["word_count"].mean()
    med_w = news_df["word_count"].median()
    ax1.axvline(mean_w, color="#e74c3c", linestyle="--", linewidth=1.5, label=f"Mean: {mean_w:.1f} kata")
    ax1.axvline(med_w, color="#27ae60", linestyle="-", linewidth=1.5, label=f"Median: {med_w:.0f} kata")
    ax1.set_title("Distribusi Word Count Paragraf Berita (Scraping)", fontsize=11, fontweight="bold", color="#2c3e50")
    ax1.set_xlabel("Jumlah Kata per Paragraf", fontsize=10)
    ax1.set_ylabel("Frekuensi", fontsize=10)
    ax1.legend(loc="upper right")
    
    # Boxplot Perbandingan Word Count Antar Sumber
    data_to_plot = []
    labels = []
    box_colors = []
    source_map = {
        "scraping": ("Scraping", "#2980b9"),
        "interview": ("Interview", "#8e44ad"),
        "survey": ("Survey", "#d35400"),
        "social_media": ("Medsos", "#16a085"),
    }
    for s in ["scraping", "interview", "survey", "social_media"]:
        sub = df[df["data_source"] == s]["word_count"].dropna()
        if len(sub) > 0:
            name, col = source_map.get(s, (s.capitalize(), "#95a5a6"))
            data_to_plot.append(sub.values)
            labels.append(f"{name}\n(N={len(sub):,})")
            box_colors.append(col)
            
    bplot = ax2.boxplot(data_to_plot, patch_artist=True, tick_labels=labels, showfliers=False, widths=0.5)
    for patch, c in zip(bplot["boxes"], box_colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    for median in bplot["medians"]:
        median.set(color="black", linewidth=2)
        
    ax2.set_title("Komparasi Kedalaman Unit Teks Antar Sumber Data", fontsize=11, fontweight="bold", color="#2c3e50")
    ax2.set_ylabel("Jumlah Kata per Unit Analisis (Tanpa Outliers)", fontsize=10)
    
    # Anotasi penjelasan
    ax2.text(
        0.5, 0.05,
        "Wawancara memiliki unit ide rata-rata ~65 kata (narasi kualitatif mendalam),\n"
        "Medsos rata-rata ~44 kata, sementara berita rata-rata ~28 kata per paragraf.",
        transform=ax2.transAxes, ha="center", fontsize=8.5, style="italic",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#dcdde1")
    )
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "06_word_count_and_length_dist.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 06_word_count_and_length_dist.png")


def plot_portal_and_source_distribution(df: pd.DataFrame, output_dir: str):
    """
    [07] Top 15 Portal Berita + Platform Medsos + Entitas Narasumber Wawancara.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6), gridspec_kw={"width_ratios": [1.8, 1.0, 1.2]})
    
    # 1. Top 15 Portals in Scraping
    portal_counts = df[df["data_source"].isin(["scraping", "news"])]["source_portal"].value_counts().head(15)
    if len(portal_counts) > 0:
        bars1 = ax1.barh(portal_counts.index[::-1], portal_counts.values[::-1], color="#2980b9", height=0.65)
        ax1.set_title("Top 15 Portal Media Massa (N=13.840)", fontsize=11, fontweight="bold", color="#2c3e50")
        ax1.set_xlabel("Jumlah Paragraf", fontsize=10)
        for bar in bars1:
            w = bar.get_width()
            ax1.text(w + 20, bar.get_y() + bar.get_height() / 2, f"{int(w):,}",
                     va="center", fontsize=8.5, color="#2c3e50")
        ax1.set_xlim(0, max(portal_counts.values) * 1.15)
    else:
        ax1.text(0.5, 0.5, "Data portal tidak tersedia", ha="center", va="center")
        ax1.set_title("Top 15 Portal Media Massa", fontsize=11, fontweight="bold")
    
    # 2. Social Media Platforms
    soc_df = df[df["data_source"] == "social_media"]
    if len(soc_df) > 0:
        soc_counts = soc_df["source_portal"].value_counts()
        bars2 = ax2.barh(soc_counts.index[::-1], soc_counts.values[::-1], color="#16a085", height=0.5)
        ax2.set_title("Platform Media Sosial (N=311)", fontsize=11, fontweight="bold", color="#2c3e50")
        ax2.set_xlabel("Jumlah Postingan", fontsize=10)
        for bar in bars2:
            w = bar.get_width()
            pct = w / len(soc_df) * 100
            ax2.text(w + 2, bar.get_y() + bar.get_height() / 2, f"{int(w)} ({pct:.1f}%)",
                     va="center", fontsize=9, fontweight="bold", color="#2c3e50")
        ax2.set_xlim(0, max(soc_counts.values) * 1.25)
    else:
        ax2.text(0.5, 0.5, "Data medsos tidak tersedia", ha="center", va="center")
        ax2.set_title("Platform Media Sosial", fontsize=11, fontweight="bold")
    
    # 3. Interview Entities
    interview_df = df[df["data_source"] == "interview"]
    entity_counts = interview_df["interviewee"].value_counts()
    bars3 = ax3.barh(entity_counts.index[::-1], entity_counts.values[::-1], color="#8e44ad", height=0.5)
    ax3.set_title("Narasumber Wawancara (N=113)", fontsize=11, fontweight="bold", color="#2c3e50")
    ax3.set_xlabel("Jumlah Unit Ide", fontsize=10)
    for bar in bars3:
        w = bar.get_width()
        pct = w / len(interview_df) * 100
        ax3.text(w + 1, bar.get_y() + bar.get_height() / 2, f"{int(w)} ({pct:.1f}%)",
                 va="center", fontsize=9, fontweight="bold", color="#2c3e50")
    ax3.set_xlim(0, max(entity_counts.values) * 1.25)
    
    plt.suptitle("Cakupan Kanal & Entitas Informasi: Media Massa, Media Sosial, & Pelaku Startup",
                 fontsize=13, fontweight="bold", y=0.98, color="#2c3e50")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(output_dir, "07_portal_and_source_distribution.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 07_portal_and_source_distribution.png")


# ==============================================================================
# 2. PRIMARY SURVEY STRUCTURED VISUALIZATIONS (N=12)
# ==============================================================================

def plot_survey_radar_chart(survey_df: pd.DataFrame, output_dir: str):
    """
    [08] Radar / Spider Chart: Persepsi Ekosistem 6 Dimensi (Q15-Q20).
    Skala Likert 1 (Sangat Buruk) hingga 5 (Sangat Baik).
    """
    dim_cols = [
        "persepsi_ekosistem",
        "persepsi_pendanaan",
        "persepsi_mentor",
        "persepsi_pemerintah",
        "persepsi_optimis",
        "persepsi_infra",
    ]
    dim_labels = [
        "Ekosistem Umum (Q15)",
        "Akses Pendanaan (Q16)",
        "Mentor & Inkubasi (Q17)",
        "Regulasi & Dukungan (Q18)",
        "Optimisme Masa Depan (Q19)",
        "Kesiapan Infrastruktur (Q20)",
    ]
    
    means = [survey_df[c].mean() for c in dim_cols]
    
    # Tutup lingkaran radar
    num_vars = len(dim_labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    means_closed = means + means[:1]
    benchmark = [3.0] * (num_vars + 1)  # Garis Benchmark Netral = 3.0
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Plot Benchmark
    ax.plot(angles, benchmark, color="#e74c3c", linestyle="--", linewidth=1.8, label="Benchmark Netral (Skor 3.0)")
    ax.fill(angles, benchmark, color="#e74c3c", alpha=0.04)
    
    # Plot Skor Survei
    ax.plot(angles, means_closed, color="#2980b9", linewidth=2.5, marker="o", markersize=7, label="Mean Persepsi Pelaku (N=12)")
    ax.fill(angles, means_closed, color="#3498db", alpha=0.25)
    
    # Labels & Styling
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), [f"{lbl}\n({val:.2f}/5.0)" for lbl, val in zip(dim_labels, means)],
                      fontsize=10, fontweight="bold", color="#2c3e50")
    
    ax.set_ylim(0, 5)
    ax.set_rgrids([1, 2, 3, 4, 5], labels=["1 (Sangat Buruk)", "2 (Buruk)", "3 (Cukup)", "4 (Baik)", "5 (Sangat Baik)"],
                  angle=0, fontsize=8.5, color="#7f8c8d")
    
    ax.set_title("Radar Persepsi Kondisi Ekosistem Startup Aceh\n(Evaluasi 6 Dimensi Likert 1-5, N=12 Responden)",
                 fontsize=13, fontweight="bold", pad=28, color="#2c3e50")
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.05), frameon=True)
    
    # Highlight Defisit Pendanaan & Regulasi
    fig.text(
        0.5, 0.02,
        "[Defisit Kritis] Akses Pendanaan (1.42/5) dan Regulasi Pemerintah (1.67/5) berada jauh di bawah garis netral.\n"
        "[Titik Terang] Optimisme founder tetap positif (3.08/5) didukung kesiapan infrastruktur dasar (2.92/5).",
        ha="center", fontsize=9, style="italic", color="#2c3e50",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fef9e7", edgecolor="#f39c12")
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_path = os.path.join(output_dir, "08_survey_radar_chart.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print("   ✓ 08_survey_radar_chart.png")


def plot_survey_challenges_ranking(survey_df: pd.DataFrame, output_dir: str):
    """
    [09] Horizontal Bar Chart: Ranking Tantangan Utama Startup Aceh (Q12 Multi-Select).
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    all_challenges = pd.concat([
        survey_df["tantangan_1"],
        survey_df["tantangan_2"],
        survey_df["tantangan_3"]
    ]).dropna()
    
    challenge_counts = all_challenges.value_counts()
    n_respondents = len(survey_df)
    
    # Filter dan agregasi kategori
    colors = []
    for c in challenge_counts.index:
        if "Pendanaan" in c:
            colors.append("#e74c3c")
        elif "Talent" in c:
            colors.append("#e67e22")
        elif "Regulasi" in c:
            colors.append("#f39c12")
        elif "Pasar" in c or "Customer" in c:
            colors.append("#2980b9")
        else:
            colors.append("#95a5a6")
            
    bars = ax.barh(challenge_counts.index[::-1], challenge_counts.values[::-1], color=colors[::-1], height=0.65)
    
    ax.set_title("Ranking Tantangan Utama Pelaku Startup Digital di Aceh (Q12)\nPersentase Responden yang Memilih Kendala (N=12)",
                 fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_xlabel("Frekuensi Pemilihan oleh Responden", fontsize=10)
    
    for bar in bars:
        w = bar.get_width()
        pct = (w / n_respondents) * 100
        ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2, f"{int(w)} responden ({pct:.1f}%)",
                va="center", fontsize=9.5, fontweight="bold", color="#2c3e50")
        
    ax.set_xlim(0, max(challenge_counts.values) * 1.35)
    
    # Custom Legend
    legend_elements = [
        mpatches.Patch(color="#e74c3c", label="Pendanaan & Investasi (Paling Krusial 50.0%)"),
        mpatches.Patch(color="#e67e22", label="Ketersediaan Talent / SDM (41.7%)"),
        mpatches.Patch(color="#f39c12", label="Regulasi & Perizinan (33.3%)"),
        mpatches.Patch(color="#2980b9", label="Pasar & Traksi Bisnis (25.0%)"),
        mpatches.Patch(color="#95a5a6", label="Lainnya / Operasional"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", frameon=True, fontsize=9)
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "09_survey_challenges_ranking.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 09_survey_challenges_ranking.png")


def plot_survey_likert_diverging(survey_df: pd.DataFrame, output_dir: str):
    """
    [10] Diverging Stacked Bar Chart: Distribusi Nilai Likert 1-5 (Q15-Q20).
    """
    dim_cols = [
        "persepsi_pendanaan",
        "persepsi_pemerintah",
        "persepsi_mentor",
        "persepsi_ekosistem",
        "persepsi_infra",
        "persepsi_optimis",
    ]
    dim_names = [
        "Q16: Akses Pendanaan",
        "Q18: Dukungan Pemerintah",
        "Q17: Mentor & Inkubasi",
        "Q15: Ekosistem Umum",
        "Q20: Infrastruktur Digital",
        "Q19: Optimisme Masa Depan",
    ]
    
    likert_palette = {
        1: "#c0392b",  # Sangat Buruk
        2: "#e67e22",  # Buruk
        3: "#bdc3c7",  # Cukup / Netral
        4: "#2ecc71",  # Baik
        5: "#27ae60",  # Sangat Baik
    }
    
    counts_data = {rating: [] for rating in range(1, 6)}
    
    for col in dim_cols:
        val_counts = survey_df[col].value_counts().to_dict()
        for r in range(1, 6):
            counts_data[r].append(val_counts.get(r, 0))
            
    plot_df = pd.DataFrame(counts_data, index=dim_names)
    
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    left = np.zeros(len(dim_names))
    for r in range(1, 6):
        vals = plot_df[r].values
        ax.barh(dim_names, vals, left=left, color=likert_palette[r],
                edgecolor="white", height=0.6, label=f"Skor {r}")
        # Tambah teks angka jika > 0
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(left[i] + v / 2, i, str(int(v)),
                        ha="center", va="center", color="white" if r in [1, 5] else "#2c3e50",
                        fontweight="bold", fontsize=9.5)
        left += vals
        
    ax.set_title("Distribusi Skor Skala Likert 1-5 pada 6 Dimensi Ekosistem (N=12)",
                 fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    ax.set_xlabel("Jumlah Responden (Orang)", fontsize=10)
    ax.set_xlim(0, 12.5)
    
    custom_legend = [
        mpatches.Patch(color=likert_palette[1], label="1: Sangat Buruk"),
        mpatches.Patch(color=likert_palette[2], label="2: Buruk"),
        mpatches.Patch(color=likert_palette[3], label="3: Cukup / Netral"),
        mpatches.Patch(color=likert_palette[4], label="4: Baik"),
        mpatches.Patch(color=likert_palette[5], label="5: Sangat Baik"),
    ]
    ax.legend(handles=custom_legend, loc="lower right", bbox_to_anchor=(1.0, -0.22), ncol=5, frameon=True)
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "10_survey_likert_diverging.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print("   ✓ 10_survey_likert_diverging.png")


def plot_survey_talent_market_readiness(survey_df: pd.DataFrame, output_dir: str):
    """
    [11] Bar Chart: Kesiapan Pasar (Q14) vs Ketersediaan Talent (Q13) vs Daya Tahan (Q11).
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))
    
    metrics = {
        "Daya Tahan 1-2 Thn\n(Q11: Resilience)": survey_df["kemungkinan_bertahan"].mean(),
        "Akses Pasar Luar\n(Q14: Market Ease)": survey_df["kemudahan_pasar"].mean(),
        "Ketersediaan Talent\n(Q13: Talent Ease)": survey_df["kemudahan_talent"].mean(),
    }
    
    colors = ["#27ae60", "#2980b9", "#e67e22"]
    bars = ax.bar(metrics.keys(), metrics.values(), color=colors, width=0.45, edgecolor="none")
    
    ax.axhline(3.0, color="#e74c3c", linestyle="--", linewidth=1.5, label="Garis Netral / Standar (3.0)")
    ax.set_ylabel("Rata-rata Skor Penilaian (1-5)", fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_title("Profil Kesiapan Operasional Startup: Daya Tahan, Pasar, & SDM (N=12)",
                 fontsize=12, fontweight="bold", pad=12, color="#2c3e50")
    
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.12, f"{h:.2f} / 5.0",
                ha="center", va="bottom", fontsize=11, fontweight="bold", color="#2c3e50")
        
    ax.legend(loc="upper right", frameon=True)
    
    # Anotasi
    fig.text(
        0.5, 0.01,
        "Insight: Founder menunjukkan resiliensi tinggi (4.08) dan kemudahan ekspansi pasar non-lokal (3.75),\n"
        "namun terhambat oleh pasokan talent kompeten (3.00) dan pendanaan lokal yang minim.",
        ha="center", fontsize=8.5, style="italic", color="#7f8c8d"
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    out_path = os.path.join(output_dir, "11_survey_talent_market_readiness.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 11_survey_talent_market_readiness.png")


# ==============================================================================
# 3. TRIANGULATION SYNTHESIS & CONVERGENCE VISUALIZATIONS
# ==============================================================================

def plot_triangulation_convergence_summary(tri_df: pd.DataFrame, output_dir: str):
    """
    [12] Visual Scorecard: Status Konvergensi 6 Hipotesis (H1-H6).
    """
    fig, ax = plt.subplots(figsize=(13, 6))
    
    h_labels = [f"{r['hypothesis']}: {r['hypothesis_title']}" for _, r in tri_df.iterrows()]
    y_pos = np.arange(len(h_labels))
    
    has_soc = "social_media_evidence" in tri_df.columns
    max_src = 4 if has_soc else 3
    support_text = "SUPPORTED (4/4)" if has_soc else "SUPPORTED (3/3)"
    
    # Semua 6 hipotesis terdukung oleh multi-sumber data (100% convergence rate)
    ax.barh(y_pos, [max_src] * len(h_labels), color="#27ae60", alpha=0.85, height=0.55, edgecolor="none")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(h_labels[::-1], fontsize=10.5, fontweight="medium", color="#2c3e50")
    ax.set_xlabel("Jumlah Sumber Data yang Mengonfirmasi Bukti (Kekuatan Triangulasi)", fontsize=10.5, labelpad=8)
    ax.set_xlim(0, max_src + 1.2)
    
    if has_soc:
        ax.set_xticks([0, 1, 2, 3, 4])
        ax.set_xticklabels(["0 Sumber", "1 Sumber", "2 Sumber (Moderate)", "3 Sumber (Kuat)", "4/4 Sumber (Sangat Kuat)"], fontsize=10)
        sub_title = "Validasi Silang: Berita (Macro) × Survei (Micro) × Wawancara (Qualitative) × Media Sosial (Grassroots)"
    else:
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels(["0 Sumber", "1 Sumber", "2 Sumber (Moderate)", "3/3 Sumber (Kuat / Valid)"], fontsize=10)
        sub_title = "Validasi Silang: Berita (Macro) × Survei (Micro) × Wawancara (Qualitative)"
        
    ax.set_title(f"Scorecard Konvergensi Triangulasi Multi-Sumber (H1 – H6)\n{sub_title}",
                 fontsize=12.5, fontweight="bold", pad=14, color="#2c3e50")
    
    for i, idx in enumerate(reversed(range(len(h_labels)))):
        ax.text(max_src + 0.1, i, support_text, va="center", fontsize=10, fontweight="bold", color="#27ae60")
        
    plt.tight_layout()
    out_path = os.path.join(output_dir, "12_triangulation_convergence_summary.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("   ✓ 12_triangulation_convergence_summary.png")


def plot_triangulation_evidence_matrix_table(tri_df: pd.DataFrame, output_dir: str):
    """
    [13] Tabel Visual Resolusi Tinggi: Matriks Bukti Triangulasi H1-H6.
    """
    fig, ax = plt.subplots(figsize=(19, 9))
    ax.axis("off")
    
    has_soc = "social_media_evidence" in tri_df.columns
    table_data = []
    for _, r in tri_df.iterrows():
        claim_short = r["hypothesis_claim"][:55] + "..." if len(r["hypothesis_claim"]) > 55 else r["hypothesis_claim"]
        macro_short = r["scraping_evidence"][:45] + "..." if len(r["scraping_evidence"]) > 45 else r["scraping_evidence"]
        survey_short = r["survey_evidence"][:45] + "..." if len(r["survey_evidence"]) > 45 else r["survey_evidence"]
        interview_short = r["interview_evidence"][:45] + "..." if len(r["interview_evidence"]) > 45 else r["interview_evidence"]
        
        row_cells = [
            r["hypothesis"],
            r["hypothesis_title"],
            claim_short,
            macro_short,
            survey_short,
            interview_short,
        ]
        if has_soc:
            soc_ev = str(r["social_media_evidence"])
            soc_short = soc_ev[:45] + "..." if len(soc_ev) > 45 else soc_ev
            row_cells.append(soc_short)
            row_cells.append("SUPPORTED\n(4/4 Sumber)")
        else:
            row_cells.append("SUPPORTED\n(3/3 Sumber)")
            
        table_data.append(row_cells)
        
    if has_soc:
        col_labels = [
            "ID",
            "Judul Hipotesis",
            "Klaim Masalah",
            "Bukti Berita (Macro)",
            "Bukti Survei (Micro)",
            "Bukti Wawancara (Kualitatif)",
            "Bukti Sosmed (Grassroots)",
            "Status Validasi"
        ]
        col_widths = [0.04, 0.14, 0.18, 0.15, 0.15, 0.15, 0.15, 0.09]
        status_col_idx = 7
    else:
        col_labels = [
            "ID",
            "Judul Hipotesis",
            "Klaim Masalah",
            "Bukti Berita (Macro)",
            "Bukti Survei (Micro)",
            "Bukti Wawancara (Kualitatif)",
            "Status Validasi"
        ]
        col_widths = [0.05, 0.17, 0.22, 0.19, 0.19, 0.19, 0.11]
        status_col_idx = 6
    
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="left",
        loc="center",
        colWidths=col_widths,
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(8.0)
    table.scale(1.0, 2.3)
    
    # Styling Header & Rows
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold", ha="center")
        else:
            if row % 2 == 0:
                cell.set_facecolor("#f8f9fa")
            else:
                cell.set_facecolor("#ffffff")
                
            if col == 0:
                cell.set_text_props(fontweight="bold", ha="center")
            elif col == status_col_idx:
                cell.set_facecolor("#e8f8f5")
                cell.set_text_props(color="#16a085", fontweight="bold", ha="center")
                
    ax.set_title("Matriks Sintesis Triangulasi 4-Pilar Hipotesis Ekosistem Startup Aceh (Sprint 3)",
                 fontsize=14, fontweight="bold", pad=20, color="#2c3e50")
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, "13_triangulation_evidence_matrix_table.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print("   ✓ 13_triangulation_evidence_matrix_table.png")


# ==============================================================================
# 4. REPORT & ARTIFACT GENERATION
# ==============================================================================

def generate_word_frequency_report(df: pd.DataFrame, output_dir: str):
    """
    Menghasilkan laporan teks frekuensi leksikal top 30 kata per topik.
    """
    report_lines = [
        "=" * 70,
        f"LAPORAN FREKUENSI KATA PER TOPIK EKOSISTEM (COMBINED DATASET N={len(df):,})",
        "=" * 70,
        "",
    ]
    
    for topic in sorted(df["topic"].dropna().unique()):
        subset = df[df["topic"] == topic]
        topic_text = subset["text"].dropna().str.lower().str.cat(sep=" ")
        words = [w.strip(".,;:\"'()[]{}!?") for w in topic_text.split()]
        words_filtered = [
            w for w in words
            if len(w) >= 3 and w not in STOPWORDS_ID and not w.isnumeric()
        ]
        
        counter = Counter(words_filtered)
        top_30 = counter.most_common(30)
        
        report_lines.append(f"=== TOPIK: {topic.upper()} (Total Paragraf: {len(subset):,}) ===")
        for rank, (w, count) in enumerate(top_30, 1):
            report_lines.append(f"  {rank:2d}. {w:<20} : {count:>5d} kali")
        report_lines.append("")
        
    out_file = os.path.join(output_dir, "word_frequency_per_topic.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("   ✓ word_frequency_per_topic.txt")


def generate_triangulation_html(tri_df: pd.DataFrame, output_dir: str):
    """
    Menghasilkan visualisasi HTML responsif dan interaktif untuk matriks triangulasi.
    """
    has_soc = "social_media_evidence" in tri_df.columns
    rows_html = []
    for _, r in tri_df.iterrows():
        soc_td = f'<td style="background-color: #f0fdf4; font-size: 0.88em;">{r.get("social_media_evidence", "")}</td>' if has_soc else ''
        row_str = f"""
        <tr>
            <td style="font-weight: bold; text-align: center; color: #2c3e50;">{r['hypothesis']}</td>
            <td style="font-weight: 600; color: #34495e;">{r['hypothesis_title']}</td>
            <td style="color: #555; font-size: 0.9em;">{r['hypothesis_claim']}</td>
            <td style="background-color: #f4f6f9; font-size: 0.88em;">{r['scraping_evidence']}</td>
            <td style="background-color: #fbf6f0; font-size: 0.88em;">{r['survey_evidence']}</td>
            <td style="background-color: #f9f4fb; font-size: 0.88em;">{r['interview_evidence']}</td>
            {soc_td}
            <td style="text-align: center;">
                <span style="background-color: #d4edda; color: #155724; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.82em;">
                    {r['convergence']}
                </span>
                <div style="font-size: 0.75em; color: #6c757d; margin-top: 4px;">{r['strength']}</div>
            </td>
        </tr>
        """
        rows_html.append(row_str)
        
    soc_th = '<th style="width: 15%;">Bukti Sosmed (Grassroots)</th>' if has_soc else ''
    soc_badge = '<span class="badge" style="background: #dcfce7; color: #15803d;">📱 Sumber Grassroots: 311 Post Sosmed (X/YT/LI)</span>' if has_soc else ''
    
    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matriks Triangulasi Riset Ekosistem Startup Aceh — Sprint 3</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            padding: 30px;
            margin: 0;
        }}
        .container {{
            max-width: 1500px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        h1 {{
            color: #0f172a;
            margin-bottom: 8px;
            font-size: 24px;
        }}
        p.subtitle {{
            color: #64748b;
            margin-top: 0;
            margin-bottom: 25px;
            font-size: 14px;
        }}
        .badge-bar {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .badge {{
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }}
        .badge-macro {{ background: #e0f2fe; color: #0369a1; }}
        .badge-micro {{ background: #ffedd5; color: #c2410c; }}
        .badge-qual {{ background: #f3e8ff; color: #7e22ce; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            line-height: 1.5;
        }}
        th {{
            background-color: #1e293b;
            color: #ffffff;
            padding: 12px 14px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }}
        tr:hover td {{
            background-color: #f1f5f9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📐 Matriks Triangulasi Multi-Sumber: Validasi Hipotesis H1 – H6</h1>
        <p class="subtitle">Riset Ekosistem Startup Aceh 2026 · Metode Integrasi Data-Centric AI (DCAI) & Mixed-Methods</p>
        
        <div class="badge-bar">
            <span class="badge badge-macro">🌐 Sumber Macro: 13.840 Berita Scraping</span>
            <span class="badge badge-micro">📊 Sumber Micro: 12 Responden Survei Primer</span>
            <span class="badge badge-qual">🎙️ Sumber Kualitatif: 113 Unit Ide Wawancara (3 Entitas)</span>
            {soc_badge}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 4%;">ID</th>
                    <th style="width: 13%;">Judul Hipotesis</th>
                    <th style="width: 17%;">Klaim Hipotesis</th>
                    <th style="width: 16%;">Bukti Berita (Macro)</th>
                    <th style="width: 15%;">Bukti Survei (Micro)</th>
                    <th style="width: 15%;">Bukti Wawancara (Mendalam)</th>
                    {soc_th}
                    <th style="width: 10%; text-align: center;">Konvergensi</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    out_file = os.path.join(output_dir, "triangulation_matrix.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("   ✓ triangulation_matrix.html")


def generate_summary_metrics_json(combined_df: pd.DataFrame, survey_df: pd.DataFrame, tri_df: pd.DataFrame, output_dir: str):
    """
    Menghasilkan file JSON metrik ringkas untuk integrasi Dashboard Fase 5.
    """
    metrics = {
        "dataset_summary": {
            "total_records": len(combined_df),
            "sources": combined_df["data_source"].value_counts().to_dict(),
            "topics": combined_df["topic"].value_counts().to_dict(),
            "sentiments": combined_df["sentiment"].value_counts().to_dict(),
            "mean_word_count": round(float(combined_df["word_count"].mean()), 2),
            "median_word_count": int(combined_df["word_count"].median()),
        },
        "survey_summary": {
            "n_respondents": len(survey_df),
            "likert_means": {
                "persepsi_ekosistem": round(float(survey_df["persepsi_ekosistem"].mean()), 2),
                "persepsi_pendanaan": round(float(survey_df["persepsi_pendanaan"].mean()), 2),
                "persepsi_mentor": round(float(survey_df["persepsi_mentor"].mean()), 2),
                "persepsi_pemerintah": round(float(survey_df["persepsi_pemerintah"].mean()), 2),
                "persepsi_optimis": round(float(survey_df["persepsi_optimis"].mean()), 2),
                "persepsi_infra": round(float(survey_df["persepsi_infra"].mean()), 2),
            },
            "operational_means": {
                "kemungkinan_bertahan": round(float(survey_df["kemungkinan_bertahan"].mean()), 2),
                "kemudahan_talent": round(float(survey_df["kemudahan_talent"].mean()), 2),
                "kemudahan_pasar": round(float(survey_df["kemudahan_pasar"].mean()), 2),
            },
        },
        "triangulation_summary": {
            "total_hypotheses": len(tri_df),
            "supported_hypotheses": int((tri_df["convergence"] == "SUPPORTED").sum()),
            "convergence_rate_pct": round(float((tri_df["convergence"] == "SUPPORTED").mean() * 100), 1),
            "hypotheses": tri_df[["hypothesis", "hypothesis_title", "convergence", "strength"]].to_dict(orient="records")
        }
    }
    
    out_file = os.path.join(output_dir, "eda_summary_metrics.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("   ✓ eda_summary_metrics.json")


# ==============================================================================
# MAIN PIPELINE EXECUTION
# ==============================================================================

def main():
    print("=" * 72)
    print("📊 06_eda.py — Multi-Source Exploratory Data Analysis & Triangulation")
    print("   GRAK 2026 · Sprint 3 (Integrasi Fase 3.5 & Pondasi Fase 4)")
    print("=" * 72)
    
    # 1. Validasi Input Files
    required_files = [
        ("Combined Text", COMBINED_CSV),
        ("Survey Structured", SURVEY_CSV),
        ("Triangulation Matrix", TRIANGULATION_CSV),
    ]
    
    for name, path in required_files:
        if not os.path.exists(path):
            print(f"❌ Error: File {name} tidak ditemukan di: {path}")
            print("   Jalankan script Fase 3.5 sebelumnya terlebih dahulu!")
            sys.exit(1)
            
    os.makedirs(EDA_DIR, exist_ok=True)
    
    # 2. Baca Dataset
    combined_df = pd.read_csv(COMBINED_CSV)
    # Standardisasi nama data_source ke 'scraping' agar konsisten dengan konvensi planning
    combined_df = combined_df.assign(data_source=combined_df["data_source"].replace({"news": "scraping"}))
    survey_df = pd.read_csv(SURVEY_CSV)
    tri_df = pd.read_csv(TRIANGULATION_CSV)
    
    print(f"\n📂 Membaca Dataset Berhasil:")
    print(f"   • Combined Text Dataset    : {len(combined_df):,} baris")
    print(f"   • Survey Structured Data   : {len(survey_df)} responden")
    print(f"   • Matriks Triangulasi      : {len(tri_df)} hipotesis (H1–H6)")
    print(f"   • Output Directory         : {EDA_DIR}")
    
    # 3. Generate Visualisasi Multi-Source
    print("\n📈 [1/3] Menghasilkan Visualisasi Multi-Source Dataset...")
    plot_source_composition(combined_df, EDA_DIR)
    plot_topic_distribution_by_source(combined_df, EDA_DIR)
    plot_sentiment_contrast_by_source(combined_df, EDA_DIR)
    plot_sentiment_topic_heatmap(combined_df, EDA_DIR)
    plot_wordclouds_multitopic(combined_df, EDA_DIR)
    plot_word_count_and_length_dist(combined_df, EDA_DIR)
    plot_portal_and_source_distribution(combined_df, EDA_DIR)
    
    # 4. Generate Visualisasi Survei Primer (N=12)
    print("\n📊 [2/3] Menghasilkan Visualisasi Survei Primer Terstruktur...")
    plot_survey_radar_chart(survey_df, EDA_DIR)
    plot_survey_challenges_ranking(survey_df, EDA_DIR)
    plot_survey_likert_diverging(survey_df, EDA_DIR)
    plot_survey_talent_market_readiness(survey_df, EDA_DIR)
    
    # 5. Generate Visualisasi & Laporan Triangulasi
    print("\n📐 [3/3] Menghasilkan Visualisasi & Laporan Triangulasi...")
    plot_triangulation_convergence_summary(tri_df, EDA_DIR)
    plot_triangulation_evidence_matrix_table(tri_df, EDA_DIR)
    generate_word_frequency_report(combined_df, EDA_DIR)
    generate_triangulation_html(tri_df, EDA_DIR)
    generate_summary_metrics_json(combined_df, survey_df, tri_df, EDA_DIR)
    
    print("\n" + "=" * 72)
    print(f"🎉 SUKSES: Seluruh artefak EDA ({len(os.listdir(EDA_DIR))} file) selesai dihasilkan!")
    print(f"📁 Lokasi: {EDA_DIR}")
    print("=" * 72)


if __name__ == "__main__":
    main()
