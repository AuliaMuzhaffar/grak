# Fase 5: Visualization & Dashboard

> **Estimasi waktu**: 1 - 1.5 hari kerja  
> **Prioritas**: 🟡 P1  
> **Prasyarat**: Fase 4 selesai (model trained + evaluation report ada)  
> **Output**: Interactive HTML dashboard + laporan final  

---

## 🎯 Tujuan Fase Ini

1. **Buat dashboard interaktif** — Visualisasi insight ekosistem startup Aceh
2. **Ringkasan temuan** — Distribusi topic, sentiment, portal coverage
3. **Model performance** — Tampilkan evaluation metrics secara visual
4. **Export-ready** — Dashboard bisa dibuka di browser tanpa server

---

## 📋 Daftar File yang Dibuat

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/09_dashboard.py` | Script generate dashboard HTML |
| **Output** | `data/processed/dashboard/index.html` | Dashboard interaktif |
| **Output** | `data/processed/dashboard/assets/` | Grafik PNG yang di-embed |
| **Output** | `data/processed/final_report.md` | Laporan ringkas markdown |

---

## Step 0: Install Dependencies

```bash
pip install plotly    # Untuk interactive charts dalam HTML
```

### Kenapa Plotly?

| Opsi | Pro | Kontra |
|------|-----|--------|
| **Plotly** ✅ | Interactive, export ke HTML standalone, tidak perlu server | File size agak besar (~3MB) |
| Matplotlib | Ringan, standard | Hanya static PNG, tidak interaktif |
| Streamlit | Interactive, mudah | Butuh `streamlit run`, perlu server |
| Tableau | Visual bagus | Perlu license, bukan Python |

**Plotly terpilih** karena menghasilkan **satu file HTML** yang bisa dibuka di browser tanpa setup apapun — cocok untuk dibagikan ke tim.

---

## Step 1: Buat `09_dashboard.py`

**File**: `sprint-3/materi-4/scraping/09_dashboard.py`

```python
"""
09_dashboard.py — Generate Interactive HTML Dashboard
GRAK 2026 · Sprint 3

CARA PAKAI:
  python3 09_dashboard.py

INPUT:
  → data/processed/labeled_dataset_final.csv
  → data/models/evaluation_report.json

OUTPUT:
  → data/processed/dashboard/index.html (Dashboard interaktif)
  → data/processed/final_report.md (Laporan markdown)

PRASYARAT:
  pip install plotly pandas
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from collections import Counter

# Coba import plotly
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("⚠️ plotly belum terinstall. Install dengan: pip install plotly")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.logger import get_logger

# Paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")
DASHBOARD_DIR = os.path.join(PROCESSED_DIR, "dashboard")

INPUT_CSV = os.path.join(PROCESSED_DIR, "labeled_dataset_final.csv")
EVAL_REPORT = os.path.join(MODELS_DIR, "evaluation_report.json")
OUTPUT_HTML = os.path.join(DASHBOARD_DIR, "index.html")
OUTPUT_REPORT = os.path.join(PROCESSED_DIR, "final_report.md")

log = get_logger("09_dashboard")

# Color scheme
TOPIC_COLORS = {
    "funding": "#e74c3c",
    "talent": "#3498db",
    "infrastructure": "#2ecc71",
    "regulation": "#f39c12",
    "market_access": "#9b59b6",
    "ecosystem": "#1abc9c",
    "digitalization": "#e67e22",
    "success_story": "#27ae60",
}

SENTIMENT_COLORS = {
    "positive": "#2ecc71",
    "negative": "#e74c3c",
    "neutral": "#95a5a6",
}


def create_topic_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart distribusi topic."""
    topic_counts = df["topic"].value_counts().sort_values(ascending=True)
    
    colors = [TOPIC_COLORS.get(t, "#bdc3c7") for t in topic_counts.index]
    
    fig = go.Figure(go.Bar(
        x=topic_counts.values,
        y=topic_counts.index,
        orientation="h",
        marker_color=colors,
        text=[f"{v} ({v/len(df)*100:.1f}%)" for v in topic_counts.values],
        textposition="outside",
    ))
    
    fig.update_layout(
        title="📊 Distribusi Topic",
        xaxis_title="Jumlah Paragraf",
        height=400,
        margin=dict(l=150),
    )
    
    return fig


