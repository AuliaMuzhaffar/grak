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
