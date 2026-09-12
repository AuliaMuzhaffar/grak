"""
labeling_rules.py — Definisi rules untuk auto-labeling
GRAK 2026 · Sprint 3

Rules ini dipakai oleh 05_labeling.py untuk auto-label topic dan sentiment.

CARA UPDATE:
  1. Jalankan 05_labeling.py pertama kali
  2. Cek needs_review.csv → review manual
  3. Temukan pattern baru → tambahkan keyword di sini
  4. Jalankan 05_labeling.py lagi (idempotent, aman di-run ulang)
"""

# ============================================================
# TOPIC RULES — Keyword matching untuk auto-label topic
# ============================================================
# Setiap topic punya 3 tier keyword:
#   - strong: Kata-kata yang PASTI menunjukkan topic ini (confidence tinggi)
#   - medium: Kata-kata yang MUNGKIN menunjukkan topic ini (perlu konteks)
#   - weak: Kata-kata yang LEMAH, hanya sebagai pendukung
#
# Logic scoring:
#   score = (jumlah strong × 3) + (jumlah medium × 2) + (jumlah weak × 1)
#   Topic dipilih berdasarkan score tertinggi.
#   Minimum score = 3 untuk dianggap auto-labeled.

TOPIC_RULES = {
    "funding": {
        "strong": [
            "pendanaan", "investasi", "modal ventura", "venture capital",
            "fundraising", "angel investor", "seed funding", "hibah",
            "grant", "pinjaman modal", "kredit usaha", "KUR",
            "modal usaha", "dana bergulir", "pembiayaan syariah",
            "bank syariah", "bank aceh syariah", "penyaluran kur",
            "bantuan permodalan", "suntikan modal", "investor",
        ],
        "medium": [
            "modal", "dana", "biaya", "anggaran", "subsidi",
            "permodalan", "kapitalisasi", "valuasi", "pembiayaan",
            "pinjaman", "kredit", "bsi", "bank aceh",
        ],
        "weak": [
            "uang", "rupiah", "miliar", "juta", "bisnis",
        ],
    },
    
    "talent": {
        "strong": [
            "talent digital", "sumber daya manusia", "SDM digital",
            "programmer", "developer", "software engineer",
            "bootcamp", "pelatihan coding", "pelatihan digital",
            "training IT", "sertifikasi", "fresh graduate",
            "digital marketer", "UI/UX designer", "talenta digital",
            "peningkatan kapasitas sdm", "pelatihan vokasi",
        ],
        "medium": [
            "pelatihan", "training", "keterampilan", "skill",
            "lulusan", "mahasiswa", "kampus", "universitas",
            "dosen", "tenaga kerja", "SDM", "wirausaha muda",
            "kompetensi", "magang", "keahlian",
        ],
        "weak": [
            "belajar", "pendidikan", "sekolah", "kursus", "generasi muda", "anak muda",
        ],
    },
    
    "infrastructure": {
        "strong": [
            "infrastruktur digital", "infrastruktur internet",
            "co-working space", "coworking", "data center",
            "pusat data", "server", "cloud computing",
            "jaringan internet", "fiber optik", "broadband",
            "BTS", "telekomunikasi", "gedung amanah",
            "konektivitas internet", "akses internet",
        ],
        "medium": [
            "infrastruktur", "internet", "jaringan", "koneksi",
            "sinyal", "bandwidth", "ruang kerja", "gedung", "fasilitas",
            "creative hub",
        ],
        "weak": [
            "online", "wifi", "4G", "5G",
        ],
    },
    
    "regulation": {
        "strong": [
            "regulasi", "kebijakan pemerintah", "peraturan daerah",
            "perizinan usaha", "izin usaha", "SIUP", "NIB",
            "OSS", "OJK", "BKPM", "Kemenkumham",
            "perda", "qanun", "moratorium", "diskopukm",
            "dinas koperasi", "sertifikasi halal", "izin edar",
        ],
        "medium": [
            "kebijakan", "peraturan", "perizinan", "birokrasi",
            "aturan", "legalitas", "hukum", "undang-undang",
            "pemerintah daerah", "pemda", "pemerintah aceh", "pemprov aceh",
        ],
        "weak": [
            "pemerintah", "dinas", "kementerian", "resmi",
        ],
    },
    
    "market_access": {
        "strong": [
            "akses pasar", "market access", "penetrasi pasar",
            "pangsa pasar", "target market", "ekspansi pasar",
            "distribusi produk", "supply chain", "rantai pasok",
            "export", "ekspor", "import", "pasar ekspor",
            "business matching", "temu bisnis",
        ],
        "medium": [
            "pasar", "market", "konsumen", "customer", "pelanggan",
            "penjualan", "revenue", "omzet", "transaksi",
            "produk", "jasa", "layanan", "bazar umkm", "pameran",
        ],
        "weak": [
            "jual", "beli", "harga", "toko", "dagang", "komersial",
        ],
    },
    
    "ecosystem": {
        "strong": [
            "inkubator bisnis", "akselerator startup", "incubator",
            "accelerator", "mentoring startup", "mentor bisnis",
            "komunitas startup", "komunitas teknologi",
            "innovation hub", "startup hub", "tech community",
            "ekosistem startup", "ekosistem digital",
            "garuda spark", "startup weekend", "program inkubasi",
            "program akselerasi", "wadah kreatif",
        ],
        "medium": [
            "inkubator", "akselerator", "mentor", "mentoring",
            "komunitas", "networking", "kolaborasi",
            "ekosistem", "hub", "co-creation", "jejaring",
        ],
        "weak": [
            "acara", "event", "workshop", "seminar", "webinar",
        ],
    },
    
    "digitalization": {
        "strong": [
            "transformasi digital", "digitalisasi UMKM",
            "UMKM digital", "go digital", "adopsi digital",
            "e-commerce", "marketplace", "toko online",
            "fintech", "payment gateway", "digital banking",
            "aplikasi mobile", "platform digital", "qris",
            "pembayaran digital", "adopsi teknologi",
        ],
        "medium": [
            "digitalisasi", "digital", "teknologi informasi",
            "IT", "aplikasi", "platform", "website",
            "online", "elektronik", "sistem informasi",
        ],
        "weak": [
            "modern", "inovasi", "teknologi",
        ],
    },
    
    "success_story": {
        "strong": [
            "kisah sukses", "success story", "startup sukses",
            "penghargaan", "award", "juara", "pemenang",
            "berhasil meraih", "tumbuh pesat",
            "meraih pendanaan", "berhasil ekspansi",
            "unicorn", "centaur", "lolos kurasi", "meraih prestasi",
        ],
        "medium": [
            "berhasil", "sukses", "tumbuh", "berkembang",
            "meningkat", "naik", "pertumbuhan",
            "prestasi", "capaian", "pencapaian", "unggulan",
        ],
        "weak": [
            "positif", "baik", "bagus", "hebat",
        ],
    },
}


