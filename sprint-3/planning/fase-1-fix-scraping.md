# Fase 1: Fix & Refactor Scraping Pipeline

> **Estimasi waktu**: 1.5 - 2 hari kerja  
> **Prioritas**: 🔴 P0 — Harus selesai pertama  
> **Prasyarat**: Tidak ada (fase pertama)  
> **Output**: Data artikel bertambah dari 660 → ~1,000+ artikel  

---

## 🎯 Tujuan Fase Ini

1. **Fix root cause kegagalan 690 URL** — 90% gagal karena Google News decoder tidak bisa resolve URL
2. **Buat shared HTTP client** — Anti-ban: rate limiting, rotating user-agent, exponential backoff
3. **Refactor extraction** — Checkpoint/resume, proper error handling, structured logging
4. **Re-run extraction pada URL yang gagal** — Target: success rate naik dari 49% ke ≥80%

---

## 📋 Daftar File yang Dibuat/Diubah

| Action | File Path | Deskripsi |
|--------|-----------|-----------|
| **[NEW]** | `scraping/lib/__init__.py` | Package marker |
| **[NEW]** | `scraping/lib/http_client.py` | HTTP session pool + rate limiter + rotating UA |
| **[NEW]** | `scraping/lib/logger.py` | Structured logging ke file + console |
| **[NEW]** | `scraping/02_resolver.py` | Multi-strategy Google News URL resolver |
| **[MODIFY]** | `scraping/03_extraction.py` | Refactor: pakai shared http_client, checkpoint |
| **[MODIFY]** | `scraping/config.py` | Tambah konfigurasi baru |

---

## Step 1: Buat Folder Struktur

### 1.1 Buat folder `lib/`

```bash
# Jalankan dari terminal:
mkdir -p /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping/lib
mkdir -p /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/logs
```

### 1.2 Buat `lib/__init__.py`

**File**: `sprint-3/materi-4/scraping/lib/__init__.py`

```python
"""
lib/ — Shared utilities untuk scraping pipeline GRAK 2026
"""
```

---

## Step 2: Buat `lib/http_client.py` — Anti-Ban HTTP Client

**File**: `sprint-3/materi-4/scraping/lib/http_client.py`

### Kenapa file ini penting:
- **Rate limiting per domain** — Tidak mengirim terlalu banyak request ke satu server
- **Rotating User-Agent** — Setiap request pakai UA browser berbeda agar tidak terdeteksi bot
- **Exponential backoff** — Kalau server error, tunggu makin lama sebelum retry
- **Connection pooling** — Reuse koneksi TCP, lebih cepat dari `requests.get()` bare

### Code lengkap:

