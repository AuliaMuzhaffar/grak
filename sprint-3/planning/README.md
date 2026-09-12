# 🗺️ Master Roadmap — GRAK Sprint 3 Pipeline

> **Project**: Analisis Ekosistem Startup Aceh 2026  
> **Deadline**: Minggu depan (ML model + dashboard ready)  
> **Owner**: Aulia (semua wilayah)  

---

## 📂 Daftar File Planning

| Fase | File | Estimasi | Status |
|------|------|----------|--------|
| **Fase 1** | [fase-1-fix-scraping.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/planning/fase-1-fix-scraping.md) | 1.5-2 hari | ✅ Selesai |
| **Fase 2** | [fase-2-cleaning.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/planning/fase-2-cleaning.md) | 0.5-1 hari | ✅ Selesai |
| **Fase 3** | [fase-3-labeling.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/planning/fase-3-labeling.md) | 1-1.5 hari | ⬜ Belum |
| **Fase 4** | [fase-4-ml-model.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/planning/fase-4-ml-model.md) | 1.5-2 hari | ⬜ Belum |
| **Fase 5** | [fase-5-dashboard.md](file:///Users/auliamuzhaffar/Documents/grak/sprint-3/planning/fase-5-dashboard.md) | 1-1.5 hari | ⬜ Belum |

**Total estimasi**: 5.5-8 hari kerja

---

## 🔗 Dependency Graph

```
Fase 1 ──→ Fase 2 ──→ Fase 3 ──→ Fase 4 ──→ Fase 5
Scraping    Cleaning    Labeling    ML Model    Dashboard
(2 hari)    (0.5 hari)  (1.5 hari)  (2 hari)    (1 hari)

Output:     Output:      Output:     Output:     Output:
resolved    clean.csv    labeled     .pkl models index.html
articles    quality      _final.csv  eval report report.md
.csv        report                   confusion
                                     matrix
```

**Setiap fase HARUS selesai sebelum fase berikutnya dimulai.**

---

## 🏃 Execution Order

### Hari 1-2: Fase 1 — Fix Scraping Pipeline
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping

# Step 1-3: Buat lib/ modules
# (ikuti instruksi di fase-1-fix-scraping.md)

# Step 4: Jalankan URL resolver
python3 02_resolver.py

# Step 5: Re-run extraction
python3 03_extraction.py

# Verifikasi: total artikel naik dari 660 ke ≥1000
```

### Hari 2-3: Fase 2 — Cleaning
```bash
# Step 1: Install dependencies
pip install datasketch

# Step 2-4: Jalankan cleaning
python3 04_cleaning.py

# Verifikasi: quality gate terpenuhi
```

### Hari 3-4: Fase 3 — Labeling
```bash
# Step 1-2: Auto-label
python3 05_labeling.py

# Step 3: Human review (buka needs_review.csv di Sheets/Excel)
# Step 4: Iterate rules → re-run
python3 05_labeling.py
```

### Hari 4-5: Fase 4 — ML Model
```bash
# Step 0: Install
pip install scikit-learn matplotlib seaborn wordcloud

# Step 1: EDA
python3 06_eda.py

# Step 2: Train model
python3 07_model_training.py

# Step 3: Test prediction
python3 08_predict.py --text "Startup Aceh mendapat pendanaan"
```

### Hari 5-6: Fase 5 — Dashboard
```bash
# Step 0: Install
pip install plotly

# Step 1: Generate dashboard
python3 09_dashboard.py

# Buka di browser
open ../data/processed/dashboard/index.html
```

---

## 📦 File Pipeline Summary

```
sprint-3/materi-4/
├── scraping/
│   ├── config.py                ← Konfigurasi (sudah ada, perlu update)
│   ├── 01_discovery.py          ← Fase 0: Sudah ada, tidak diubah
│   ├── 02_resolver.py           ← Fase 1: URL resolver (NEW)
│   ├── 03_extraction.py         ← Fase 1: Extraction refactored
│   ├── 04_cleaning.py           ← Fase 2: Cleaning refactored (NEW)
│   ├── 05_labeling.py           ← Fase 3: Semi-auto labeling (NEW)
│   ├── labeling_rules.py        ← Fase 3: Label rules (NEW)
│   ├── 06_eda.py                ← Fase 4: EDA (NEW)
│   ├── 07_model_training.py     ← Fase 4: ML training (NEW)
│   ├── 08_predict.py            ← Fase 4: Prediction (NEW)
│   ├── 09_dashboard.py          ← Fase 5: Dashboard (NEW)
│   └── lib/
│       ├── __init__.py          ← Fase 1 (NEW)
│       ├── http_client.py       ← Fase 1 (NEW)
│       ├── logger.py            ← Fase 1 (NEW)
│       └── dedup.py             ← Fase 2 (NEW)
├── data/
│   ├── discovery_articles.csv   ← Existing
│   ├── resolved_urls.csv        ← Fase 1 output
│   ├── articles_database.csv    ← Fase 1 output (updated)
│   ├── paragraphs_raw.csv       ← Fase 1 output (updated)
│   ├── processed/
│   │   ├── public_text_news_clean.csv    ← Fase 2 output
│   │   ├── quality_report.json           ← Fase 2 output
│   │   ├── labeled_dataset.csv           ← Fase 3 output
│   │   ├── needs_review.csv              ← Fase 3 output
│   │   ├── labeled_dataset_final.csv     ← Fase 3 output (after review)
│   │   ├── eda_report/                   ← Fase 4 output
│   │   ├── dashboard/index.html          ← Fase 5 output
│   │   └── final_report.md               ← Fase 5 output
│   └── models/
│       ├── tfidf_vectorizer.pkl          ← Fase 4 output
│       ├── topic_model.pkl               ← Fase 4 output
│       ├── sentiment_model.pkl           ← Fase 4 output
│       └── evaluation_report.json        ← Fase 4 output
├── logs/
│   └── scraping_*.jsonl                  ← All phases
└── planning/
    ├── README.md                         ← File ini
    ├── fase-1-fix-scraping.md
    ├── fase-2-cleaning.md
    ├── fase-3-labeling.md
    ├── fase-4-ml-model.md
    └── fase-5-dashboard.md
```

---

## 🧪 All Dependencies (Install All at Once)

```bash
pip install requests beautifulsoup4 newspaper3k lxml_html_clean \
            pandas tqdm googlenewsdecoder \
            datasketch \
            scikit-learn matplotlib seaborn wordcloud \
            plotly
```

---

## 💡 Tips untuk Eksekusi dengan Coding Agent

1. **Satu fase = satu prompt** — Copy-paste isi file fase ke agent, minta eksekusi
2. **Verifikasi setiap step** — Setiap step punya verification command, jalankan sebelum lanjut
3. **Jangan skip checklist** — Checklist di akhir setiap fase adalah quality gate
4. **Jika error** — Lihat tabel troubleshooting di akhir setiap fase
5. **Agent boleh modifikasi** — Selama output dan behavior sesuai spesifikasi