# ============================================================
# SENTIMENT RULES — Keyword matching untuk auto-label sentiment
# ============================================================
# Logic:
#   positive_score = jumlah keyword positive yang ditemukan
#   negative_score = jumlah keyword negative yang ditemukan
#   
#   Jika positive_score > negative_score dan positive_score >= 2 → "positive"
#   Jika negative_score > positive_score dan negative_score >= 2 → "negative"
#   Else → "neutral"

SENTIMENT_RULES = {
    "positive": [
        # Achievement / Success
        "berhasil", "sukses", "tumbuh", "berkembang", "meningkat",
        "prestasi", "pencapaian", "terobosan", "inovasi",
        "penghargaan", "juara", "terbaik", "unggul",
        
        # Opportunity / Potential
        "peluang", "potensi", "prospek", "harapan", "optimis",
        "menjanjikan", "potensial", "strategis",
        
        # Support / Enablement
        "dukungan", "mendukung", "mendorong", "memfasilitasi",
        "bantuan", "kolaborasi", "kerja sama", "kemitraan",
        "pemberdayaan", "pengembangan",
        
        # Growth / Impact
        "pertumbuhan", "perkembangan", "kemajuan", "progres",
        "dampak positif", "kontribusi", "manfaat",
    ],
    
    "negative": [
        # Barriers / Obstacles
        "hambatan", "kendala", "tantangan", "masalah", "kesulitan",
        "rintangan", "bottleneck", "barrier",
        
        # Limitation / Scarcity
        "kurang", "terbatas", "minim", "sedikit", "langka",
        "kekurangan", "keterbatasan", "tidak memadai",
        "tidak cukup", "belum tersedia",
        
        # Failure / Decline
        "gagal", "kegagalan", "menurun", "turun", "merosot",
        "bangkrut", "gulung tikar", "tutup",
        
        # Negative sentiment
        "sulit", "berat", "rumit", "kompleks", "mahal",
        "lambat", "tertinggal", "terbelakang",
        "pesimis", "khawatir", "cemas",
    ],
}


# ============================================================
# SCORING THRESHOLDS — Minimum score untuk auto-label
# ============================================================

# Topic: minimum total score agar dianggap auto-labeled
TOPIC_MIN_SCORE = 3  # Misal: 1 strong match (3 poin) sudah cukup

# Sentiment: minimum keyword match
SENTIMENT_MIN_MATCHES = 2  # Minimal 2 keyword match

# Jika score di bawah threshold → masuk needs_review.csv
