# 🔧 Reusable Pipeline: Dari Hardcode ke Config-Driven

> **Level**: Intermediate SWE  
> **Prerequisite**: Python dasar, sudah paham pipeline Sprint 3  
> **Waktu belajar**: 2-3 jam  
> **Kapan mengerjakannya**: SETELAH Sprint 3 selesai. Ini improvement, bukan prioritas Sprint.

---

## 0. Apa Masalahnya Sekarang?

Buka `config.py` kamu sekarang. Di dalamnya ada:

```python
# Hardcoded untuk Aceh
DISCOVERY_QUERIES = [
    "startup Aceh",
    "UMKM digital Banda Aceh",
    "ekosistem startup Aceh",
    ...
]

ACEH_KEYWORDS = [
    "aceh", "banda aceh", "lhokseumawe",
    ...
]
```

**Masalah**: Kalau besok mau riset Yogyakarta, kamu harus:
1. Copy-paste SEMUA file
2. Find-replace "Aceh" → "Yogyakarta" di banyak tempat
3. Ganti keyword satu-satu
4. Doa supaya tidak ada yang kelewat

Ini namanya **hardcoding** — dan ini musuh utama software engineer.

---

## 1. Konsep: Config-Driven Architecture

### Sebelum (Hardcoded)

```
Pipeline
├── config.py          ← "Aceh" tertanam di mana-mana
├── 01_discovery.py    ← Import dari config.py
├── 02_resolver.py     ← Import dari config.py
└── ...
```

Untuk ganti region: copy semua file, edit manual.

### Sesudah (Config-Driven)

```
Pipeline
├── regions/
│   ├── aceh.yaml          ← Semua config Aceh di sini
│   ├── yogyakarta.yaml    ← Semua config Yogya di sini
│   └── makassar.yaml      ← Semua config Makassar di sini
├── pipeline/
│   ├── config.py          ← Baca dari .yaml, TIDAK ada region hardcoded
│   ├── discovery.py       ← Terima config sebagai parameter
│   ├── resolver.py
│   └── ...
└── run_pipeline.py        ← Entry point: --region aceh
```

Untuk ganti region: `python3 run_pipeline.py --region yogyakarta`. **Zero code changes.**

---

## 2. Prerequisite: Apa yang Perlu Kamu Tahu

### 2.1 YAML (data format)

YAML itu seperti JSON tapi lebih mudah dibaca manusia. Contoh:

```yaml
# Ini komentar
name: Aceh
queries:
  - "startup Aceh"
  - "UMKM digital Banda Aceh"
  - "ekosistem startup Aceh"

keywords:
  region:
    - aceh
    - banda aceh
    - lhokseumawe
  
  boilerplate:
    - baca juga
    - baca selengkapnya
```

Install: `pip install pyyaml`

Cara baca di Python:
```python
import yaml

with open("regions/aceh.yaml") as f:
    config = yaml.safe_load(f)

print(config["name"])       # "Aceh"
print(config["queries"][0]) # "startup Aceh"
```

**Kenapa YAML bukan JSON?**
- YAML: support komentar, lebih readable, tidak perlu tanda kutip di mana-mana
- JSON: tidak bisa komentar, banyak kurung kurawal
- Untuk config file, YAML lebih nyaman

### 2.2 argparse (command line arguments)

```python
import argparse

parser = argparse.ArgumentParser(description="GRAK Pipeline")
parser.add_argument("--region", required=True, help="Region name (e.g. aceh)")
parser.add_argument("--phase", type=int, default=0, help="Run specific phase only")
args = parser.parse_args()

print(args.region)  # "aceh"
print(args.phase)   # 0
```

Penggunaan:
```bash
python3 run_pipeline.py --region aceh          # run semua fase
python3 run_pipeline.py --region aceh --phase 1  # run fase 1 saja
```

### 2.3 Dependency Injection (konsep)

Ini bukan library, ini **pola pikir**. Artinya: function TIDAK boleh tahu dari mana datanya — dia terima data sebagai parameter.

```python
# ❌ SEBELUM: function "tahu" bahwa dia untuk Aceh
def discover():
    queries = ["startup Aceh", "UMKM Aceh"]  # hardcoded!
    for q in queries:
        search(q)

# ✅ SESUDAH: function TIDAK tahu region — dia terima config
def discover(config: dict):
    for q in config["queries"]:  # dari parameter, bukan hardcoded
        search(q)
```

