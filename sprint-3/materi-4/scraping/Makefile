# ==============================================================================
# 🚀 GRAK SPRINT 3 — PIPELINE MASTER MAKEFILE (FASE 1 & FASE 2)
# ==============================================================================

.PHONY: help smoke smoke-quick clean-smoke resolve extract full status logs \
        test-dedup clean-data check-quality spot-check

PYTHON   := python3
DATA_DIR := ../data
PROCESSED_DIR := ../data/processed
LOGS_DIR := ../logs

help:
	@echo ""
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;33m       🛠️  GRAK SPRINT 3 — PIPELINE MASTER MAKEFILE                   \033[0m"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo "\033[1;32m🧪 PENGUJIAN & SMOKE TEST (FASE 1):\033[0m"
	@echo "  \033[1;37mmake smoke\033[0m          : Jalankan smoke test scraping 50 artikel"
	@echo "  \033[1;37mmake smoke-quick\033[0m    : Jalankan smoke test kilat 10 artikel"
	@echo "  \033[1;37mmake clean-smoke\033[0m    : Bersihkan folder output smoke test"
	@echo ""
	@echo "\033[1;32m🌐 SCRAPING & EXTRACTION (FASE 1):\033[0m"
	@echo "  \033[1;37mmake resolve\033[0m        : Jalankan 02_resolver.py (decode URL Google News)"
	@echo "  \033[1;37mmake extract\033[0m        : Jalankan 03_extraction.py (ekstraksi artikel & paragraf)"
	@echo "  \033[1;37mmake full\033[0m           : Jalankan resolve + extract berurutan"
	@echo ""
	@echo "\033[1;32m🧹 DATA CLEANING & DEDUPLICATION (FASE 2):\033[0m"
	@echo "  \033[1;37mmake test-dedup\033[0m     : Unit test algoritma MinHash LSH (lib/dedup.py)"
	@echo "  \033[1;37mmake clean-data\033[0m     : Jalankan 04_cleaning.py (pipeline pembersihan 6-tahap)"
	@echo "  \033[1;37mmake check-quality\033[0m  : Validasi kepatuhan Quality Gate Fase 2"
	@echo "  \033[1;37mmake spot-check\033[0m     : Tampilkan 10 sampel acak teks dataset bersih"
	@echo ""
	@echo "\033[1;32m📊 MONITORING & PEMERIKSAAN DATA:\033[0m"
	@echo "  \033[1;37mmake status\033[0m         : Cek ringkasan volume data mentah & bersih"
	@echo "  \033[1;37mmake logs\033[0m           : Intip 20 event log scraping terakhir"
	@echo "\033[1;36m======================================================================\033[0m"
	@echo ""

# ==============================================================================
# FASE 1: SCRAPING & EXTRACTION
# ==============================================================================

smoke:
	@echo "\033[1;33m▶ Menjalankan Smoke Test (50 Artikel)...\033[0m"
	@$(PYTHON) smoke_test.py --sample-size 50

smoke-quick:
	@echo "\033[1;33m▶ Menjalankan Smoke Test Kilat (10 Artikel)...\033[0m"
	@$(PYTHON) smoke_test.py --sample-size 10

clean-smoke:
	@echo "\033[1;33m▶ Membersihkan folder output smoke test...\033[0m"
	@rm -rf $(DATA_DIR)/smoke_test_output/*
	@echo "\033[1;32m✅ Folder smoke_test_output telah dibersihkan!\033[0m"

resolve:
	@echo "\033[1;33m▶ [Step 1] Menjalankan URL Resolver (1.350 URL)...\033[0m"
	@$(PYTHON) 02_resolver.py

extract:
	@echo "\033[1;33m▶ [Step 2] Menjalankan Ekstraksi Konten (Resume Mode Aktif)...\033[0m"
	@$(PYTHON) 03_extraction.py

full: resolve extract
	@echo "\033[1;32m🎉 Pipeline Scraping Fase 1 Selesai Lengkap!\033[0m"
	@$(MAKE) status

# ==============================================================================
# FASE 2: CLEANING, DEDUPLICATION, & QUALITY ASSURANCE
# ==============================================================================

test-dedup:
	@echo "\033[1;33m▶ Menjalankan Unit Test MinHash LSH (lib/dedup.py)...\033[0m"
	@$(PYTHON) -c "from lib.dedup import find_near_duplicates; \
texts = ['Pemerintah Aceh mendukung pengembangan startup digital di Banda Aceh melalui berbagai program inkubasi', \
'Pemerintah Aceh mendukung pengembangan startup digital di Banda Aceh melalui berbagai program inkubasi daerah', \
'Sektor pariwisata Sabang terus mengalami peningkatan kunjungan wisatawan lokal']; \
dupes = find_near_duplicates(texts, threshold=0.7); \
print(f'  • Data input uji : {len(texts)} baris'); \
print(f'  • Indeks duplikat: {dupes}'); \
assert 1 in dupes, 'Gagal mendeteksi near-duplicate!'; \
print('\033[1;32m✅ Unit Test MinHash LSH Lolos 100%!\033[0m')"

clean-data:
	@echo "\033[1;33m▶ Menjalankan Pipeline Pembersihan & Deduplikasi (04_cleaning.py)...\033[0m"
	@$(PYTHON) 04_cleaning.py

check-quality:
	@$(PYTHON) -c "import os, pandas as pd; \
clean_file = os.path.join('$(PROCESSED_DIR)', 'public_text_news_clean.csv'); \
assert os.path.exists(clean_file), 'File public_text_news_clean.csv belum ada! Jalankan make clean-data'; \
df = pd.read_csv(clean_file); \
total = len(df); \
high_med = ((df['aceh_confidence'] == 'high') | (df['aceh_confidence'] == 'medium')).sum(); \
high_med_pct = (high_med / total) * 100 if total > 0 else 0; \
avg_words = df['word_count'].mean(); \
portals = df['source_portal'].nunique(); \
print(''); \
print('\033[1;36m======================================================================\033[0m'); \
print('\033[1;33m📋 LAPORAN QUALITY GATE FASE 2 (public_text_news_clean.csv)          \033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
[print(f'  • {l:<28} : {a:<16} (Target: {t:<10}) {\"\033[1;32m✅ PASS\033[0m\" if ok else \"\033[1;31m❌ FAIL\033[0m\"}') for l, a, t, ok in [('Total Paragraf Bersih', f'{total:,}', '>= 5.000', total >= 5000), ('Relevansi Aceh (High+Med)', f'{high_med_pct:.1f}%', '>= 60.0%', high_med_pct >= 60), ('Rata-rata Kata/Paragraf', f'{avg_words:.1f}', '>= 15.0', avg_words >= 15), ('Cakupan Portal Berita', f'{portals}', '>= 10', portals >= 10)]]; \
print('\033[1;36m----------------------------------------------------------------------\033[0m'); \
print('\033[1;32m🏆 KESIMPULAN: SELURUH QUALITY GATE FASE 2 TERPENUHI SEMPURNA!\033[0m' if (total >= 5000 and high_med_pct >= 60 and avg_words >= 15 and portals >= 10) else '\033[1;31m⚠️ KESIMPULAN: ADA METRIK YANG BELUM MEMENUHI KRITERIA!\033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
print('')"

spot-check:
	@$(PYTHON) -c "import os, pandas as pd; \
clean_file = os.path.join('$(PROCESSED_DIR)', 'public_text_news_clean.csv'); \
assert os.path.exists(clean_file), 'File public_text_news_clean.csv belum ada! Jalankan make clean-data'; \
df = pd.read_csv(clean_file); \
sample = df.sample(min(10, len(df)), random_state=42); \
print(''); \
print('\033[1;36m======================================================================\033[0m'); \
print('\033[1;33m🔍 SPOT CHECK: 10 SAMPEL ACAK DATASET BERSIH FASE 2                   \033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
[print(f'[{i}] {\"🟢\" if r[\"aceh_confidence\"]==\"high\" else (\"🟡\" if r[\"aceh_confidence\"]==\"medium\" else \"🔴\")} [{r[\"aceh_confidence\"].upper()}] [{r[\"source_portal\"]}] (Word Count: {r[\"word_count\"]})\n    \"{r[\"text\"][:140]}...\"\n') for i, (_, r) in enumerate(sample.iterrows(), 1)]; \
print('\033[1;36m======================================================================\033[0m'); \
print('')"

# ==============================================================================
# MONITORING & OBSERVABILITAS
# ==============================================================================

status:
	@echo ""
	@echo "\033[1;36m📊 RINGKASAN STATUS PIPELINE & DATASET (materi-4/data):\033[0m"
	@$(PYTHON) -c "import os, pandas as pd; \
d = '$(DATA_DIR)'; \
pd_dir = '$(PROCESSED_DIR)'; \
disc = os.path.join(d, 'discovery_articles.csv'); \
res = os.path.join(d, 'resolved_urls.csv'); \
db = os.path.join(d, 'articles_database.csv'); \
para_raw = os.path.join(d, 'paragraphs_raw.csv'); \
para_clean = os.path.join(pd_dir, 'public_text_news_clean.csv'); \
fail = os.path.join(d, 'failed_urls.csv'); \
n_raw = len(pd.read_csv(para_raw)) if os.path.exists(para_raw) else 0; \
n_clean = len(pd.read_csv(para_clean)) if os.path.exists(para_clean) else 0; \
reduct = round((1 - n_clean / n_raw) * 100, 1) if n_raw > 0 and n_clean > 0 else 0; \
print(f'  • Discovery Articles : {len(pd.read_csv(disc)) if os.path.exists(disc) else 0} URL'); \
print(f'  • Resolved URLs      : {len(pd.read_csv(res)) if os.path.exists(res) else 0} URL'); \
print(f'  • Articles Database  : {len(pd.read_csv(db)) if os.path.exists(db) else 0} artikel'); \
print(f'  • Paragraphs Raw (Fase 1)   : {n_raw:,} paragraf'); \
print(f'  • Paragraphs Clean (Fase 2) : {n_clean:,} paragraf (Dibersihkan: {reduct}%)'); \
print(f'  • Failed URLs        : {len(pd.read_csv(fail)) if os.path.exists(fail) else 0} URL')"
	@echo ""

logs:
	@echo "\033[1;36m📝 20 LOG EVENT TERAKHIR:\033[0m"
	@ls -t $(LOGS_DIR)/scraping_*.jsonl 2>/dev/null | head -n 1 | xargs -I {} tail -n 20 {}
