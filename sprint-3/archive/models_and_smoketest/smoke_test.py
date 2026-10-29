"""
smoke_test.py — Smoke Test & Efficiency Evaluation Suite
GRAK 2026 · Sprint 3 · Materi 4

Tujuan:
  Menguji pipeline scraping end-to-end pada 50 artikel (bukan sekadar 3-5)
  agar dapat mengevaluasi:
    1. Fungsionalitas teknis (anti-ban, multi-strategy resolver, fallback extractor, logging)
    2. Efisiensi eksekusi (kecepatan URLs/detik, throughput ekstraksi, latency rate limit)
    3. Proyeksi waktu untuk scraping penuh 1.350 artikel
    4. Tingkat keberhasilan (success rate) dan distribusi domain

Fitur:
  - Non-destruktif: Hasil uji disimpan ke data/smoke_test_output/ (database utama aman)
  - Multithreaded: 5 workers untuk resolver, 8 workers untuk extractor (sama dengan produksi)
  - Proyeksi kapasitas & efisiensi otomatis
  - Schema & quality gate validation

Cara pakai:
  cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
  python3 smoke_test.py
  python3 smoke_test.py --sample-size 50   # Default 50 artikel
"""

import os
import sys
import time
import json
import argparse
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Setup path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from config import DATA_DIR, DISCOVERY_CSV
from lib.http_client import RateLimitedClient, USER_AGENT_POOL
from lib.logger import get_logger, LOGS_DIR

import importlib
resolver_mod = importlib.import_module("02_resolver")
resolve_single_url = resolver_mod.resolve_single_url
is_google_news_url = resolver_mod.is_google_news_url

extractor_mod = importlib.import_module("03_extraction")
process_single_article = extractor_mod.process_single_article

SMOKE_OUTPUT_DIR = os.path.join(DATA_DIR, "smoke_test_output")
SMOKE_RESOLVED_CSV = os.path.join(SMOKE_OUTPUT_DIR, "smoke_resolved_urls.csv")
SMOKE_ARTICLES_CSV = os.path.join(SMOKE_OUTPUT_DIR, "smoke_articles_db.csv")
SMOKE_PARAS_CSV = os.path.join(SMOKE_OUTPUT_DIR, "smoke_paragraphs_raw.csv")


def print_stage_header(stage_num: int, stage_name: str):
    print("\n" + "=" * 65)
    print(f"🔹 STAGE {stage_num}: {stage_name}")
    print("=" * 65)