Sekarang function yang sama bisa dipakai untuk Aceh, Yogya, atau Mars — tinggal beri config berbeda.

---

## 3. Arsitektur: Bagaimana Ini Bekerja

```
USER menjalankan:
  python3 run_pipeline.py --region aceh --phase 1

                    │
                    ▼
            ┌──────────────┐
            │ run_pipeline  │  1. Baca regions/aceh.yaml
            │   .py         │  2. Buat output dir: output/aceh/
            └──────┬───────┘  3. Jalankan fase yang diminta
                   │
          ┌────────┼────────────┐
          ▼        ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Phase 1  │ │ Phase 2  │ │ Phase 3  │ ...
    │ discovery│ │ cleaning │ │ labeling │
    └──────────┘ └──────────┘ └──────────┘
          │             │           │
          ▼             ▼           ▼
    output/aceh/   output/aceh/  output/aceh/
    discovery.csv  clean.csv     labeled.csv


USER menjalankan lagi:
  python3 run_pipeline.py --region yogyakarta --phase 1

          │
          ▼
    Baca regions/yogyakarta.yaml
    Output ke output/yogyakarta/
    SAMA persis codenya, BEDA confignya
```

---

## 4. Step-by-Step: Cara Refactor

### Step 1: Buat Region Config File

**File**: `regions/aceh.yaml`

```yaml
# ============================================================
# REGION CONFIG: Aceh
# ============================================================
# File ini berisi SEMUA konfigurasi yang spesifik untuk region Aceh.
# Untuk riset region lain, copy file ini dan ubah value-nya.

# Identitas region
name: "Aceh"
slug: "aceh"                    # Untuk nama folder output (huruf kecil, no space)
description: "Ekosistem Startup Aceh 2026"

# ============================================================
# DISCOVERY — Query untuk cari berita
# ============================================================
discovery:
  queries:
    - "startup Aceh"
    - "startup digital Aceh"
    - "ekosistem startup Aceh"
    - "UMKM digital Banda Aceh"
    - "UMKM digital Aceh"
    - "inkubator bisnis Aceh"
    - "akselerator startup Aceh"
    - "investasi startup Aceh"
    - "pendanaan startup Aceh"
    - "transformasi digital Aceh"
    - "ekonomi digital Aceh"
    - "teknologi informasi Aceh"
    - "komunitas startup Banda Aceh"
    - "co-working space Banda Aceh"
    - "digitalisasi UMKM Aceh"
  
  # Google News params
  google_news:
    hl: "id"
    gl: "ID"
    ceid: "ID:id"
  
  # Antara News
  antara:
    enabled: true
    search_url: "https://www.antaranews.com/search?q="

# ============================================================
# KEYWORDS — Untuk filtering dan confidence scoring
# ============================================================
keywords:
  # Keyword yang menandakan text ini tentang region ini
  region:
    - "aceh"
    - "banda aceh"
    - "lhokseumawe"
    - "langsa"
    - "sabang"
    - "meulaboh"
    - "sigli"
    - "bireuen"
    - "takengon"
    - "blangkejeren"
    - "kutacane"
    - "tapaktuan"
    - "subulussalam"
    - "nagan raya"
    - "aceh besar"
    - "pidie"
    - "aceh utara"
    - "aceh timur"
    - "aceh tengah"
    - "bener meriah"
    - "aceh tenggara"
    - "aceh selatan"
    - "aceh barat"
    - "aceh jaya"
    - "simeulue"
    - "NAD"
    - "nanggroe aceh darussalam"
    - "qanun"

# ============================================================
# LABELING — Rules untuk auto-label topic
# ============================================================
# (Topic dan sentiment rules biasanya SAMA untuk semua region,
#  jadi kita taruh di shared config, bukan di sini)

# ============================================================
# SCRAPING — Rate limiting dan anti-ban
# ============================================================
scraping:
  max_workers: 8
  delay_between_queries: 3  # detik
  request_timeout: 15       # detik
  
  # Delay per domain (detik)
  domain_delays:
    "news.google.com": 2
    "antaranews.com": 1
    "kompas.com": 1.5
    "detik.com": 1.5

# ============================================================
# OUTPUT — Lokasi file output
# ============================================================
output:
  base_dir: "output"    # Akan jadi: output/aceh/
```