def create_sentiment_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart distribusi sentiment."""
    sent_counts = df["sentiment"].value_counts()
    
    colors = [SENTIMENT_COLORS.get(s, "#bdc3c7") for s in sent_counts.index]
    
    fig = go.Figure(go.Pie(
        labels=sent_counts.index,
        values=sent_counts.values,
        hole=0.4,
        marker_colors=colors,
        textinfo="label+percent",
        textfont_size=14,
    ))
    
    fig.update_layout(
        title="😊 Distribusi Sentiment",
        height=400,
    )
    
    return fig


def create_topic_sentiment_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap topic × sentiment."""
    cross = pd.crosstab(df["topic"], df["sentiment"])
    
    # Normalize per row (%)
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
    
    fig = go.Figure(go.Heatmap(
        z=cross_pct.values,
        x=cross_pct.columns.tolist(),
        y=cross_pct.index.tolist(),
        colorscale="RdYlGn",
        text=cross.values,
        texttemplate="%{text}",
        textfont_size=12,
        hovertemplate="Topic: %{y}<br>Sentiment: %{x}<br>Count: %{text}<br>%{z:.1f}%",
    ))
    
    fig.update_layout(
        title="🔥 Topic × Sentiment Heatmap",
        height=400,
    )
    
    return fig


def create_portal_chart(df: pd.DataFrame) -> go.Figure:
    """Top 15 portal berita."""
    portal_counts = df["source_portal"].value_counts().head(15)
    
    fig = go.Figure(go.Bar(
        x=portal_counts.values,
        y=portal_counts.index,
        orientation="h",
        marker_color="#3498db",
        text=portal_counts.values,
        textposition="outside",
    ))
    
    fig.update_layout(
        title="📰 Top 15 Portal Berita",
        xaxis_title="Jumlah Paragraf",
        height=450,
        margin=dict(l=200),
    )
    
    return fig


def create_confidence_chart(df: pd.DataFrame) -> go.Figure:
    """Distribusi Aceh confidence."""
    conf_counts = df["aceh_confidence"].value_counts()
    
    colors = {"high": "#27ae60", "medium": "#f39c12", "low": "#e74c3c"}
    
    fig = go.Figure(go.Bar(
        x=conf_counts.index,
        y=conf_counts.values,
        marker_color=[colors.get(c, "#bdc3c7") for c in conf_counts.index],
        text=[f"{v} ({v/len(df)*100:.1f}%)" for v in conf_counts.values],
        textposition="outside",
    ))
    
    fig.update_layout(
        title="🎯 Aceh Relevance Confidence",
        yaxis_title="Jumlah Paragraf",
        height=350,
    )
    
    return fig


def create_wordcount_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram word count."""
    fig = go.Figure(go.Histogram(
        x=df["word_count"],
        nbinsx=50,
        marker_color="#3498db",
        opacity=0.7,
    ))
    
    fig.add_vline(x=df["word_count"].mean(), line_dash="dash",
                  line_color="red", annotation_text=f"Mean: {df['word_count'].mean():.0f}")
    
    fig.update_layout(
        title="📏 Distribusi Word Count per Paragraf",
        xaxis_title="Word Count",
        yaxis_title="Frequency",
        height=350,
    )
    
    return fig


def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Timeline artikel per bulan."""
    df_date = df.copy()
    
    # Parse dates — handle multiple formats
    df_date["date_parsed"] = pd.to_datetime(df_date["publish_date"], errors="coerce")
    df_date = df_date.dropna(subset=["date_parsed"])
    
    if len(df_date) == 0:
        return None
    
    df_date["month"] = df_date["date_parsed"].dt.to_period("M").astype(str)
    monthly = df_date.groupby("month").size().reset_index(name="count")
    
    fig = go.Figure(go.Scatter(
        x=monthly["month"],
        y=monthly["count"],
        mode="lines+markers",
        line=dict(color="#e74c3c", width=2),
        marker=dict(size=8),
    ))
    
    fig.update_layout(
        title="📅 Timeline Publikasi Berita",
        xaxis_title="Bulan",
        yaxis_title="Jumlah Paragraf",
        height=350,
    )
    
    return fig