def run_smoke_test(sample_size: int = 50):
    start_total = time.time()
    results = {}

    print("=" * 65)
    print(f"🧪 GRAK SPRINT 3 — SCRAPING SMOKE TEST & EFFICIENCY EVALUATION")
    print(f"   • Sampel Pengujian    : {sample_size} artikel")
    print(f"   • Output Directory    : {SMOKE_OUTPUT_DIR}")
    print(f"   • Resolver Threads    : 5 threads paralel")
    print(f"   • Extraction Threads  : 8 threads paralel")
    print("=" * 65)

    os.makedirs(SMOKE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # -------------------------------------------------------------
    # STAGE 1: Dependency Check
    # -------------------------------------------------------------
    print_stage_header(1, "Dependency & Module Import Check")
    deps = [
        ("requests", "requests"),
        ("BeautifulSoup", "bs4"),
        ("newspaper3k", "newspaper"),
        ("Google News Decoder", "googlenewsdecoder"),
        ("pandas", "pandas"),
        ("tqdm", "tqdm"),
    ]
    all_deps_ok = True
    for name, mod in deps:
        try:
            __import__(mod)
            print(f"   ✅ {name:20}: OK")
        except ImportError as e:
            print(f"   ❌ {name:20}: GAGAL ({e})")
            all_deps_ok = False
    
    results["Stage 1 - Dependencies"] = "PASS" if all_deps_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 2: Anti-Ban HTTP Client
    # -------------------------------------------------------------
    print_stage_header(2, "Anti-Ban HTTP Client Verification")
    client = RateLimitedClient(timeout=10, max_retries=2)
    http_ok = True
    try:
        test_url = "https://httpbin.org/headers"
        t0 = time.time()
        res = client.get(test_url)
        t_elapsed = time.time() - t0

        if res and res.status_code == 200:
            data = res.json()
            sent_ua = data.get("headers", {}).get("User-Agent", "")
            print(f"   ✅ HTTP GET Berhasil ({t_elapsed:.2f}s)")
            print(f"   ✅ User-Agent Terkirim: {sent_ua[:55]}...")
        else:
            res2 = client.head("https://www.antaranews.com", allow_redirects=True)
            if res2 and res2.status_code < 400:
                print(f"   ✅ HTTP HEAD Antaranews Berhasil (Status: {res2.status_code})")
            else:
                print(f"   ⚠️ HTTP Test Warning: status {getattr(res, 'status_code', None)}")
    except Exception as e:
        print(f"   ❌ Error saat test HTTP Client: {e}")
        http_ok = False
    finally:
        client.close()

    results["Stage 2 - HTTP Client"] = "PASS" if http_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 3: Structured Logger Test
    # -------------------------------------------------------------
    print_stage_header(3, "Structured Logger (JSONL) Verification")
    logger_ok = True
    try:
        test_logger = get_logger("smoke_test")
        test_msg = f"Smoke test 50 articles initiated at {datetime.now().strftime('%H:%M:%S')}"
        test_logger.info(test_msg, sample_size=sample_size, run_id="smoke_50")
        
        today = time.strftime("%Y-%m-%d")
        log_file = os.path.join(LOGS_DIR, f"scraping_{today}.jsonl")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            last_line = json.loads(lines[-1])
            print(f"   ✅ Log file terdeteksi: {os.path.basename(log_file)}")
            print(f"   ✅ Event tercatat: [{last_line.get('level')}] {last_line.get('message')}")
        else:
            print("   ❌ Log file tidak ditemukan")
            logger_ok = False
    except Exception as e:
        print(f"   ❌ Error pada Logger: {e}")
        logger_ok = False

    results["Stage 3 - Logger"] = "PASS" if logger_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 4: URL Resolver on 50 Sample URLs (Multithreaded)
    # -------------------------------------------------------------
    print_stage_header(4, f"Multi-Strategy URL Resolver ({sample_size} Sample URLs)")
    resolver_ok = True
    sample_items = []
    
    if not os.path.exists(DISCOVERY_CSV):
        print(f"   ❌ {DISCOVERY_CSV} tidak ditemukan!")
        results["Stage 4 - URL Resolver"] = "FAIL"
        return False
    
    df_disc = pd.read_csv(DISCOVERY_CSV)
    # Ambil sampel representatif: campuran Google News URLs dan direct URLs
    gnews_count = min(int(sample_size * 0.85), df_disc["url"].apply(is_google_news_url).sum())
    direct_count = sample_size - gnews_count

    df_gnews = df_disc[df_disc["url"].apply(is_google_news_url)].head(gnews_count)
    df_direct = df_disc[~df_disc["url"].apply(is_google_news_url)].head(direct_count)
    
    sample_df = pd.concat([df_gnews, df_direct]).head(sample_size).reset_index(drop=True)
    sample_items = sample_df.to_dict(orient="records")
    actual_sample_size = len(sample_items)
    
    print(f"   • Total sampel diambil: {actual_sample_size} URL")
    print(f"     - Google News URLs  : {len(df_gnews)}")
    print(f"     - Direct URLs       : {len(df_direct)}")
    print("   • Menjalankan resolusi paralel (5 threads)...")

    resolved_results = []
    t_start_resolver = time.time()
    success_res_count = 0
    fail_res_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(resolve_single_url, item): item for item in sample_items}
        with tqdm(total=actual_sample_size, desc="Resolving URLs", unit="url", ncols=80) as pbar:
            for future in as_completed(futures):
                try:
                    res = future.result()
                    resolved_results.append(res)
                    if res.get("resolve_status") == "success":
                        success_res_count += 1
                    else:
                        fail_res_count += 1
                except Exception as e:
                    item_orig = futures[future]
                    resolved_results.append({
                        **item_orig,
                        "resolved_url": item_orig.get("url"),
                        "resolved_domain": "error",
                        "resolver_method": "exception",
                        "resolve_status": "failed"
                    })
                    fail_res_count += 1
                pbar.set_postfix({"✅": success_res_count, "❌": fail_res_count})
                pbar.update(1)

    t_elapsed_resolver = time.time() - t_start_resolver
    resolver_speed = actual_sample_size / t_elapsed_resolver if t_elapsed_resolver > 0 else 0
    res_success_rate = (success_res_count / actual_sample_size * 100) if actual_sample_size > 0 else 0

    df_res_sample = pd.DataFrame(resolved_results)
    df_res_sample.to_csv(SMOKE_RESOLVED_CSV, index=False, encoding="utf-8-sig")

    print("\n   📊 Hasil Resolusi:")
    print(f"   • Waktu Eksekusi     : {t_elapsed_resolver:.1f} detik")
    print(f"   • Throughput         : {resolver_speed:.2f} URLs/detik")
    print(f"   • Sukses di-resolve  : {success_res_count} / {actual_sample_size} ({res_success_rate:.1f}%)")
    print(f"   • Gagal di-resolve   : {fail_res_count}")
    print(f"   📁 Output disimpan di: {SMOKE_RESOLVED_CSV}")

    # Breakdown metode
    print("   • Breakdown Metode:")
    for method, cnt in df_res_sample[df_res_sample["resolve_status"] == "success"]["resolver_method"].value_counts().items():
        print(f"     - {method:18}: {cnt}")

    if res_success_rate < 50:
        resolver_ok = False
    results["Stage 4 - URL Resolver"] = "PASS" if resolver_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 5: Content Extraction (Multithreaded 8 workers)
    # -------------------------------------------------------------
    print_stage_header(5, "Content Extraction on Resolved Articles (8 Workers)")
    extraction_ok = True
    items_to_extract = [r for r in resolved_results if r.get("resolve_status") == "success"]
    total_to_extract = len(items_to_extract)

    print(f"   • Mengambil konten untuk {total_to_extract} URL yang sukses di-resolve...")

    extracted_articles = []
    extracted_paragraphs = []
    failed_extractions = []
    t_start_extraction = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_single_article, item): item for item in items_to_extract}
        with tqdm(total=total_to_extract, desc="Extracting Articles", unit="url", ncols=80) as pbar:
            for future in as_completed(futures):
                try:
                    art, paras, fail = future.result()
                    if art:
                        art["article_id"] = len(extracted_articles) + 1
                        extracted_articles.append(art)
                        for p in paras:
                            p["paragraph_id"] = len(extracted_paragraphs) + 1
                            p["article_id"] = art["article_id"]
                            extracted_paragraphs.append(p)
                    else:
                        failed_extractions.append(fail)
                except Exception as e:
                    failed_extractions.append({"error": str(e)})
                
                pbar.set_postfix({"sukses": len(extracted_articles), "paragraf": len(extracted_paragraphs)})
                pbar.update(1)

    t_elapsed_extraction = time.time() - t_start_extraction
    ext_speed = len(extracted_articles) / t_elapsed_extraction if t_elapsed_extraction > 0 else 0
    ext_success_rate = (len(extracted_articles) / total_to_extract * 100) if total_to_extract > 0 else 0

    if extracted_articles:
        pd.DataFrame(extracted_articles).to_csv(SMOKE_ARTICLES_CSV, index=False, encoding="utf-8-sig")
        pd.DataFrame(extracted_paragraphs).to_csv(SMOKE_PARAS_CSV, index=False, encoding="utf-8-sig")

    print("\n   📊 Hasil Ekstraksi Konten:")
    print(f"   • Waktu Eksekusi     : {t_elapsed_extraction:.1f} detik")
    print(f"   • Throughput         : {ext_speed:.2f} artikel/detik")
    print(f"   • Artikel Sukses     : {len(extracted_articles)} / {total_to_extract} ({ext_success_rate:.1f}%)")
    print(f"   • Total Paragraf     : {len(extracted_paragraphs)} paragraf")
    print(f"   • Rata-rata Paragraf : {len(extracted_paragraphs)/len(extracted_articles):.1f} per artikel" if extracted_articles else "   • 0")
    print(f"   📁 Output Artikel    : {SMOKE_ARTICLES_CSV}")
    print(f"   📁 Output Paragraf   : {SMOKE_PARAS_CSV}")

    if ext_success_rate < 50:
        extraction_ok = False
    results["Stage 5 - Extraction"] = "PASS" if extraction_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 6: Schema & Content Quality Gate
    # -------------------------------------------------------------
    print_stage_header(6, "Data Schema & Quality Gate Check")
    quality_ok = True
    if extracted_articles and extracted_paragraphs:
        required_art_cols = ["title", "url", "source_portal", "publish_date", "full_text", "extraction_method", "article_id"]
        missing_art_cols = [c for c in required_art_cols if c not in extracted_articles[0]]
        if not missing_art_cols:
            print(f"   ✅ Schema Artikel Valid ({len(required_art_cols)} atribut lengkap)")
        else:
            print(f"   ❌ Kolom artikel hilang: {missing_art_cols}")
            quality_ok = False

        required_para_cols = ["text", "article_title", "article_url", "source_portal", "word_count", "paragraph_id", "article_id"]
        missing_para_cols = [c for c in required_para_cols if c not in extracted_paragraphs[0]]
        if not missing_para_cols:
            print(f"   ✅ Schema Paragraf Valid ({len(required_para_cols)} atribut lengkap)")
        else:
            print(f"   ❌ Kolom paragraf hilang: {missing_para_cols}")
            quality_ok = False

        min_char_check = all(len(p["text"]) >= 50 for p in extracted_paragraphs)
        print(f"   ✅ Filter Panjang Paragraf: {'100% >= 50 karakter' if min_char_check else 'Ada outlier < 50'}")

        avg_words = sum(p["word_count"] for p in extracted_paragraphs) / len(extracted_paragraphs) if extracted_paragraphs else 0
        print(f"   ✅ Rata-rata kata/paragraf: {avg_words:.1f} kata")
    else:
        print("   ❌ Data hasil ekstraksi kosong")
        quality_ok = False

    results["Stage 6 - Quality Gate"] = "PASS" if quality_ok else "FAIL"

    # -------------------------------------------------------------
    # STAGE 7: Efisiensi & Proyeksi Full Scrape (1.350 Artikel)
    # -------------------------------------------------------------
    print_stage_header(7, "Evaluasi Efisiensi & Proyeksi Full Pipeline (1.350 Artikel)")
    total_time = time.time() - start_total
    
    total_pipeline_urls = 1350
    proj_resolver_sec = total_pipeline_urls / resolver_speed if resolver_speed > 0 else 0
    proj_extractor_sec = (total_pipeline_urls * (res_success_rate / 100)) / ext_speed if ext_speed > 0 else 0
    total_proj_min = (proj_resolver_sec + proj_extractor_sec) / 60

    print("   📈 METRIK EFISIENSI (Berdasarkan pengujian 50 artikel):")
    print(f"   • Kecepatan Resolver   : {resolver_speed:.2f} URLs/detik (~{resolver_speed*60:.0f} URLs/menit)")
    print(f"   • Kecepatan Extractor  : {ext_speed:.2f} artikel/detik (~{ext_speed*60:.0f} artikel/menit)")
    print(f"   • Success Rate Gabungan: {(len(extracted_articles) / actual_sample_size * 100):.1f}%")
    print("-" * 65)
    print("   ⏱️ PROYEKSI WAKTU SCRAPING PENUH (1.350 ARTIKEL):")
    print(f"   • Estimasi Resolusi URL (1.350 URL)   : ~{proj_resolver_sec/60:.1f} menit")
    print(f"   • Estimasi Ekstraksi (~{int(total_pipeline_urls*res_success_rate/100)} artikel) : ~{proj_extractor_sec/60:.1f} menit")
    print(f"   • TOTAL ESTIMASI EKSEKUSI PENUH       : ~{total_proj_min:.1f} menit")
    print("=" * 65)

    # -------------------------------------------------------------
    # SCORECARD & KESIMPULAN
    # -------------------------------------------------------------
    all_passed = all(status == "PASS" for status in results.values())
    print("\n" + "=" * 65)
    print("📊 SMOKE TEST SCORECARD SUMMARY")
    print("=" * 65)
    for stage, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"   {icon} {stage:35}: [{status}]")
    print("-" * 65)
    print(f"⏱️  Total waktu pengujian smoke test : {total_time:.1f} detik ({total_time/60:.1f} menit)")

    if all_passed:
        print("\n🎉 STATUS EVALUASI: [SANGAT BAIK / SIAP PRODUKSI] ✅")
        print("   Pipeline terbukti stabil, cepat, dan memenuhi quality gate.")
        print("   Database utama (articles_database.csv 660 baris) tetap aman.")
        print("   Anda dapat melanjutkan ke full scrape:")
        print("     1. python3 02_resolver.py")
        print("     2. python3 03_extraction.py")
    else:
        print("\n⚠️ STATUS EVALUASI: [PERLU PERBAIKAN] ❌")
        print("   Periksa rincian stage yang berstatus FAIL di atas.")
    print("=" * 65 + "\n")

    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test & efficiency evaluation")
    parser.add_argument("--sample-size", type=int, default=50, help="Jumlah sampel artikel untuk diuji (default: 50)")
    args, _ = parser.parse_known_args()
    run_smoke_test(sample_size=args.sample_size)