```python
"""
lib/http_client.py — HTTP client dengan anti-ban features
GRAK 2026 · Sprint 3

Features:
  - Rate limiting per domain (max N requests/detik per domain)
  - Rotating User-Agent (10 UA browser asli)
  - Exponential backoff saat error (retry max 3x)
  - Connection pooling via requests.Session
  - Timeout management
"""

import time
import random
import threading
from urllib.parse import urlparse
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# USER-AGENT POOL — 10 UA dari browser asli (Chrome, Firefox, Safari)
# ============================================================
USER_AGENT_POOL = [
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]

# Rate limit per domain (detik antar request)
DEFAULT_DOMAIN_DELAYS = {
    "antaranews.com": 1.5,
    "aceh.antaranews.com": 1.5,
    "tribunnews.com": 2.0,
    "aceh.tribunnews.com": 2.0,
    "news.google.com": 1.0,
    "komdigi.go.id": 2.0,
    "default": 1.0,
}


class RateLimitedClient:
    """
    HTTP client yang aman dari ban.
    
    Cara pakai:
        client = RateLimitedClient()
        response = client.get("https://antaranews.com/berita/123")
        # Otomatis:
        #   - Pakai random User-Agent
        #   - Tunggu sesuai rate limit domain
        #   - Retry 3x kalau error
        #   - Connection pooling
    """
    
    def __init__(
        self,
        domain_delays: dict[str, float] | None = None,
        timeout: int = 20,
        max_retries: int = 3,
    ):
        """
        Args:
            domain_delays: Dict domain -> delay (detik). Default pakai DEFAULT_DOMAIN_DELAYS.
            timeout: Timeout per request dalam detik.
            max_retries: Jumlah retry kalau request gagal.
        """
        self.domain_delays = domain_delays or DEFAULT_DOMAIN_DELAYS
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Track waktu terakhir request per domain (thread-safe)
        self._last_request_time: dict[str, float] = {}
        self._lock = threading.Lock()
        
        # Buat session dengan connection pooling
        self.session = requests.Session()
        
        # Setup retry adapter (retry otomatis untuk 500, 502, 503, 504)
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1.0,  # wait 1s, 2s, 4s
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,    # max 20 koneksi berbeda
            pool_maxsize=20,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain dari URL."""
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "unknown"
    
    def _get_delay(self, domain: str) -> float:
        """Ambil delay untuk domain tertentu."""
        # Cek exact match
        if domain in self.domain_delays:
            return self.domain_delays[domain]
        # Cek partial match (e.g., "aceh.tribunnews.com" matches "tribunnews.com")
        for key, delay in self.domain_delays.items():
            if key in domain:
                return delay
        return self.domain_delays.get("default", 1.0)
    
    def _wait_for_rate_limit(self, domain: str):
        """Tunggu sampai boleh request ke domain ini."""
        delay = self._get_delay(domain)
        
        with self._lock:
            now = time.time()
            last_time = self._last_request_time.get(domain, 0)
            elapsed = now - last_time
            
            if elapsed < delay:
                wait_time = delay - elapsed
                # Tambah sedikit jitter (random 0-0.5 detik) agar tidak terlalu predictable
                wait_time += random.uniform(0, 0.5)
                time.sleep(wait_time)
            
            self._last_request_time[domain] = time.time()
    
    def _get_random_headers(self) -> dict:
        """Generate headers dengan random User-Agent."""
        return {
            "User-Agent": random.choice(USER_AGENT_POOL),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }
    
    def get(
        self,
        url: str,
        allow_redirects: bool = True,
        extra_headers: dict | None = None,
    ) -> Optional[requests.Response]:
        """
        HTTP GET dengan rate limiting + rotating UA + retry.
        
        Args:
            url: URL yang mau di-GET
            allow_redirects: Follow redirect atau tidak
            extra_headers: Header tambahan (opsional)
            
        Returns:
            requests.Response jika berhasil, None jika gagal
        """
        domain = self._get_domain(url)
        
        # Tunggu rate limit
        self._wait_for_rate_limit(domain)
        
        # Siapkan headers
        headers = self._get_random_headers()
        if extra_headers:
            headers.update(extra_headers)
        
        # Coba request dengan backoff manual untuk 429
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects,
                )
                
                # Handle 429 Too Many Requests
                if response.status_code == 429:
                    wait = (2 ** attempt) * 10 + random.uniform(0, 5)  # 10s, 25s, 45s
                    time.sleep(wait)
                    continue
                
                # Handle 403 Forbidden (mungkin IP blocked)
                if response.status_code == 403:
                    # Ganti UA dan coba lagi
                    headers["User-Agent"] = random.choice(USER_AGENT_POOL)
                    wait = (2 ** attempt) * 5 + random.uniform(0, 3)
                    time.sleep(wait)
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return None
                
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return None
                
            except Exception:
                return None
        
        return None
    
    def head(
        self,
        url: str,
        allow_redirects: bool = True,
    ) -> Optional[requests.Response]:
        """
        HTTP HEAD — Hanya ambil header, tidak download body.
        Berguna untuk follow redirect tanpa download konten.
        """
        domain = self._get_domain(url)
        self._wait_for_rate_limit(domain)
        
        headers = self._get_random_headers()
        
        try:
            return self.session.head(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=allow_redirects,
            )
        except Exception:
            return None
    
    def close(self):
        """Tutup session dan release resources."""
        self.session.close()
```