def generate_html_dashboard(df: pd.DataFrame, eval_report: dict | None):
    """Generate satu file HTML dashboard."""
    
    charts = []
    
    # Row 1: Topic + Sentiment (side by side)
    charts.append(("topic", create_topic_chart(df)))
    charts.append(("sentiment", create_sentiment_chart(df)))
    
    # Row 2: Heatmap + Portal
    charts.append(("heatmap", create_topic_sentiment_heatmap(df)))
    charts.append(("portal", create_portal_chart(df)))
    
    # Row 3: Confidence + Word Count
    charts.append(("confidence", create_confidence_chart(df)))
    charts.append(("wordcount", create_wordcount_histogram(df)))
    
    # Row 4: Timeline
    timeline = create_timeline_chart(df)
    if timeline:
        charts.append(("timeline", timeline))
    
    # Build HTML
    chart_divs = ""
    chart_scripts = ""
    
    for i, (name, fig) in enumerate(charts):
        div_id = f"chart_{name}"
        chart_html = fig.to_html(full_html=False, include_plotlyjs=(i == 0), div_id=div_id)
        chart_divs += f'<div class="chart-container">{chart_html}</div>\n'
    
    # Summary statistics
    total_paragraphs = len(df)
    total_articles = df["article_url"].nunique() if "article_url" in df.columns else 0
    total_portals = df["source_portal"].nunique() if "source_portal" in df.columns else 0
    top_topic = df["topic"].value_counts().index[0] if len(df) > 0 else "N/A"
    
    # Model evaluation section
    model_section = ""
    if eval_report:
        topic_acc = eval_report.get("topic", {}).get("accuracy", "N/A")
        topic_f1 = eval_report.get("topic", {}).get("f1_macro", "N/A")
        sent_acc = eval_report.get("sentiment", {}).get("accuracy", "N/A")
        sent_f1 = eval_report.get("sentiment", {}).get("f1_macro", "N/A")
        
        model_section = f"""
        <div class="stats-grid" style="margin-top: 30px;">
            <h2 style="grid-column: 1 / -1; text-align: center;">🤖 Model Performance</h2>
            <div class="stat-card">
                <div class="stat-value">{topic_acc if isinstance(topic_acc, str) else f'{topic_acc:.1%}'}</div>
                <div class="stat-label">Topic Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{topic_f1 if isinstance(topic_f1, str) else f'{topic_f1:.1%}'}</div>
                <div class="stat-label">Topic F1 (Macro)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sent_acc if isinstance(sent_acc, str) else f'{sent_acc:.1%}'}</div>
                <div class="stat-label">Sentiment Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sent_f1 if isinstance(sent_f1, str) else f'{sent_f1:.1%}'}</div>
                <div class="stat-label">Sentiment F1 (Macro)</div>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRAK 2026 — Analisis Ekosistem Startup Aceh</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #e2e8f0;
            --accent: #38bdf8;
            --accent2: #818cf8;
            --border: #334155;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        header h1 {{
            font-size: 2.2em;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        header p {{
            color: #94a3b8;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-2px); }}
        .stat-value {{
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-label {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .chart-container {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
        }}
        footer {{
            text-align: center;
            padding: 30px;
            color: #64748b;
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
        @media (max-width: 768px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            header h1 {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Analisis Ekosistem Startup Aceh 2026</h1>
        <p>GRAK 2026 · Sprint 3 · Text Analysis Dashboard</p>
        <p style="margin-top: 5px; color: #64748b;">
            Generated: {datetime.now().strftime("%d %B %Y, %H:%M WIB")}
        </p>
    </header>
    
    <div class="container">
        <!-- Summary Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_paragraphs:,}</div>
                <div class="stat-label">Total Paragraf</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_articles:,}</div>
                <div class="stat-label">Artikel Unik</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_portals}</div>
                <div class="stat-label">Portal Berita</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{top_topic}</div>
                <div class="stat-label">Topic Dominan</div>
            </div>
        </div>
        
        {model_section}
        
        <!-- Charts -->
        <div class="charts-grid">
            {chart_divs}
        </div>
    </div>
    
    <footer>
        <p>GRAK 2026 — Data & Research Track · Aulia</p>
        <p>Pipeline: Discovery → Resolve → Extract → Clean → Label → ML → Dashboard</p>
    </footer>
</body>
</html>"""
    
    return html