### Step 2: Buat Config File untuk Region Lain (Contoh)

**File**: `regions/yogyakarta.yaml`

```yaml
name: "Yogyakarta"
slug: "yogyakarta"
description: "Ekosistem Startup Yogyakarta 2026"

discovery:
  queries:
    - "startup Yogyakarta"
    - "startup digital Jogja"
    - "ekosistem startup Yogyakarta"
    - "UMKM digital Yogyakarta"
    - "inkubator bisnis Jogja"
    - "akselerator startup Yogyakarta"
    - "investasi startup Jogja"
    - "ekonomi digital Yogyakarta"
    - "komunitas startup Jogja"
    - "co-working space Yogyakarta"
    - "digitalisasi UMKM Jogja"
  
  google_news:
    hl: "id"
    gl: "ID"
    ceid: "ID:id"
  
  antara:
    enabled: true
    search_url: "https://www.antaranews.com/search?q="

keywords:
  region:
    - "yogyakarta"
    - "jogja"
    - "jogjakarta"
    - "sleman"
    - "bantul"
    - "gunung kidul"
    - "kulon progo"
    - "DIY"
    - "daerah istimewa yogyakarta"
    - "malioboro"
    - "UGM"
    - "UNY"
    - "AMIKOM"
    - "UII"

scraping:
  max_workers: 8
  delay_between_queries: 3
  request_timeout: 15
  domain_delays:
    "news.google.com": 2
    "antaranews.com": 1

output:
  base_dir: "output"
```

**Lihat pola-nya?** Yang BERUBAH hanya:
- `name`, `slug`
- `queries` (keyword search)
- `keywords.region` (nama kota/kabupaten)

Logic pipeline SAMA PERSIS.

### Step 3: Refactor `config.py` — Baca dari YAML

**File**: `pipeline/config.py` (yang baru)

```python
"""
config.py — Config loader yang region-agnostic

SEBELUM: config.py berisi hardcoded value untuk Aceh
SESUDAH: config.py membaca dari regions/*.yaml

CARA PAKAI:
    from config import load_config
    
    cfg = load_config("aceh")         # Baca regions/aceh.yaml
    print(cfg["name"])                 # "Aceh"
    print(cfg["discovery"]["queries"]) # ["startup Aceh", ...]
"""

import os
import yaml


# Path ke folder regions/
REGIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "regions"
)

# Shared config (sama untuk semua region)
SHARED_CONFIG = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
    },
    "google_news_rss_base": "https://news.google.com/rss/search",
    "min_paragraph_length": 50,
    
    # Boilerplate patterns (sama untuk semua region Indonesia)
    "boilerplate_patterns": [
        "baca juga", "baca selengkapnya", "baca artikel",
        "simak breaking news", "ikuti kami di", "google news",
        "download aplikasi", "unduh aplikasi", "advertisement",
        "iklan", "copyright", "hak cipta", "penulis:", "editor:",
        "reporter:", "sumber:", "tag:", "artikel ini telah tayang",
        "bagikan berita ini", "subscribe", "newsletter",
        "all rights reserved", "disclaimer", "kebijakan privasi",
        "hubungi kami", "redaksi", "tentang kami",
        # ... (semua pattern dari config lama)
    ],
}


def load_config(region_slug: str) -> dict:
    """
    Load config untuk region tertentu.
    
    Args:
        region_slug: nama region (e.g., "aceh", "yogyakarta")
    
    Returns:
        Dict berisi merged config (shared + region-specific)
    
    Raises:
        FileNotFoundError: jika file regions/{slug}.yaml tidak ada
    
    Contoh:
        cfg = load_config("aceh")
        cfg["name"]                 → "Aceh"
        cfg["discovery"]["queries"] → ["startup Aceh", ...]
        cfg["keywords"]["region"]   → ["aceh", "banda aceh", ...]
        cfg["headers"]              → dari shared config
    """
    yaml_path = os.path.join(REGIONS_DIR, f"{region_slug}.yaml")
    
    if not os.path.exists(yaml_path):
        available = [f.replace(".yaml", "") for f in os.listdir(REGIONS_DIR) 
                     if f.endswith(".yaml")]
        raise FileNotFoundError(
            f"Region '{region_slug}' tidak ditemukan.\n"
            f"File yang dicari: {yaml_path}\n"
            f"Region yang tersedia: {available}"
        )
    
    with open(yaml_path, encoding="utf-8") as f:
        region_config = yaml.safe_load(f)
    
    # Merge: shared config + region config
    # Region config OVERRIDES shared config jika ada key yang sama
    merged = {**SHARED_CONFIG, **region_config}
    
    # Set output directory: output/{slug}/
    output_base = region_config.get("output", {}).get("base_dir", "output")
    merged["output_dir"] = os.path.join(output_base, region_slug)
    
    return merged


def list_regions() -> list[str]:
    """List semua region yang tersedia."""
    if not os.path.exists(REGIONS_DIR):
        return []
    return [f.replace(".yaml", "") for f in sorted(os.listdir(REGIONS_DIR)) 
            if f.endswith(".yaml")]
```