### Verifikasi Step 2:
```bash
# Test import dari terminal:
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "from lib.http_client import RateLimitedClient; c = RateLimitedClient(); print('✅ HTTP Client OK'); c.close()"
```

**Output yang diharapkan**: `✅ HTTP Client OK`

---

## Step 3: Buat `lib/logger.py` — Structured Logging

**File**: `sprint-3/materi-4/scraping/lib/logger.py`

### Kenapa file ini penting:
- Semua `print()` di script lama hilang setelah terminal ditutup
- Dengan logger, setiap event tersimpan di file `.jsonl` yang bisa di-review kapanpun
- Format JSON mudah di-parse untuk analisis error pattern

### Code lengkap:

```python
"""
lib/logger.py — Structured logging untuk scraping pipeline
GRAK 2026 · Sprint 3

Output: logs/scraping_YYYY-MM-DD.jsonl (satu baris JSON per event)

Cara pakai:
    from lib.logger import get_logger
    logger = get_logger("02_resolver")
    
    logger.info("Resolving URL", url="https://...")
    logger.error("Failed to resolve", url="https://...", error="timeout")
"""

import os
import json
import logging
from datetime import datetime


# Folder logs
LOGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "logs"
)


class JSONFormatter(logging.Formatter):
    """Format log sebagai JSON per baris."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Tambahkan extra fields (url, error, count, dll)
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """
    Logger yang output ke:
    1. Console (format readable)
    2. File JSON Lines (format machine-readable)
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Hindari duplicate handler
        if self.logger.handlers:
            return
        
        # Console handler (human readable)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s — %(message)s",
            datefmt="%H:%M:%S"
        ))
        self.logger.addHandler(console)
        
        # File handler (JSON Lines)
        os.makedirs(LOGS_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(LOGS_DIR, f"scraping_{today}.jsonl")
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal: log with extra data."""
        record = self.logger.makeRecord(
            self.name, level, "", 0, message, (), None
        )
        record.extra_data = kwargs
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        """Log informasi biasa."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning (tidak fatal, tapi perlu perhatian)."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error (operasi gagal)."""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log detail teknis (hanya muncul di file, bukan console)."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log operasi berhasil (sebagai INFO dengan tag)."""
        self._log(logging.INFO, f"✅ {message}", **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Factory function untuk buat logger."""
    return StructuredLogger(name)
```

### Verifikasi Step 3:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 -c "
from lib.logger import get_logger
log = get_logger('test')
log.info('Hello world', url='https://example.com')
log.error('Something failed', error='timeout', retry=3)
print('✅ Logger OK — cek file di ../logs/')
"
```

**Output yang diharapkan**: Log muncul di console + file `logs/scraping_YYYY-MM-DD.jsonl` terbuat.

---

## Step 4: Buat `02_resolver.py` — Multi-Strategy URL Resolver ⭐ KUNCI

**File**: `sprint-3/materi-4/scraping/02_resolver.py`

### Kenapa ini paling penting:
- 621 dari 690 URL gagal karena masih berbentuk `https://news.google.com/rss/articles/CB...`
- Script lama hanya punya 1 metode resolve. Script baru punya 4 metode waterfall.

### Strategi resolver (urutan prioritas):

```
1. googlenewsdecoder library  → Tercepat, tapi sering gagal
2. HTTP HEAD follow redirect  → Follow redirect chain, ambil final URL
3. HTTP GET follow redirect   → Sama tapi download full body  
4. HTML meta-refresh parse    → Parse <meta http-equiv="refresh" content="...url=REAL_URL">
```

### Code lengkap:

