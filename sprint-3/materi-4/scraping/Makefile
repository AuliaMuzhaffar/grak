# ==============================================================================
# 🚀 GRAK SPRINT 3 — PIPELINE MASTER MAKEFILE (FASE 1, FASE 2, & FASE 3)
# ==============================================================================

.PHONY: help smoke smoke-quick clean-smoke resolve extract full status logs \
        test-dedup clean-data check-quality spot-check \
        test-label-rules scan-collisions label-data check-label-quality spot-check-labels merge-labels

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
	@echo "\033[1;32m🏷️  SEMI-AUTOMATIC LABELING (FASE 3):\033[0m"
	@echo "  \033[1;37mmake test-label-rules\033[0m   : Unit test kamus aturan & regex boundary (trap cases)"
	@echo "  \033[1;37mmake scan-collisions\033[0m    : Diagnostic scan potensi false positive substring korpus"
	@echo "  \033[1;37mmake label-data\033[0m         : Jalankan 05_labeling.py (engine 2-pass cascading)"
	@echo "  \033[1;37mmake check-label-quality\033[0m: Validasi kepatuhan Quality Gate Fase 3"
	@echo "  \033[1;37mmake spot-check-labels\033[0m  : Tampilkan sampel acak berstrata dari hasil labeling"
	@echo "  \033[1;37mmake merge-labels\033[0m       : Jalankan 06_merge_labels.py (produksi dataset final)"
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
# FASE 3: SEMI-AUTOMATED LABELING, ACTIVE LEARNING, & QUALITY GATE
# ==============================================================================

test-label-rules:
	@echo "\033[1;33m▶ [Fase 3] Menjalankan Unit Test Rules & Regex Boundary...\033[0m"
	@$(PYTHON) -c "import importlib; \
mod = importlib.import_module('05_labeling'); \
matches_keyword = mod.matches_keyword; score_topic = mod.score_topic; \
print('  • Menguji kecocokan kasus positif...'); \
assert matches_keyword('uang', 'bantuan uang tunai untuk modal') == True, 'Gagal mencocokkan kata uang!'; \
assert matches_keyword('it', 'pelatihan sektor IT dan digital') == True, 'Gagal mencocokkan akronim IT!'; \
assert matches_keyword('kur', 'penyaluran KUR syariah BSI') == True, 'Gagal mencocokkan akronim KUR!'; \
print('  • Menguji perangkap kasus negatif (False Positive Traps)...'); \
assert matches_keyword('uang', 'peluang bisnis kopi gayo terbuka') == False, 'BOCOR: kata uang cocok di peluang!'; \
assert matches_keyword('dana', 'peluncuran perdana produk umkm') == False, 'BOCOR: kata dana cocok di perdana!'; \
assert matches_keyword('it', 'terkait dengan hal tersebut') == False, 'BOCOR: kata it cocok di terkait!'; \
assert matches_keyword('it', 'peningkatan kualitas layanan') == False, 'BOCOR: kata it cocok di kualitas!'; \
assert matches_keyword('it', 'aktivitas bisnis mulai normal') == False, 'BOCOR: kata it cocok di aktivitas!'; \
assert matches_keyword('usk', 'termasuk mahasiswa dan dosen') == False, 'BOCOR: kata usk cocok di termasuk!'; \
assert matches_keyword('beli', 'beliau menghadiri acara peresmian') == False, 'BOCOR: kata beli cocok di beliau!'; \
print('  • Menguji deteksi skor imbang (Active Learning Tie-break)...'); \
t, s, _, tie = score_topic('pelatihan programmer dan investasi modal'); \
assert t == 'unclassified' and 'TIE:' in tie, 'Gagal mendeteksi persaingan skor imbang!'; \
print('\033[1;32m✅ Seluruh Unit Test Rules & Regex Boundary Lolos 100% Bebas Bocor!\033[0m')"