### Step 4: Refactor Pipeline Scripts — Terima Config

**Sebelum** (hardcoded):
```python
# 01_discovery.py (LAMA)
from config import DISCOVERY_QUERIES, ACEH_KEYWORDS  # ← hardcoded import

def discover():
    for query in DISCOVERY_QUERIES:  # ← langsung pakai global variable
        search(query)
```

**Sesudah** (config-driven):
```python
# pipeline/discovery.py (BARU)

def discover(config: dict) -> pd.DataFrame:
    """
    Discover articles for ANY region.
    
    Args:
        config: Region config dari load_config()
    """
    queries = config["discovery"]["queries"]  # ← dari config, bukan hardcoded
    region_name = config["name"]
    
    print(f"🔍 Discovering articles for: {region_name}")
    
    for query in queries:
        results = search_google_news(query, config)
        # ...
    
    return df
```

**Pola refactor untuk SETIAP file:**

```python
# LAMA:
from config import SOME_HARDCODED_VALUE
def do_something():
    use(SOME_HARDCODED_VALUE)

# BARU:
def do_something(config: dict):
    use(config["some_key"])
```

Itu saja. Satu perubahan: **terima config sebagai parameter, bukan import langsung.**

### Step 5: Buat `run_pipeline.py` — Entry Point