```python
"""
02_resolver.py — Multi-strategy Google News URL Resolver
GRAK 2026 · Sprint 3

MASALAH:
  Google News RSS memberikan URL dalam format:
    https://news.google.com/rss/articles/CBMi...
  
  URL ini adalah encoded redirect. Untuk mendapatkan URL berita asli,
  kita perlu "decode" atau "resolve" URL tersebut.

STRATEGI (waterfall — coba satu per satu sampai berhasil):
  1. googlenewsdecoder library
  2. HTTP HEAD follow redirect
  3. HTTP GET follow redirect  
  4. HTML meta-refresh tag parse

CARA PAKAI:
  python3 02_resolver.py

INPUT:
  → data/discovery_articles.csv (dari 01_discovery.py)

OUTPUT:
  → data/resolved_urls.csv (URL asli + domain + method resolver)
  → data/resolve_failed.csv (URL yang tetap gagal setelah semua strategi)

PRASYARAT:
  pip install googlenewsdecoder requests beautifulsoup4 pandas tqdm
"""

import os
import sys
import re
import time
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, DISCOVERY_CSV
from lib.http_client import RateLimitedClient
from lib.logger import get_logger

# Output files
RESOLVED_CSV = os.path.join(DATA_DIR, "resolved_urls.csv")
RESOLVE_FAILED_CSV = os.path.join(DATA_DIR, "resolve_failed.csv")

# Logger
log = get_logger("02_resolver")

# HTTP Client (shared, thread-safe)
http = RateLimitedClient(timeout=15, max_retries=2)

# Import googlenewsdecoder (opsional)
try:
    from googlenewsdecoder import gnewsdecoder
    HAS_GNEWS = True
except ImportError:
    HAS_GNEWS = False
    log.warning("googlenewsdecoder not installed, skipping strategy 1")


def is_google_news_url(url: str) -> bool:
    """Cek apakah URL masih link Google News yang perlu di-resolve."""
    return "news.google.com" in url


def extract_domain(url: str) -> str:
    """Ambil nama domain bersih dari URL."""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return "unknown"


def strategy_1_gnewsdecoder(url: str) -> str | None:
    """
    Strategy 1: Pakai googlenewsdecoder library.
    Paling cepat tapi sering gagal.
    """
    if not HAS_GNEWS:
        return None
    try:
        result = gnewsdecoder(url)
        if result.get("status") and result.get("decoded_url"):
            decoded = result["decoded_url"]
            if not is_google_news_url(decoded):
                return decoded
    except Exception:
        pass
    return None


def strategy_2_head_redirect(url: str) -> str | None:
    """
    Strategy 2: HTTP HEAD dan follow redirect chain.
    Lebih cepat dari GET karena tidak download body.
    """
    try:
        response = http.head(url, allow_redirects=True)
        if response and not is_google_news_url(response.url):
            return response.url
    except Exception:
        pass
    return None


def strategy_3_get_redirect(url: str) -> str | None:
    """
    Strategy 3: HTTP GET dan follow redirect chain.
    Download full body tapi lebih reliable dari HEAD.
    """
    try:
        response = http.get(url, allow_redirects=True)
        if response and not is_google_news_url(response.url):
            return response.url
    except Exception:
        pass
    return None


def strategy_4_meta_refresh(url: str) -> str | None:
    """
    Strategy 4: Parse HTML body untuk cari <meta http-equiv="refresh">.
    Beberapa redirect Google News pakai meta refresh tag.
    
    Contoh:
    <meta http-equiv="refresh" content="0;url=https://real-news.com/article/123">
    """
    try:
        response = http.get(url, allow_redirects=False)
        if response is None:
            return None
        
        html = response.text[:5000]  # Hanya parse awal, hemat memory
        
        # Cari meta refresh
        match = re.search(
            r'<meta[^>]*http-equiv=["\']?refresh["\']?[^>]*content=["\']?\d+;\s*url=([^"\'>\s]+)',
            html,
            re.IGNORECASE
        )
        if match:
            target_url = match.group(1)
            if not is_google_news_url(target_url):
                return target_url
        
        # Cari JavaScript redirect
        match = re.search(
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            html,
            re.IGNORECASE
        )
        if match:
            target_url = match.group(1)
            if not is_google_news_url(target_url) and target_url.startswith("http"):
                return target_url
                
    except Exception:
        pass
    return None


def resolve_single_url(row: dict) -> dict:
    """
    Resolve satu URL melalui 4 strategi waterfall.
    
    Args:
        row: dict dari DataFrame discovery (harus punya key 'url')
    
    Returns:
        dict dengan key tambahan: resolved_url, resolved_domain, resolver_method, resolve_status
    """
    raw_url = row["url"]
    result = dict(row)  # Copy semua field asli
    
    # Jika bukan Google News URL, langsung return (sudah resolved)
    if not is_google_news_url(raw_url):
        result["resolved_url"] = raw_url
        result["resolved_domain"] = extract_domain(raw_url)
        result["resolver_method"] = "already_resolved"
        result["resolve_status"] = "success"
        return result
    
    # Coba 4 strategi berurutan
    strategies = [
        ("gnewsdecoder", strategy_1_gnewsdecoder),
        ("head_redirect", strategy_2_head_redirect),
        ("get_redirect", strategy_3_get_redirect),
        ("meta_refresh", strategy_4_meta_refresh),
    ]
    
    for method_name, strategy_fn in strategies:
        resolved = strategy_fn(raw_url)
        if resolved:
            result["resolved_url"] = resolved
            result["resolved_domain"] = extract_domain(resolved)
            result["resolver_method"] = method_name
            result["resolve_status"] = "success"
            log.debug(
                f"Resolved via {method_name}",
                raw_url=raw_url[:80],
                resolved=resolved[:80],
            )
            return result
    
    # Semua strategi gagal
    result["resolved_url"] = raw_url  # Tetap simpan URL asli
    result["resolved_domain"] = "news.google.com"
    result["resolver_method"] = "none"
    result["resolve_status"] = "failed"
    log.warning("All strategies failed", raw_url=raw_url[:80])
    return result


def main():
    # ===== Load Discovery CSV =====
    if not os.path.exists(DISCOVERY_CSV):
        print(f"❌ File tidak ditemukan: {DISCOVERY_CSV}")
        print("   Jalankan 01_discovery.py terlebih dahulu!")
        return
    
    df = pd.read_csv(DISCOVERY_CSV)
    total = len(df)
    
    # Hitung berapa yang perlu di-resolve
    needs_resolve = df["url"].apply(is_google_news_url).sum()
    already_ok = total - needs_resolve
    
    print("=" * 65)
    print("🔗 URL RESOLVER — Multi-Strategy Google News URL Decoder")
    print(f"   • Total URL           : {total}")
    print(f"   • Perlu resolve       : {needs_resolve} (Google News URLs)")
    print(f"   • Sudah OK            : {already_ok} (URL langsung)")
    print(f"   • Google News Decoder : {'✅ AKTIF' if HAS_GNEWS else '⚠️ TIDAK ADA'}")
    print(f"   • Max workers         : 5 threads")
    print("=" * 65)
    print()
    
    log.info(
        "Starting URL resolution",
        total=total,
        needs_resolve=needs_resolve,
    )
    
    # ===== Resolve URLs dengan ThreadPoolExecutor =====
    items = df.to_dict(orient="records")
    results = []
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(resolve_single_url, item): item for item in items}
        
        with tqdm(total=total, desc="Resolving URLs", unit="url", ncols=85) as pbar:
            success_count = 0
            fail_count = 0
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["resolve_status"] == "success":
                        success_count += 1
                    else:
                        fail_count += 1
                        
                except Exception as e:
                    original = futures[future]
                    results.append({
                        **original,
                        "resolved_url": original["url"],
                        "resolved_domain": "error",
                        "resolver_method": "exception",
                        "resolve_status": "failed",
                    })
                    fail_count += 1
                
                pbar.set_postfix({"✅": success_count, "❌": fail_count})
                pbar.update(1)
    
    elapsed = time.time() - start_time
    
    # ===== Simpan Hasil =====
    df_results = pd.DataFrame(results)
    
    # Split: sukses dan gagal
    df_success = df_results[df_results["resolve_status"] == "success"].copy()
    df_failed = df_results[df_results["resolve_status"] == "failed"].copy()
    
    # Deduplicate berdasarkan resolved_url
    before_dedup = len(df_success)
    df_success = df_success.drop_duplicates(subset=["resolved_url"], keep="first")
    after_dedup = len(df_success)
    
    # Simpan
    os.makedirs(DATA_DIR, exist_ok=True)
    df_success.to_csv(RESOLVED_CSV, index=False, encoding="utf-8-sig")
    if len(df_failed) > 0:
        df_failed.to_csv(RESOLVE_FAILED_CSV, index=False, encoding="utf-8-sig")
    
    # ===== Ringkasan =====
    print()
    print("=" * 65)
    print("✅ URL RESOLUTION SELESAI!")
    print(f"   • Waktu             : {elapsed:.1f} detik ({elapsed/60:.1f} menit)")
    print(f"   • Berhasil resolve  : {len(df_success)} URL")
    print(f"   • Gagal resolve     : {len(df_failed)} URL")
    print(f"   • Duplikat dihapus  : {before_dedup - after_dedup}")
    print("=" * 65)
    print()
    
    # Breakdown per resolver method
    print("📊 Breakdown per metode resolver:")
    method_counts = df_success["resolver_method"].value_counts()
    for method, count in method_counts.items():
        print(f"   {method}: {count}")
    print()
    
    # Breakdown per domain (top 15)
    print("📊 Breakdown per domain (top 15):")
    domain_counts = df_success["resolved_domain"].value_counts()
    for domain, count in domain_counts.head(15).items():
        print(f"   {domain}: {count}")
    print()
    
    print(f"📁 Resolved URLs : {RESOLVED_CSV}")
    if len(df_failed) > 0:
        print(f"📁 Failed URLs   : {RESOLVE_FAILED_CSV}")
    print()
    print("▶️  Langkah selanjutnya: jalankan 'python3 03_extraction.py'")
    print("=" * 65)
    
    log.info(
        "Resolution completed",
        success=len(df_success),
        failed=len(df_failed),
        elapsed_sec=round(elapsed, 1),
    )


if __name__ == "__main__":
    main()
```