def generate_markdown_report(df: pd.DataFrame, eval_report: dict | None) -> str:
    """Generate laporan final dalam markdown."""
    
    total = len(df)
    topic_counts = df["topic"].value_counts()
    sent_counts = df["sentiment"].value_counts()
    
    report = f"""# 📊 Laporan Final — Analisis Ekosistem Startup Aceh

> **GRAK 2026 · Sprint 3 · Text Analysis**  
> Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 1. Ringkasan Dataset

| Metric | Nilai |
|--------|-------|
| Total paragraf | {total:,} |
| Artikel unik | {df['article_url'].nunique():,} |
| Portal berita | {df['source_portal'].nunique()} |
| Rata-rata kata/paragraf | {df['word_count'].mean():.1f} |

## 2. Distribusi Topic

| Topic | Jumlah | Persentase |
|-------|--------|-----------|
"""
    
    for topic, count in topic_counts.items():
        pct = count / total * 100
        report += f"| {topic} | {count} | {pct:.1f}% |\n"
    
    report += f"""
## 3. Distribusi Sentiment

| Sentiment | Jumlah | Persentase |
|-----------|--------|-----------|
"""
    
    for sent, count in sent_counts.items():
        pct = count / total * 100
        report += f"| {sent} | {count} | {pct:.1f}% |\n"
    
    report += f"""
## 4. Aceh Relevance

| Level | Jumlah | Persentase |
|-------|--------|-----------|
"""
    
    conf_counts = df["aceh_confidence"].value_counts()
    for level in ["high", "medium", "low"]:
        count = conf_counts.get(level, 0)
        pct = count / total * 100
        report += f"| {level} | {count} | {pct:.1f}% |\n"
    
    report += f"""
## 5. Top 10 Portal Berita

| Portal | Paragraf |
|--------|----------|
"""
    
    portal_counts = df["source_portal"].value_counts().head(10)
    for portal, count in portal_counts.items():
        report += f"| {portal} | {count} |\n"
    
    if eval_report:
        topic_acc = eval_report.get("topic", {}).get("accuracy", "N/A")
        topic_f1 = eval_report.get("topic", {}).get("f1_macro", "N/A")
        sent_acc = eval_report.get("sentiment", {}).get("accuracy", "N/A")
        sent_f1 = eval_report.get("sentiment", {}).get("f1_macro", "N/A")
        
        report += f"""
## 6. Model Performance

| Model | Accuracy | F1 (Macro) |
|-------|----------|-----------|
| Topic (LinearSVC) | {topic_acc} | {topic_f1} |
| Sentiment (LogReg) | {sent_acc} | {sent_f1} |
"""
    
    report += f"""
---

## 7. Key Insights

### Topic yang paling banyak dibahas
- **{topic_counts.index[0]}** mendominasi dengan {topic_counts.values[0]} paragraf ({topic_counts.values[0]/total*100:.1f}%)
- Ini menunjukkan bahwa media Aceh paling banyak membahas isu {topic_counts.index[0]} terkait ekosistem startup

### Sentiment keseluruhan
- Mayoritas berita bersifat **{sent_counts.index[0]}** ({sent_counts.values[0]/total*100:.1f}%)
- Ini menunjukkan bagaimana media meframe ekosistem startup di Aceh

### Rekomendasi
1. Fokus analisis lebih dalam pada topic "{topic_counts.index[0]}" dan "{topic_counts.index[1]}"
2. Cross-reference temuan text analysis dengan data survey Sprint 3
3. Gunakan model prediction untuk classify data baru dari wilayah lain

---

*Laporan ini dihasilkan otomatis oleh pipeline GRAK Sprint 3.*
"""
    
    return report


