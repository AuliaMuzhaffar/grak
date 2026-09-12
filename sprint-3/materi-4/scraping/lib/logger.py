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
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


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