### Verifikasi Step 4:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 02_resolver.py
```

**Output yang diharapkan**: 
- Progress bar menunjukkan resolving URLs
- `resolved_urls.csv` terbuat di `data/`
- Success rate ≥80% dari total URL
- Breakdown per resolver method dan per domain

---

## Step 5: Refactor `03_extraction.py` — Pakai Shared Modules

**File**: `sprint-3/materi-4/scraping/03_extraction.py`

### Perubahan dari versi lama:

| Aspek | Lama (`02_extraction.py`) | Baru (`03_extraction.py`) |
|-------|---------------------------|---------------------------|
| Input | `discovery_articles.csv` (URL belum resolved) | `resolved_urls.csv` (URL sudah resolved) |
| HTTP | `requests.get()` bare, 1 UA | `RateLimitedClient` (rate limit, rotating UA) |
| Paralel | 10 thread tanpa rate limit | 8 thread + per-domain rate limit |
| Error | Langsung masuk `failed_urls.csv` | Retry 3x, baru gagal |
| Logging | `print()` saja | Structured JSON logs |
| Resume | ❌ Tidak ada | Cek existing `articles_database.csv`, skip yang sudah ada |

### Perubahan yang harus dilakukan:

```python
# Perubahan utama di 03_extraction.py:

# 1. Ganti import
# LAMA:
#   import requests
#   from config import HEADERS, REQUEST_TIMEOUT
# BARU:
from lib.http_client import RateLimitedClient
from lib.logger import get_logger

