# ==============================================================================
# 🚀 GRAK SPRINT 3 — FASE 1 SCRAPING PIPELINE MAKEFILE
# ==============================================================================
# Gunakan 'make' atau 'make help' untuk melihat daftar perintah yang tersedia.
# ==============================================================================

.PHONY: help smoke smoke-quick resolve extract full status logs clean-smoke

PYTHON       := python3
SCRAPING_DIR := materi-4/scraping
DATA_DIR     := materi-4/data
LOGS_DIR     := materi-4/logs

# Default target: Tampilkan menu bantuan yang rapi dan berwarna
help:
	@echo ""
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;33m       🛠️  GRAK SPRINT 3 — MAKEFILE PIPELINE SCRAPING (FASE 1)         \033[0m"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;32m🧪 PENGUJIAN & SMOKE TEST (Aman, Database Asli Tidak Tersentuh):\033[0m"
	@echo "  \033[1;37mmake smoke\033[0m        : Jalankan smoke test 50 artikel (evaluasi efisiensi)"
	@echo "  \033[1;37mmake smoke-quick\033[0m  : Jalankan smoke test cepat 10 artikel (~10 detik)"
	@echo "  \033[1;37mmake clean-smoke\033[0m  : Hapus file sementara hasil smoke test"
	@echo ""
	@echo "\033[1;32m🚀 EKSEKUSI PENUH (FULL SCRAPE):\033[0m"
	@echo "  \033[1;37mmake resolve\033[0m      : Jalankan 02_resolver.py (decode semua URL Google News)"
	@echo "  \033[1;37mmake extract\033[0m      : Jalankan 03_extraction.py (ekstraksi artikel baru)"
	@echo "  \033[1;37mmake full\033[0m         : Jalankan resolve + extract secara berurutan"
	@echo ""
	@echo "\033[1;32m📊 MONITORING & PEMERIKSAAN DATA:\033[0m"
	@echo "  \033[1;37mmake status\033[0m       : Cek jumlah data artikel, paragraf, dan progres"
	@echo "  \033[1;37mmake logs\033[0m         : Intip 20 baris log event terakhir"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo ""

# ------------------------------------------------------------------------------
# 🧪 SMOKE TEST TARGETS
# ------------------------------------------------------------------------------
smoke:
	@echo "\033[1;33m▶ Menjalankan Smoke Test (50 Artikel)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) smoke_test.py --sample-size 50

smoke-quick:
	@echo "\033[1;33m▶ Menjalankan Smoke Test Kilat (10 Artikel)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) smoke_test.py --sample-size 10

clean-smoke:
	@echo "\033[1;33m▶ Membersihkan folder output smoke test...\033[0m"
	@rm -rf $(DATA_DIR)/smoke_test_output/*
	@echo "\033[1;32m✅ Folder smoke_test_output telah dibersihkan!\033[0m"

# ------------------------------------------------------------------------------
# 🚀 FULL PRODUCTION SCRAPE TARGETS
# ------------------------------------------------------------------------------
resolve:
	@echo "\033[1;33m▶ [Step 1] Menjalankan URL Resolver (1.350 URL)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 02_resolver.py

extract:
	@echo "\033[1;33m▶ [Step 2] Menjalankan Ekstraksi Konten (Resume Mode Aktif)...\033[0m"
	@cd $(SCRAPING_DIR) && $(PYTHON) 03_extraction.py

full: resolve extract
	@echo "\033[1;32m🎉 Pipeline Scraping Fase 1 Selesai Lengkap!\033[0m"
	@$(MAKE) status

# ------------------------------------------------------------------------------
# 📊 MONITORING & STATUS TARGETS
# ------------------------------------------------------------------------------
status:
	@echo ""
	@echo "\033[1;36m📊 RINGKASAN STATUS DATASET (materi-4/data):\033[0m"
	@$(PYTHON) -c "import os, pandas as pd; \
d = '$(DATA_DIR)'; \
disc = os.path.join(d, 'discovery_articles.csv'); \
res = os.path.join(d, 'resolved_urls.csv'); \
db = os.path.join(d, 'articles_database.csv'); \
para = os.path.join(d, 'paragraphs_raw.csv'); \
fail = os.path.join(d, 'failed_urls.csv'); \
print(f'  • Discovery Articles : {len(pd.read_csv(disc)) if os.path.exists(disc) else 0} URL'); \
print(f'  • Resolved URLs      : {len(pd.read_csv(res)) if os.path.exists(res) else 0} URL'); \
print(f'  • Articles Database  : {len(pd.read_csv(db)) if os.path.exists(db) else 0} artikel'); \
print(f'  • Paragraphs Raw     : {len(pd.read_csv(para)) if os.path.exists(para) else 0} paragraf'); \
print(f'  • Failed URLs        : {len(pd.read_csv(fail)) if os.path.exists(fail) else 0} URL')"
	@echo ""

logs:
	@echo "\033[1;36m📝 20 LOG EVENT TERAKHIR:\033[0m"
	@ls -t $(LOGS_DIR)/scraping_*.jsonl 2>/dev/null | head -n 1 | xargs -I {} tail -n 20 {}