def main():
    if not HAS_PLOTLY:
        print("❌ plotly belum terinstall!")
        print("   pip install plotly")
        return
    
    if not os.path.exists(INPUT_CSV):
        print(f"❌ File tidak ditemukan: {INPUT_CSV}")
        print("   Jalankan labeling dulu (Fase 3)!")
        return
    
    df = pd.read_csv(INPUT_CSV)
    df = df.dropna(subset=["topic"])
    df = df[df["topic"] != ""]
    
    print("=" * 65)
    print("📊 DASHBOARD — Generating Interactive Dashboard")
    print(f"   Dataset: {len(df)} baris berlabel")
    print("=" * 65)
    print()
    
    # Load evaluation report (optional)
    eval_report = None
    if os.path.exists(EVAL_REPORT):
        with open(EVAL_REPORT) as f:
            eval_report = json.load(f)
        print("   ✓ Model evaluation report loaded")
    else:
        print("   ⚠️ Evaluation report tidak ditemukan, skip model metrics")
    
    # Generate HTML dashboard
    print("   📈 Generating HTML dashboard...")
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    html = generate_html_dashboard(df, eval_report)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"   ✓ Dashboard saved: {OUTPUT_HTML}")
    
    # Generate markdown report
    print("   📝 Generating markdown report...")
    report_md = generate_markdown_report(df, eval_report)
    
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_md)
    
    print(f"   ✓ Report saved: {OUTPUT_REPORT}")
    
    # ===== RINGKASAN =====
    print()
    print("=" * 65)
    print("✅ DASHBOARD SELESAI!")
    print("=" * 65)
    print()
    print(f"📁 Dashboard HTML : {OUTPUT_HTML}")
    print(f"📁 Final Report   : {OUTPUT_REPORT}")
    print()
    print("🌐 Buka dashboard di browser:")
    print(f"   open {OUTPUT_HTML}")
    print()
    print("=" * 65)
    
    log.info("Dashboard generated", output=OUTPUT_HTML)


if __name__ == "__main__":
    main()
```

### Verifikasi:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 09_dashboard.py

# Buka di browser:
open ../data/processed/dashboard/index.html
```

**Output yang diharapkan**:
- File `index.html` terbuat
- Dashboard bisa dibuka di browser
- 7 chart interaktif (hover, zoom)
- Summary stats di bagian atas
- Model performance metrics (jika model sudah di-train)

---

## ✅ Checklist Fase 5 Selesai

- [ ] `09_dashboard.py` — Jalan tanpa error
- [ ] `dashboard/index.html` — Terbuat, bisa dibuka di browser
- [ ] 7 chart interaktif tampil dengan benar
- [ ] Summary stats (total paragraf, artikel, portal) akurat
- [ ] Model performance section tampil (jika Fase 4 selesai)
- [ ] `final_report.md` — Terbuat, key insights masuk akal
- [ ] Dashboard bisa di-share (single HTML file, no server needed)

---

## 🚨 Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `ModuleNotFoundError: plotly` | Belum install | `pip install plotly` |
| Chart tidak muncul di browser | HTML corrupt | Re-run `09_dashboard.py` |
| Timeline chart kosong | Date format tidak dikenali | Cek format `publish_date` di CSV |
| Model section tidak tampil | `evaluation_report.json` tidak ada | Jalankan Fase 4 dulu |
| File HTML terlalu besar (>10MB) | Plotly JS embedded | Normal untuk standalone HTML |

---

## 📝 Catatan untuk Agent / Rekan

1. **Dashboard standalone** — File `index.html` berisi semua JS/CSS di dalamnya. Bisa di-email, di-share via WhatsApp, tanpa server.
2. **Re-generate** — Setiap kali data berubah, jalankan `python3 09_dashboard.py` untuk update dashboard.
3. **Dark mode** — Dashboard sudah dark mode by default (lebih premium).
4. **Responsive** — Dashboard bisa dilihat di mobile (responsive grid).
5. **Markdown report** — `final_report.md` cocok untuk copy-paste ke dokumen Google Docs atau presentasi.