# 2. Ganti input file
# LAMA:
#   DISCOVERY_CSV sebagai input
# BARU:
RESOLVED_CSV = os.path.join(DATA_DIR, "resolved_urls.csv")  # output dari 02_resolver.py

# 3. Ganti semua requests.get() dengan http.get()
# LAMA:
#   response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
# BARU:
#   http = RateLimitedClient()
#   response = http.get(url)

# 4. Tambah resume logic di awal main():
# Cek apakah articles_database.csv sudah ada
# Jika ada, baca URL yang sudah di-extract
# Skip URL yang sudah ada sehingga bisa resume

# 5. Kurangi MAX_WORKERS dari 10 ke 8
MAX_WORKERS = 8

# 6. Ganti print() dengan logger
# LAMA:
#   print(f"✓ Extracted {url}")
# BARU:
#   log.info("Extracted", url=url, method="newspaper3k")
```

### Perubahan detail per fungsi:

#### `extract_antara(url)` → Ganti `requests.get` dengan `http.get`

```python
# LAMA (line 121):
response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

# BARU:
response = http.get(url)
if response is None:
    return None
```

#### `extract_fallback(url)` → Sama, ganti `requests.get`

```python
# LAMA (line 211):
response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

# BARU:
response = http.get(url)
if response is None:
    return None