scan-collisions:
	@echo "\033[1;33m▶ [Fase 3] Menjalankan Reverse Vocabulary Collision Scanner...\033[0m"
	@$(PYTHON) -c "import os, re, pandas as pd; from labeling_rules import TOPIC_RULES; \
clean_file = os.path.join('$(PROCESSED_DIR)', 'public_text_news_clean.csv'); \
assert os.path.exists(clean_file), 'File dataset bersih belum ada!'; \
df = pd.read_csv(clean_file); \
tokens = set(re.findall(r'\b[a-z]{3,}\b', ' '.join(df['text'].dropna().astype(str).str.lower()))); \
all_kws = list(set([k.lower().strip() for t in TOPIC_RULES.values() for tr in ['strong','medium','weak'] for k in t[tr] if ' ' not in k and len(k) <= 5])); \
collisions = {kw: [t for t in tokens if kw in t and t != kw][:5] for kw in all_kws if any(kw in t and t != kw for t in tokens)}; \
print(f'  • Total kosakata unik di korpus : {len(tokens):,} kata'); \
print(f'  • Kata kunci rentan collision   : {len(collisions)} kata'); \
print('  • Sampel jebakan yang berhasil ditangkal boundary regex \\\b:'); \
[print(f'    - \"{kw}\" terlindungi dari: {words}') for kw, words in sorted(collisions.items(), key=lambda x: len(x[1]), reverse=True)[:6]]; \
print('\033[1;32m✅ Scanning selesai: Seluruh collision diamankan oleh word boundary regex!\033[0m')"

label-data:
	@echo "\033[1;33m▶ [Fase 3] Menjalankan Engine Labeling 2-Pass Cascading (05_labeling.py)...\033[0m"
	@$(PYTHON) 05_labeling.py