```python
"""
run_pipeline.py — Entry point untuk seluruh pipeline

CARA PAKAI:
  # Jalankan semua fase untuk region Aceh:
  python3 run_pipeline.py --region aceh

  # Jalankan fase tertentu saja:
  python3 run_pipeline.py --region aceh --phase 1
  python3 run_pipeline.py --region aceh --phase 2

  # Jalankan untuk region lain:
  python3 run_pipeline.py --region yogyakarta

  # List semua region yang tersedia:
  python3 run_pipeline.py --list-regions
"""

import argparse
import os
import sys
from datetime import datetime

from pipeline.config import load_config, list_regions


def run_phase_1(config: dict):
    """Discovery + URL Resolution + Extraction."""
    from pipeline.discovery import discover
    from pipeline.resolver import resolve_urls
    from pipeline.extraction import extract_articles
    
    print(f"\n{'='*60}")
    print(f"📡 FASE 1: Scraping — {config['name']}")
    print(f"{'='*60}")
    
    df_urls = discover(config)
    df_resolved = resolve_urls(df_urls, config)
    df_articles = extract_articles(df_resolved, config)
    
    # Simpan ke output/{region}/
    output_dir = config["output_dir"]
    df_articles.to_csv(
        os.path.join(output_dir, "articles_raw.csv"),
        index=False, encoding="utf-8-sig"
    )
    print(f"✅ Fase 1 selesai: {len(df_articles)} articles")


def run_phase_2(config: dict):
    """Cleaning & Deduplication."""
    from pipeline.cleaning import clean_dataset
    
    print(f"\n{'='*60}")
    print(f"🧹 FASE 2: Cleaning — {config['name']}")
    print(f"{'='*60}")
    
    input_path = os.path.join(config["output_dir"], "articles_raw.csv")
    df_clean = clean_dataset(input_path, config)
    
    df_clean.to_csv(
        os.path.join(config["output_dir"], "clean.csv"),
        index=False, encoding="utf-8-sig"
    )
    print(f"✅ Fase 2 selesai: {len(df_clean)} clean paragraphs")


def run_phase_3(config: dict):
    """Labeling."""
    from pipeline.labeling import auto_label
    
    print(f"\n{'='*60}")
    print(f"🏷️  FASE 3: Labeling — {config['name']}")
    print(f"{'='*60}")
    
    input_path = os.path.join(config["output_dir"], "clean.csv")
    df_labeled = auto_label(input_path, config)
    
    df_labeled.to_csv(
        os.path.join(config["output_dir"], "labeled.csv"),
        index=False, encoding="utf-8-sig"
    )
    print(f"✅ Fase 3 selesai: {len(df_labeled)} labeled paragraphs")


def run_phase_4(config: dict):
    """ML Model Training."""
    from pipeline.training import train_model
    
    print(f"\n{'='*60}")
    print(f"🤖 FASE 4: ML Training — {config['name']}")
    print(f"{'='*60}")
    
    input_path = os.path.join(config["output_dir"], "labeled.csv")
    models_dir = os.path.join(config["output_dir"], "models")
    train_model(input_path, models_dir, config)
    
    print(f"✅ Fase 4 selesai: models saved to {models_dir}")


def run_phase_5(config: dict):
    """Dashboard Generation."""
    from pipeline.dashboard import generate_dashboard
    
    print(f"\n{'='*60}")
    print(f"📊 FASE 5: Dashboard — {config['name']}")
    print(f"{'='*60}")
    
    input_path = os.path.join(config["output_dir"], "labeled.csv")
    dashboard_path = os.path.join(config["output_dir"], "dashboard")
    generate_dashboard(input_path, dashboard_path, config)
    
    print(f"✅ Fase 5 selesai: {dashboard_path}/index.html")


PHASES = {
    1: ("Scraping", run_phase_1),
    2: ("Cleaning", run_phase_2),
    3: ("Labeling", run_phase_3),
    4: ("ML Training", run_phase_4),
    5: ("Dashboard", run_phase_5),
}


def main():
    parser = argparse.ArgumentParser(
        description="GRAK Ecosystem Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python3 run_pipeline.py --region aceh           # Semua fase
  python3 run_pipeline.py --region aceh --phase 2  # Fase 2 saja
  python3 run_pipeline.py --list-regions           # List region
        """
    )
    parser.add_argument("--region", type=str, help="Region slug (e.g., aceh)")
    parser.add_argument("--phase", type=int, choices=[1,2,3,4,5],
                        help="Run specific phase only")
    parser.add_argument("--list-regions", action="store_true",
                        help="List available regions")
    
    args = parser.parse_args()
    
    # List regions
    if args.list_regions:
        regions = list_regions()
        print("Available regions:")
        for r in regions:
            print(f"  • {r}")
        return
    
    if not args.region:
        parser.print_help()
        return
    
    # Load config
    config = load_config(args.region)
    
    # Create output directory
    os.makedirs(config["output_dir"], exist_ok=True)
    
    print(f"🚀 GRAK Pipeline — {config['name']}")
    print(f"   Output: {config['output_dir']}/")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Run phase(s)
    if args.phase:
        name, func = PHASES[args.phase]
        func(config)
    else:
        for phase_num in sorted(PHASES.keys()):
            name, func = PHASES[phase_num]
            func(config)
    
    print(f"\n🎉 Pipeline selesai untuk {config['name']}!")


if __name__ == "__main__":
    main()
```

---

## 5. Struktur Folder Akhir

```
grak-pipeline/                          # ← nama baru, bukan "sprint-3"
├── run_pipeline.py                     # Entry point
├── requirements.txt                    # Dependencies
├── README.md                          # Dokumentasi
│
├── regions/                            # Config per region
│   ├── aceh.yaml
│   ├── yogyakarta.yaml
│   └── makassar.yaml
│
├── pipeline/                           # Logic (TIDAK ADA hardcoded region)
│   ├── __init__.py
│   ├── config.py                       # Config loader
│   ├── discovery.py                    # Fase 1a
│   ├── resolver.py                     # Fase 1b
│   ├── extraction.py                   # Fase 1c
│   ├── cleaning.py                     # Fase 2
│   ├── labeling.py                     # Fase 3
│   ├── labeling_rules.py              # Rules (shared, semua region sama)
│   ├── training.py                     # Fase 4
│   ├── dashboard.py                    # Fase 5
│   └── lib/
│       ├── __init__.py
│       ├── http_client.py
│       ├── logger.py
│       └── dedup.py
│
├── output/                             # Output per region (auto-generated)
│   ├── aceh/
│   │   ├── articles_raw.csv
│   │   ├── clean.csv
│   │   ├── labeled.csv
│   │   ├── models/
│   │   └── dashboard/
│   └── yogyakarta/
│       ├── articles_raw.csv
│       └── ...
│
└── data/                               # Shared data
    └── interviews/
```