```

#### `process_single_article(item)` → Pakai `resolved_url` instead of decode

```python
# LAMA:
#   raw_url = item["url"]
#   real_url = decode_url_if_needed(raw_url)

# BARU (tidak perlu decode lagi, sudah di-resolve di step 4):
raw_url = item.get("url", "")
real_url = item.get("resolved_url", raw_url)  # Sudah resolved!
source_portal = item.get("resolved_domain", get_domain(real_url))
```

#### `main()` → Tambah resume logic

```python
def main():
    # Pakai resolved_urls.csv sebagai input
    input_csv = RESOLVED_CSV
    if not os.path.exists(input_csv):
        print(f"❌ File tidak ditemukan: {input_csv}")
        print("   Jalankan 02_resolver.py terlebih dahulu!")
        return
    
    df = pd.read_csv(input_csv)
    
    # Filter hanya yang resolve berhasil
    df = df[df.get("resolve_status", "success") == "success"]
    
    # === RESUME LOGIC ===
    # Jika articles_database.csv sudah ada, skip URL yang sudah di-extract
    if os.path.exists(ARTICLES_DB_CSV):
        df_existing = pd.read_csv(ARTICLES_DB_CSV)
        existing_urls = set(df_existing["url"].dropna().tolist())
        before = len(df)
        df = df[~df["resolved_url"].isin(existing_urls)]
        skipped = before - len(df)
        print(f"⏭️  Resume mode: skip {skipped} URL yang sudah di-extract")
    
    total_urls = len(df)
    if total_urls == 0:
        print("✅ Semua URL sudah di-extract sebelumnya!")
        return
    
    # ... sisanya sama seperti sebelumnya ...
```

### Verifikasi Step 5:
```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 03_extraction.py
```

**Output yang diharapkan**:
- Hanya memproses URL yang belum pernah di-extract (resume)
- Rate limiter aktif (terlihat dari kecepatan yang lebih stabil)
- Log tersimpan di `logs/scraping_YYYY-MM-DD.jsonl`
- `articles_database.csv` bertambah datanya

---

## Step 6: Update `config.py`

**File**: `sprint-3/materi-4/scraping/config.py`

### Tambahan yang diperlukan:

```python
# Tambahkan di bagian bawah config.py:

# ============================================================
# RESOLVED — Path untuk output resolver
# ============================================================
RESOLVED_CSV = os.path.join(DATA_DIR, "resolved_urls.csv")
RESOLVE_FAILED_CSV = os.path.join(DATA_DIR, "resolve_failed.csv")