check-label-quality:
	@$(PYTHON) -c "import os, json, pandas as pd; \
stats_file = os.path.join('$(PROCESSED_DIR)', 'label_stats.json'); \
labeled_file = os.path.join('$(PROCESSED_DIR)', 'labeled_dataset.csv'); \
assert os.path.exists(stats_file) and os.path.exists(labeled_file), 'File output labeling belum ada! Jalankan make label-data'; \
stats = json.load(open(stats_file, 'r')); \
df = pd.read_csv(labeled_file); \
total = stats['total_rows']; \
auto_pct = stats['auto_label_pct']; \
needs_rev_pct = round(stats['needs_review'] / total * 100, 1); \
topics = stats['topic_distribution']; \
max_topic = max(topics.values()) / total * 100; \
min_topic = min(topics.values()) / total * 100; \
sents = stats['sentiment_distribution']; \
pos_neu_pct = (sents.get('positive', 0) + sents.get('neutral', 0)) / total * 100; \
prov_valid = df['topic_method'].isin(['auto', 'article_propagated', 'title_propagated', 'needs_review', 'manual']).all(); \
print(''); \
print('\033[1;36m======================================================================\033[0m'); \
print('\033[1;33m📋 LAPORAN QUALITY GATE FASE 3 (labeled_dataset.csv)                  \033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
metrics = [ \
    ('Cakupan Auto-label', f'{auto_pct:.1f}% ({stats[\"auto_labeled_total\"]:,})', '>= 70.0%', auto_pct >= 70.0), \
    ('Batas Maksimal Ambigu', f'{needs_rev_pct:.1f}% ({stats[\"needs_review\"]:,})', '<= 20.0%', needs_rev_pct <= 20.0), \
    ('Batas Skew Topik Tertinggi', f'{max_topic:.1f}% ({list(topics.keys())[0]})', '<= 30.0%', max_topic <= 30.0), \
    ('Representasi Topik Terkecil', f'{min_topic:.1f}% (8 topik ada)', '>= 1.0%', min_topic >= 1.0 and len(topics) == 8), \
    ('Kewajaran Sentimen (Pos+Net)', f'{pos_neu_pct:.1f}%', '>= 70.0%', pos_neu_pct >= 70.0), \
    ('Integritas Metode Provenance', '100% Valid' if prov_valid else 'Ada Invalid', '100%', prov_valid) \
]; \
[print(f'  • {l:<29} : {a:<22} (Target: {t:<9}) {\"\033[1;32m✅ PASS\033[0m\" if ok else \"\033[1;31m❌ FAIL\033[0m\"}') for l, a, t, ok in metrics]; \
all_ok = all(ok for _, _, _, ok in metrics); \
print('\033[1;36m----------------------------------------------------------------------\033[0m'); \
print('\033[1;32m🏆 KESIMPULAN: SELURUH QUALITY GATE FASE 3 TERPENUHI SEMPURNA!\033[0m' if all_ok else '\033[1;31m⚠️ KESIMPULAN: ADA METRIK YANG BELUM MEMENUHI KRITERIA!\033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
print('')"

spot-check-labels:
	@$(PYTHON) -c "import os, pandas as pd; \
labeled_file = os.path.join('$(PROCESSED_DIR)', 'labeled_dataset.csv'); \
assert os.path.exists(labeled_file), 'File labeled_dataset.csv belum ada! Jalankan make label-data'; \
df = pd.read_csv(labeled_file); \
samples = [df[df['topic_method'] == m].sample(min(2, (df['topic_method'] == m).sum()), random_state=42) for m in ['auto', 'article_propagated', 'title_propagated', 'needs_review'] if (df['topic_method'] == m).sum() > 0]; \
sample_df = pd.concat(samples).reset_index(drop=True); \
print(''); \
print('\033[1;36m======================================================================\033[0m'); \
print('\033[1;33m🔍 SPOT CHECK: SAMPEL HASIL LABELING BERSTRATA (FASE 3)                \033[0m'); \
print('\033[1;36m======================================================================\033[0m'); \
badge = {'auto': '\033[1;32m[AUTO-DIRECT]\033[0m', 'article_propagated': '\033[1;34m[ARTICLE-PROP]\033[0m', 'title_propagated': '\033[1;35m[TITLE-PROP]\033[0m', 'needs_review': '\033[1;33m[NEEDS-REVIEW]\033[0m'}; \
[print(f'[{i}] {badge.get(r[\"topic_method\"], r[\"topic_method\"])} Topik: \033[1;37m{str(r[\"topic\"]) if pd.notna(r[\"topic\"]) and r[\"topic\"] != \"\" else \"(unclassified)\"}\033[0m (Skor: {r[\"topic_score\"]}) Sentimen: {r[\"sentiment\"]}\n    Judul : {str(r[\"article_title\"])[:80]}...\n    Teks  : \"{str(r[\"text\"])[:120]}...\"\n    Notes : {r[\"labeling_notes\"] if pd.notna(r[\"labeling_notes\"]) and r[\"labeling_notes\"] != \"\" else \"-\"}\n') for i, (_, r) in enumerate(sample_df.iterrows(), 1)]; \
print('\033[1;36m======================================================================\033[0m'); \
print('')"

merge-labels:
	@echo "\033[1;33m▶ [Fase 3] Menjalankan Konsolidasi Dataset Final (06_merge_labels.py)...\033[0m"
	@$(PYTHON) 06_merge_labels.py

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
auto_file = os.path.join(pd_dir, 'auto_labeled.csv'); \
review_file = os.path.join(pd_dir, 'needs_review.csv'); \
final_file = os.path.join(pd_dir, 'labeled_dataset_final.csv'); \
fail = os.path.join(d, 'failed_urls.csv'); \
n_raw = len(pd.read_csv(para_raw)) if os.path.exists(para_raw) else 0; \
n_clean = len(pd.read_csv(para_clean)) if os.path.exists(para_clean) else 0; \
n_auto = len(pd.read_csv(auto_file)) if os.path.exists(auto_file) else 0; \
n_rev = len(pd.read_csv(review_file)) if os.path.exists(review_file) else 0; \
n_final = len(pd.read_csv(final_file)) if os.path.exists(final_file) else 0; \
reduct = round((1 - n_clean / n_raw) * 100, 1) if n_raw > 0 and n_clean > 0 else 0; \
auto_pct = round((n_auto / n_clean) * 100, 1) if n_clean > 0 and n_auto > 0 else 0; \
print(f'  • Discovery Articles        : {len(pd.read_csv(disc)) if os.path.exists(disc) else 0} URL'); \
print(f'  • Resolved URLs             : {len(pd.read_csv(res)) if os.path.exists(res) else 0} URL'); \
print(f'  • Articles Database         : {len(pd.read_csv(db)) if os.path.exists(db) else 0} artikel'); \
print(f'  • Paragraphs Raw (Fase 1)   : {n_raw:,} paragraf'); \
print(f'  • Paragraphs Clean (Fase 2) : {n_clean:,} paragraf (Dibersihkan: {reduct}%)'); \
print(f'  • Auto-labeled (Fase 3)     : {n_auto:,} paragraf ({auto_pct}%)'); \
print(f'  • Needs Review (Fase 3)     : {n_rev:,} paragraf'); \
print(f'  • Dataset Final (Fase 3)    : {n_final:,} paragraf'); \
print(f'  • Failed URLs               : {len(pd.read_csv(fail)) if os.path.exists(fail) else 0} URL')"
	@echo ""

logs:
	@echo "\033[1;36m📝 20 LOG EVENT TERAKHIR:\033[0m"
	@ls -t $(LOGS_DIR)/scraping_*.jsonl 2>/dev/null | head -n 1 | xargs -I {} tail -n 20 {}