---

## 6. Prinsip-Prinsip yang Kamu Pelajari

### Prinsip 1: Separation of Concerns (SoC)

```
Config (APA)     → regions/aceh.yaml     "Scrape apa? Keyword apa?"
Logic (BAGAIMANA) → pipeline/*.py         "Bagaimana cara scrape?"
Output (HASIL)    → output/aceh/          "Simpan di mana?"
```

Tiga hal ini TERPISAH. Ganti config → output berubah. Logic TIDAK perlu berubah.

### Prinsip 2: Don't Repeat Yourself (DRY)

```
❌ LAMA: 01_discovery.py, 02_extraction.py, 03_cleaning.py
         Setiap file import config berbeda, ada kode yang diulang

✅ BARU: Semua function terima `config: dict`
         Satu config loader, satu set functions, banyak region
```

### Prinsip 3: Single Responsibility

```
config.py    → HANYA load config, tidak ada logic bisnis
discovery.py → HANYA discovery, tidak ada cleaning
cleaning.py  → HANYA cleaning, tidak ada labeling
```

Setiap file punya SATU tanggung jawab.

### Prinsip 4: Open-Closed Principle

```
Pipeline TERBUKA untuk ekstensi (tambah region baru = tambah .yaml)
Pipeline TERTUTUP untuk modifikasi (tidak perlu edit code untuk ganti region)
```

---

## 7. Cara Memulai Refactor (Urutan)

> ⚠️ **JANGAN refactor sekarang.** Selesaikan Sprint 3 dulu dengan code yang ada.
> Refactor ini untuk SETELAH Sprint 3 selesai.

Kalau sudah siap:

```
Urutan refactor (dari yang paling mudah):

1. Buat regions/aceh.yaml
   → Pindahkan semua hardcoded values ke sini
   → Pastikan code lama MASIH JALAN (belum ganti import)

2. Buat pipeline/config.py dengan load_config()
   → Test: python3 -c "from pipeline.config import load_config; print(load_config('aceh'))"

3. Refactor SATU script dulu (mulai dari yang paling sederhana)
   → Misalnya 04_cleaning.py → pipeline/cleaning.py
   → Ubah: function terima config sebagai parameter
   → Test: pastikan output SAMA dengan sebelum refactor

4. Refactor script lainnya satu per satu
   → SELALU test setelah setiap refactor
   → Bandingkan output baru vs lama — harus IDENTIK

5. Buat run_pipeline.py
   → Hubungkan semua phase

6. Test end-to-end:
   → python3 run_pipeline.py --region aceh
   → Bandingkan output dengan pipeline lama

7. Buat region baru untuk validasi:
   → Buat regions/yogyakarta.yaml
   → python3 run_pipeline.py --region yogyakarta
   → Apakah jalan tanpa error?
```

### Golden Rule Refactoring:

> **"Make it work, make it right, make it fast."**
> 
> Kamu sudah di tahap "make it work" (Sprint 3 pipeline jalan).
> Refactor ini adalah "make it right".
> Optimization (async, caching) nanti kalau perlu = "make it fast".

---

## 8. Bonus: Gimana Kalau Mau Tambah Region Baru?

Sesudah refactor, workflow menambah region baru:

```bash
# 1. Copy template
cp regions/aceh.yaml regions/makassar.yaml

# 2. Edit: ganti queries dan keywords
code regions/makassar.yaml

# 3. Jalankan
python3 run_pipeline.py --region makassar

# SELESAI. Zero code changes. 🎉
```

Waktu yang dibutuhkan: **15 menit** (edit YAML) vs **2 jam** (copy-paste dan find-replace seluruh codebase).

Ini yang membedakan engineer yang **koding** vs engineer yang **membangun sistem**.