# ============================================================
# PIPELINE — Urutan file eksekusi
# ============================================================
# Urutan baru (setelah refactor):
#   1. python3 01_discovery.py     → discovery_articles.csv
#   2. python3 02_resolver.py      → resolved_urls.csv  (NEW)
#   3. python3 03_extraction.py    → articles_database.csv + paragraphs_raw.csv
#   4. python3 04_cleaning.py      → public_text_news_clean.csv
#   5. python3 05_labeling.py      → labeled_dataset.csv (NEW)
```

---

## Step 7: Jalankan Pipeline & Verifikasi

### 7.1 Jalankan URL Resolver

```bash
cd /Users/auliamuzhaffar/Documents/grak/sprint-3/materi-4/scraping
python3 02_resolver.py
```

**Cek output**:
```bash
wc -l ../data/resolved_urls.csv
# Harusnya ~1200+ baris (setelah dedup)

# Cek berapa yang berhasil di-resolve:
python3 -c "
import pandas as pd
df = pd.read_csv('../data/resolved_urls.csv')
print('Success:', len(df[df['resolve_status']=='success']))
print('Per method:', df['resolver_method'].value_counts().to_dict())
"
```

### 7.2 Re-run Extraction

```bash
python3 03_extraction.py
```

**Cek output**:
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('../data/articles_database.csv')
print(f'Total artikel: {len(df)}')
print(f'Success rate: {len(df)/1350*100:.1f}%')
print(f'Top domains:', df['source_portal'].value_counts().head(10).to_dict())
"
```

**Target**: Total artikel naik dari 660 ke ≥1,000.

### 7.3 Cek Log Files

```bash
# Lihat log terbaru:
ls -la ../logs/
tail -20 ../logs/scraping_*.jsonl | python3 -m json.tool --no-ensure-ascii
```

---

## ✅ Checklist Fase 1 Selesai

Semua item di bawah harus ✓ sebelum lanjut ke Fase 2:

- [ ] `lib/__init__.py` ada dan bisa di-import
- [ ] `lib/http_client.py` — `RateLimitedClient` bisa di-import dan test
- [ ] `lib/logger.py` — `get_logger()` bisa di-import, log file terbuat
- [ ] `02_resolver.py` — Jalan tanpa error, output `resolved_urls.csv` terbuat
- [ ] `03_extraction.py` — Pakai `resolved_urls.csv` sebagai input, pakai `RateLimitedClient`
- [ ] Total artikel di `articles_database.csv` naik dari 660 ke ≥1,000
- [ ] Log files ada di `logs/`
- [ ] `config.py` sudah di-update dengan path baru

---

## 🚨 Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `ModuleNotFoundError: googlenewsdecoder` | Belum install | `pip install googlenewsdecoder` |
| `ModuleNotFoundError: lib.http_client` | `__init__.py` belum ada | Buat `lib/__init__.py` |
| Resolver success rate rendah (<60%) | Google blocking | Naikkan delay: edit `DEFAULT_DOMAIN_DELAYS["news.google.com"]` ke `2.0` |
| `ConnectionError` saat resolve | Internet putus | Cek koneksi, coba lagi |
| `429 Too Many Requests` | Terlalu cepat | Script otomatis backoff, tunggu saja |
| Extraction gagal banyak setelah resolve | Website pakai JS render | Normal — website pemerintah (.go.id) sering begini |
| `PermissionError` saat write log | Folder tidak ada | `mkdir -p ../logs/` |

---

## 📝 Catatan untuk Agent / Rekan

1. **Jangan ubah `01_discovery.py`** — Script ini sudah OK, tidak perlu diubah
2. **File lama `02_extraction.py` di-rename** — Jadi `03_extraction.py` (karena ada step baru di tengah)
3. **Urutan eksekusi baru**: `01_discovery.py` → `02_resolver.py` → `03_extraction.py`
4. **Rate limiter** sudah built-in di `RateLimitedClient`, jangan tambah `time.sleep()` manual lagi
5. **Semua password/API key**: Tidak ada. Semua scraping ini pakai public HTTP request biasa.
