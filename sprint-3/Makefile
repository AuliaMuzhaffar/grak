# ==============================================================================
# 🚀 GRAK SPRINT 3 — PIPELINE DATA ENGINEERING, ANALYTICS & AUDIT
# ==============================================================================
# Gunakan 'make' atau 'make help' untuk melihat daftar perintah yang tersedia.
# ==============================================================================

.PHONY: help setup resolve extract phase1 clean phase2 label merge-labels phase3 \
        process-sources merge phase3_5 story phase5 pipeline-all status logs \
        audit-custody verify-custody

PYTHON       := python3
SCRAPING_DIR := materi-4/scraping
DATA_DIR     := materi-4/data
PROCESSED_DIR:= $(DATA_DIR)/processed
LOGS_DIR     := materi-4/logs

# Default target: Tampilkan menu bantuan yang rapi dan berwarna
help:
	@echo ""
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;33m      🛠️  GRAK SPRINT 3 — MAKEFILE PIPELINE LENGKAP                   \033[0m"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;32m📦 PERSIAPAN LINGKUNGAN (Setup):\033[0m"
	@echo "  \033[1;37mmake setup\033[0m           : Install semua dependensi (pip install -r requirements.txt)"
	@echo ""
	@echo "\033[1;32m🚀 FASE 1: SCRAPING (Data Acquisition)\033[0m"
	@echo "  \033[1;37mmake resolve\033[0m         : Jalankan 02_resolver.py (decode URL Google News)"
	@echo "  \033[1;37mmake extract\033[0m         : Jalankan 03_extraction.py (ekstraksi artikel)"
	@echo "  \033[1;37mmake phase1\033[0m          : Eksekusi Fase 1 Penuh (resolve + extract)"
	@echo ""
	@echo "\033[1;32m🧹 FASE 2: CLEANING & DEDUPLICATION\033[0m"
	@echo "  \033[1;37mmake phase2\033[0m          : Jalankan 04_cleaning.py (MinHash LSH Deduplication)"
	@echo "  \033[1;37mmake clean\033[0m           : Alias untuk phase2"
	@echo ""
	@echo "\033[1;32m🏷️  FASE 3: LABELING & INGESTION SHIELD\033[0m"
	@echo "  \033[1;37mmake label\033[0m           : Jalankan 05_labeling.py (Cascading Regex, 2-Pass)"
	@echo "  \033[1;37mmake merge-labels\033[0m    : Jalankan 06_merge_labels.py (Konsolidasi Auto & Manual)"
	@echo "  \033[1;37mmake phase3\033[0m          : Eksekusi Fase 3 Penuh (label + merge-labels)"
	@echo ""
	@echo "\033[1;32m🛡️  FASE 3.5: MULTI-SOURCE INTEGRATION\033[0m"
	@echo "  \033[1;37mmake process-sources\033[0m : Proses data survei (10), wawancara (10b), & medsos (10c)"
	@echo "  \033[1;37mmake merge\033[0m           : Jalankan 11_merge_all_sources.py (Shield V2 -> Golden Dataset)"
	@echo "  \033[1;37mmake phase3_5\033[0m        : Eksekusi Fase 3.5 Penuh (process-sources + merge)"
	@echo ""
	@echo "\033[1;32m📊 FASE 5: STORYTELLING & DECK ARTIFACTS\033[0m"
	@echo "  \033[1;37mmake story\033[0m           : Eksekusi 13_metrics + 14_charts + 15_build_deck + 15b_sync"
	@echo "  \033[1;37mmake phase5\033[0m          : Alias untuk story"
	@echo ""
	@echo "\033[1;32m⚡ MASTER PIPELINE:\033[0m"
	@echo "  \033[1;37mmake pipeline-all\033[0m    : Jalankan otomatis Fase 2 s/d 5 + Verifikasi Audit"
	@echo ""
	@echo "\033[1;32m🛡️  AUDIT & CHAIN OF CUSTODY:\033[0m"
	@echo "  \033[1;37mmake audit-custody\033[0m    : Verifikasi Integritas SHA-256 & Rantai Bukti Data"
	@echo ""
	@echo "\033[1;32m📈 MONITORING & STATUS:\033[0m"
	@echo "  \033[1;37mmake status\033[0m          : Cek progres lengkap volume data"
	@echo "  \033[1;37mmake logs\033[0m            : Intip 20 baris log event terakhir"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo ""

# ------------------------------------------------------------------------------
# 📦 SETUP TARGETS
# ------------------------------------------------------------------------------
setup:
	@echo "\033[1;33m▶ Menginstal seluruh dependensi Python...\033[0m"
	@$(PYTHON) -m pip install -r requirements.txt
	@echo "\033[1;32m✔ Seluruh dependensi berhasil diinstal!\033[0m"

# ------------------------------------------------------------------------------
# 🚀 FASE 1: SCRAPING TARGETS
# ------------------------------------------------------------------------------
resolve:
	@echo "\033[1;33m▶ [Step 1] Menjalankan URL Resolver...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 02_resolver.py

extract:
	@echo "\033[1;33m▶ [Step 2] Menjalankan Ekstraksi Konten...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 03_extraction.py

phase1: resolve extract
	@echo "\033[1;32m🎉 Fase 1 (Scraping) Selesai!\033[0m"

# ------------------------------------------------------------------------------
# 🧹 FASE 2: CLEANING TARGETS
# ------------------------------------------------------------------------------
clean:
	@echo "\033[1;33m▶ Menjalankan Data Cleaning & MinHash Deduplication...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 04_cleaning.py
	@echo "\033[1;32m🎉 Fase 2 Selesai!\033[0m"

phase2: clean

# ------------------------------------------------------------------------------
# 🏷️ FASE 3: LABELING TARGETS
# ------------------------------------------------------------------------------
label:
	@echo "\033[1;33m▶ Menjalankan Semi-Automatic Labeling (Cascading Regex)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 05_labeling.py

merge-labels:
	@echo "\033[1;33m▶ Menjalankan Konsolidasi Auto & Manual Labels...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 06_merge_labels.py

phase3: label merge-labels
	@echo "\033[1;32m🎉 Fase 3 Selesai!\033[0m"

# ------------------------------------------------------------------------------
# 🛡️ FASE 3.5: MERGING TARGETS
# ------------------------------------------------------------------------------
process-sources:
	@echo "\033[1;33m▶ Memproses Data Survei (10_process_survey.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 10_process_survey.py
	@echo "\033[1;33m▶ Memproses Data Wawancara (10b_process_interviews.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 10b_process_interviews.py
	@echo "\033[1;33m▶ Memproses Data Media Sosial (10c_process_social_media.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 10c_process_social_media.py

merge: process-sources
	@echo "\033[1;33m▶ Menjalankan Ingestion Shield V2 & Multi-Source Merge...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 11_merge_all_sources.py

phase3_5: merge
	@echo "\033[1;32m🎉 Fase 3.5 Selesai!\033[0m"

# ------------------------------------------------------------------------------
# 📊 FASE 5: STORYTELLING & DECK TARGETS
# ------------------------------------------------------------------------------
story:
	@echo "\033[1;33m▶ [1/4] Menghitung Metrik Terverifikasi (13_verified_metrics.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 13_verified_metrics.py
	@echo "\033[1;33m▶ [2/4] Membangun Grafik Visualisasi (14_story_charts.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 14_story_charts.py
	@echo "\033[1;33m▶ [3/4] Merender Dek Presentasi Eksekutif (15_build_deck.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 15_build_deck.py
	@echo "\033[1;33m▶ [4/4] Menyinkronkan Laporan Eksekutif Utama (15b_sync_executive_report.py)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 15b_sync_executive_report.py
	@echo "\033[1;32m🎉 Fase 5 (Storytelling & HTML Deliverables) Selesai!\033[0m"

phase5: story

# ------------------------------------------------------------------------------
# ⚡ MASTER PIPELINE: RUN ALL AUTOMATICALLY
# ------------------------------------------------------------------------------
pipeline-all: phase2 phase3 phase3_5 phase5 audit-custody
	@echo ""
	@echo "\033[1;32m======================================================================\033[0m"
	@echo "\033[1;32m🏆 SELURUH PIPELINE GRAK SPRINT 3 BERHASIL DIEKSEKUSI & LOLOS AUDIT! \033[0m"
	@echo "\033[1;32m======================================================================\033[0m"
	@echo ""

# ------------------------------------------------------------------------------
# 🛡️ AUDIT & CHAIN OF CUSTODY TARGETS
# ------------------------------------------------------------------------------
audit-custody:
	@$(PYTHON) $(SCRAPING_DIR)/16_verify_chain_of_custody.py

verify-custody: audit-custody

# ------------------------------------------------------------------------------
# 📈 MONITORING & STATUS TARGETS
# ------------------------------------------------------------------------------
status:
	@echo ""
	@echo "\033[1;36m📊 RINGKASAN STATUS DATASET GRAK SPRINT 3:\033[0m"
	@$(PYTHON) -c "import os, pandas as pd; \
d = '$(DATA_DIR)'; pd_dir = '$(PROCESSED_DIR)'; \
disc = os.path.join(d, 'discovery_articles.csv'); \
res = os.path.join(d, 'resolved_urls.csv'); \
db = os.path.join(d, 'articles_database.csv'); \
clean = os.path.join(pd_dir, 'public_text_news_clean.csv'); \
labeled = os.path.join(pd_dir, 'labeled_dataset_final.csv'); \
comb = os.path.join(pd_dir, 'combined_text.csv'); \
srv = os.path.join(pd_dir, 'survey_text_extracted.csv'); \
ivw = os.path.join(pd_dir, 'interview_dataset.csv'); \
soc = os.path.join(pd_dir, 'social_media_labeled.csv'); \
print(f'  [Fase 1] Articles Database  : {len(pd.read_csv(db)) if os.path.exists(db) else 0} artikel'); \
print(f'  [Fase 2] Cleaned Paragraphs : {len(pd.read_csv(clean)) if os.path.exists(clean) else 0} baris'); \
print(f'  [Fase 3] Labeled Dataset    : {len(pd.read_csv(labeled)) if os.path.exists(labeled) else 0} baris'); \
print(f'  [Fase 3.5] Survey Dataset   : {len(pd.read_csv(srv)) if os.path.exists(srv) else 0} baris'); \
print(f'  [Fase 3.5] Interview Data   : {len(pd.read_csv(ivw)) if os.path.exists(ivw) else 0} baris'); \
print(f'  [Fase 3.5] Social Media     : {len(pd.read_csv(soc)) if os.path.exists(soc) else 0} baris'); \
df_comb = pd.read_csv(comb) if os.path.exists(comb) else None; \
news_survivors = len(df_comb[df_comb[\"data_source\"] == \"news\"]) if df_comb is not None else 0; \
print(f'  [Fase 3.5] Golden News Data : {news_survivors} baris (Lolos Ingestion Shield)'); \
print(f'  [Fase 3.5] Golden Dataset   : {len(df_comb) if df_comb is not None else 0} baris (4 Sumber)')"
	@echo ""

logs:
	@echo "\033[1;36m📝 20 LOG EVENT TERAKHIR:\033[0m"
	@ls -t $(LOGS_DIR)/scraping_*.jsonl 2>/dev/null | head -n 1 | xargs -I {} tail -n 20 {}
