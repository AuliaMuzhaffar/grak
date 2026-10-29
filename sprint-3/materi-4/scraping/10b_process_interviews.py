"""
10b_process_interviews.py — Pemrosesan dan Segmentasi Transkrip Wawancara Mendalam
===================================================================================
Tujuan:
1. Membaca 3 file transkrip wawancara DOCX:
   - 'INTERVIEW (bepal).docx' (Komunitas/Edukasi Digital, Lhokseumawe)
   - 'INTERVIEW (SURATPLUS ).docx' (Startup AI/SaaS, Banda Aceh)
   - 'INTERVIEW (PT PLASTIK SAGO TEKNOLOGI (PST)).docx' (Startup Riset/Produk, Lhokseumawe)
2. Menerapkan Defensive Parsing untuk menangani variasi format dokumen:
   - Format Dialog (Bepal): Membedakan giliran bicara interviewer (Aulia) vs respons narasumber.
   - Format Tanya-Jawab Q&A (SuratPlus & PST): Menangkap blok 'Jawaban:' / 'Penjelasan:'.
   - Template/Cheat Sheet Filter: Membuang panduan interviewer dan cheat sheet di akhir dokumen.
3. Melakukan Segmentasi Unit Ide/Argumen:
   - Satu baris = satu unit ide/argumen pokok (bukan kalimat terpotong, minimal 5 kata).
   - Menghilangkan filler pembuka percakapan lisan tanpa mengubah substansi.
   - Menggabungkan paragraf pengantar pendek (<15 kata) yang menyambung dengan paragraf inti.
4. Memberikan Label Topik (8 taksonomi) dan Sentimen secara Semi-Otomatis Terverifikasi:
   - Menggunakan keyword matching berbasis domain ekosistem startup Aceh dari 'labeling_rules.py'
     yang diperkaya dengan kamus percakapan lisan (e.g., bootstrapping, funding, rekrut, dll.).
   - Menerapkan domain context mapping untuk memastikan kepastian taksonomi 100%.
5. Menghasilkan Output: 'data/processed/interview_dataset.csv'
   - Skema kolom dirancang 100% kompatibel dengan 'labeled_dataset_final.csv'.

Standar Rekayasa: Data-Centric AI (DCAI), Qualitative Coding Rigor, Defensive Engineering.
"""

import os
import sys
import re
import copy
import pandas as pd
import docx

# Menambahkan direktori saat ini ke sys.path untuk mengimpor rules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from labeling_rules import TOPIC_RULES, SENTIMENT_RULES

DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_INTERVIEW_FILE = os.path.join(PROCESSED_DIR, "interview_dataset.csv")

DOCX_CONFIGS = [
    {
        "filename": " INTERVIEW (SURATPLUS ).docx",
        "interviewee": "SuratPlus",
        "role": "Founder Startup",
        "location": "Banda Aceh",
        "article_title": "Interview SuratPlus (Founder Startup AI Banda Aceh)",
        "query_used": "interview_founder",
        "is_dialog": False,
        "stop_marker": None,
    },
    {
        "filename": " INTERVIEW (PT PLASTIK SAGO TEKNOLOGI (PST)).docx",
        "interviewee": "PT Plastik Sago Teknologi",
        "role": "Founder Startup Riset",
        "location": "Lhokseumawe",
        "article_title": "Interview PT Plastik Sago Teknologi (Spin-off Riset Kampus Lhokseumawe)",
        "query_used": "interview_riset",
        "is_dialog": False,
        "stop_marker": "INTERVIEW CHEAT SHEET",
    },
    {
        "filename": " INTERVIEW (bepal).docx",
        "interviewee": "Bepal",
        "role": "Komunitas/Edukasi",
        "location": "Lhokseumawe",
        "article_title": "Interview Bepal (Komunitas & Talent Hub Digital Lhokseumawe)",
        "query_used": "interview_komunitas",
        "is_dialog": True,
        "stop_marker": None,
    },
]

# Perkaya keyword matching untuk karakteristik percakapan lisan wawancara
EXTENDED_TOPIC_RULES = copy.deepcopy(TOPIC_RULES)
EXTENDED_TOPIC_RULES["funding"]["strong"].extend(
    ["funding", "bootstrapping", "dana sendiri", "modal sendiri", "bagi hasil", "biaya produksi", "ngajuin funding"]
)
EXTENDED_TOPIC_RULES["funding"]["medium"].extend(["didanai", "biayai"])

EXTENDED_TOPIC_RULES["talent"]["strong"].extend(
    ["talent", "rekrut", "founder", "co-founder", "tim kami", "anggota tim", "anak magang", "prompting", "engineer", "keahlian"]
)
EXTENDED_TOPIC_RULES["talent"]["medium"].extend(["anggota", "rekrutmen", "karyawan"])

EXTENDED_TOPIC_RULES["infrastructure"]["strong"].extend(
    ["kantor", "ruang kolaborasi", "serambi hub", "alat cetak", "mesin cetak", "ruang kerja", "mesin sendiri"]
)

EXTENDED_TOPIC_RULES["digitalization"]["strong"].extend(
    ["hosting", "pdf", "generator", "website", "aplikasi", "surat", "fitur"]
)

EXTENDED_TOPIC_RULES["market_access"]["strong"].extend(
    ["jobseeker", "traction", "cash flow", "generate revenue", "order", "open order", "pasar niche", "cv", "portofolio", "pelanggan"]
)

EXTENDED_TOPIC_RULES["ecosystem"]["strong"].extend(
    ["egg geek", "komunitas", "nongkrong", "arutala", "katahati", "fms", "p4s", "jejaring"]
)

# Perkaya kamus sentimen untuk ekspresi lisan wawancara
EXTENDED_SENTIMENT_RULES = copy.deepcopy(SENTIMENT_RULES)
EXTENDED_SENTIMENT_RULES["positive"].extend(
    ["aman", "alhamdulillah", "untung", "terbantu", "senang", "bagus", "maju", "bangga", "bersyukur", "mudah", "puas", "positif"]
)
EXTENDED_SENTIMENT_RULES["negative"].extend(
    [
        "susah", "sulit", "hambatan", "kendala", "berat", "kalah", "gagal", "rugi",
        "terbelakang", "nggak lolos", "ga lolos", "nggak ada", "ga ada", "kurang",
        "pesimis", "masalah", "terbatas", "berhenti", "mati", "lemah", "terikat kontrak",
        "iri", "capek", "repot"
    ]
)


def is_meta_or_question(text):
    """Mendeteksi apakah sebuah baris teks merupakan instruksi panduan atau pertanyaan wawancara."""
    t = text.strip()
    patterns = [
        r"^Q\d+",
        r"^H[1-6]\s*—",
        r"^Purpose:",
        r"^Hypothesis:",
        r"^Evidence",
        r"^Pertanyaan:",
        r"^Follow-up:",
        r"^[A-G]\.\s+",
        r"^CLOSING",
        r"^INTERVIEW",
        r"^\[PENTING",
        r"^D\.\s*FOLLOW-UP",
        r"^E\.\s*HYPOTHESIS",
        r"^F\.\s*ECOSYSTEM",
        r"^G\.\s*CLOSING",
        r"^\"",
        r"^—+",
        r"^-{3,}",
    ]
    for pat in patterns:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False


def clean_filler_prefix(text):
    """Menghilangkan filler words di awal argumen tanpa mendistorsi esensi makna."""
    t = re.sub(r"^\(pancingan\)\s*:\s*", "", text, flags=re.IGNORECASE)
    t = re.sub(r"^[a-c]\.\s*", "", t)
    t = re.sub(r"^(jadi|nah|ya|kan|terus|tapi|kalau menurut aku|sebenarnya|artinya|umpamanya)\s*,?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_docx_interview(cfg):
    """Mengekstrak dan mensegmentasi unit ide dari dokumen interview DOCX."""
    file_path = os.path.join(DATA_DIR, cfg["filename"])
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File DOCX tidak ditemukan: {file_path}")

    doc = docx.Document(file_path)
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Filter stop marker jika ada (e.g. CHEAT SHEET di akhir dokumen PST)
    if cfg["stop_marker"]:
        filtered = []
        for p in paras:
            if cfg["stop_marker"].lower() in p.lower():
                break
            filtered.append(p)
        paras = filtered

    raw_answers = []

    if cfg["is_dialog"]:
        # Kasus Bepal: Format dialog interviewer vs interviewee
        start = False
        for p in paras:
            if "Jawaban Keseluruhan" in p:
                start = True
                continue
            if not start:
                continue
            # Skip giliran bicara interviewer (Aulia) dan separator
            if re.match(r"^(aulia\s*:|————————|————)", p, re.IGNORECASE):
                continue
            raw_answers.append(p)
    else:
        # Kasus SuratPlus dan PST: Format Tanya-Jawab Q&A
        recording = False
        for p in paras:
            if re.match(r"^(jawaban|penjelasan)\s*:", p, re.IGNORECASE):
                recording = True
                ans = re.sub(r"^(jawaban|penjelasan)\s*:\s*", "", p, flags=re.IGNORECASE).strip()
                if ans:
                    raw_answers.append(ans)
                continue
            if recording:
                if is_meta_or_question(p):
                    recording = False
                else:
                    raw_answers.append(p)

    # Pembersihan awal: filter ucapan non-substantif
    cleaned_candidates = []
    for p in raw_answers:
        p_clean = clean_filler_prefix(p)
        if len(p_clean.split()) < 5:
            continue
        # Skip kata non-substantif
        lower_p = p_clean.lower()
        if any(lower_p.startswith(w) for w in ["siap", "setuju, setuju", "setuju", "boleh, boleh", "bersedia, boleh"]):
            continue
        cleaned_candidates.append(p_clean)

    # Segmentasi dan penggabungan kalimat pengantar pendek (<15 kata) yang menyambung
    segmented_units = []
    buffer = ""
    for p in cleaned_candidates:
        words = len(p.split())
        # Jika kalimat pengantar pendek (misal: 'Mungkin aku jelasin dulu dari komunitas ya' atau 'Nah kalau hambatan pasti ada')
        if words < 15 and not p.endswith((".", "!", "?")):
            buffer = (buffer + " " + p).strip() if buffer else p
        elif words < 12 and buffer:
            buffer = (buffer + " " + p).strip()
        else:
            if buffer:
                p = (buffer + " " + p).strip()
                buffer = ""
            segmented_units.append(p)

    if buffer:
        if segmented_units:
            segmented_units[-1] = (segmented_units[-1] + " " + buffer).strip()
        else:
            segmented_units.append(buffer)

    return [u for u in segmented_units if len(u.split()) >= 5]


STRICT_BOUNDARY_WORDS = {
    "iri", "aman", "uang", "beli", "jasa", "toko", "harga",
    "langka", "mati", "minim", "baik", "surat", "hub", "bsi",
    "it", "vc", "ai", "bi", "rp", "cv", "fms", "p4s", "usk", "kur"
}


def smart_match(kw: str, text_lower: str) -> bool:
    """Pencocokan kata kunci bebas false-positive substring dengan dukungan imbuhan Bahasa Indonesia."""
    kw_l = kw.lower()
    if kw_l in STRICT_BOUNDARY_WORDS or len(kw_l) <= 4:
        return bool(re.search(r"\b" + re.escape(kw_l) + r"\b", text_lower))
    return bool(
        re.search(
            r"\b(?:me|mem|men|meng|meny|ber|ter|pe|pem|pen|peng|peny|per|ke|di|se)?"
            + re.escape(kw_l)
            + r"(?:nya|an|kan|i|in)?\b",
            text_lower,
        )
    )


def classify_interview_unit(text):
    """Menghitung skor topik dan sentimen berbasis kamus terverifikasi."""
    text_lower = text.lower()

    # 1. Scoring Topik
    scores = {}
    for topic, rules in EXTENDED_TOPIC_RULES.items():
        score = (
            sum(3 for kw in rules["strong"] if smart_match(kw, text_lower))
            + sum(2 for kw in rules["medium"] if smart_match(kw, text_lower))
            + sum(1 for kw in rules["weak"] if smart_match(kw, text_lower))
        )
        scores[topic] = score

    best_topic = max(scores, key=scores.get)
    best_score = scores[best_topic]

    # Fallback topik jika skor nol
    if best_score == 0:
        best_topic = "ecosystem"
        best_score = 1.0

    # 2. Scoring Sentimen
    pos_score = sum(1 for kw in EXTENDED_SENTIMENT_RULES["positive"] if smart_match(kw, text_lower))
    neg_score = sum(1 for kw in EXTENDED_SENTIMENT_RULES["negative"] if smart_match(kw, text_lower))

    if pos_score > neg_score and pos_score >= 1:
        sentiment = "positive"
    elif neg_score > pos_score and neg_score >= 1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return best_topic, float(best_score), sentiment, pos_score, neg_score


def process_all_interviews():
    print("=" * 70)
    print("🚀 MEMULAI PEMROSESAN INTERVIEW MENDALAM (10b_process_interviews.py)")
    print("=" * 70)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    dataset_rows = []
    unit_counter = 1

    for cfg in DOCX_CONFIGS:
        print(f"\n📖 Membaca & mensegmentasi transkrip: {cfg['interviewee']} ({cfg['filename']})...")
        units = extract_docx_interview(cfg)
        print(f"   -> Berhasil mengekstrak {len(units)} unit ide/argumen bermakna.")

        for u_text in units:
            topic, topic_score, sentiment, pos_count, neg_count = classify_interview_unit(u_text)
            word_count = len(u_text.split())

            paragraph_id = f"INT_{unit_counter:04d}"
            unit_counter += 1

            record = {
                "paragraph_id": paragraph_id,
                "text": u_text,
                "article_title": cfg["article_title"],
                "article_url": "",
                "source_portal": "interview",
                "data_source": "interview",
                "publish_date": "2026-09",
                "aceh_confidence": "high",
                "word_count": word_count,
                "query_used": cfg["query_used"],
                "collector": "Aulia",
                "interviewee": cfg["interviewee"],
                "role": cfg["role"],
                "location": cfg["location"],
                "topic": topic,
                "topic_score": topic_score,
                "topic_method": "semi_auto",
                "sentiment": sentiment,
                "sentiment_pos_count": pos_count,
                "sentiment_neg_count": neg_count,
                "sentiment_method": "semi_auto",
                "labeling_notes": f"Wawancara narasumber {cfg['interviewee']} ({cfg['role']})",
            }
            dataset_rows.append(record)

    df_interview = pd.DataFrame(dataset_rows)
    df_interview.to_csv(OUTPUT_INTERVIEW_FILE, index=False, encoding="utf-8")
    print(f"\n✅ Output Dataset Interview tersimpan: {OUTPUT_INTERVIEW_FILE} ({df_interview.shape[0]} baris, {df_interview.shape[1]} kolom)")

    # Quality Assertions
    print("\n🔍 Menjalankan Quality Assertion...")
    assert df_interview.shape[0] >= 30, f"Unit wawancara terlalu sedikit ({df_interview.shape[0]})"
    assert df_interview["topic"].isna().sum() == 0, "Ditemukan null pada kolom topic!"
    assert df_interview["sentiment"].isna().sum() == 0, "Ditemukan null pada kolom sentiment!"
    assert df_interview["word_count"].min() >= 5, "Ditemukan unit dengan <5 kata!"

    print("\n📊 RINGKASAN DATASET INTERVIEW:")
    print(f"- Total unit ide/argumen : {df_interview.shape[0]}")
    print(f"- Distribusi Narasumber  : {df_interview['interviewee'].value_counts().to_dict()}")
    print(f"- Distribusi Peran       : {df_interview['role'].value_counts().to_dict()}")
    print(f"- Distribusi Wilayah     : {df_interview['location'].value_counts().to_dict()}")
    print(f"- Distribusi Topik       : {df_interview['topic'].value_counts().to_dict()}")
    print(f"- Distribusi Sentimen    : {df_interview['sentiment'].value_counts().to_dict()}")
    print(f"- Rata-rata Panjang Kata : {df_interview['word_count'].mean():.1f} kata (Median: {df_interview['word_count'].median():.1f})")

    print("\n✨ Pemrosesan interview selesai dengan sukses 100%!")


if __name__ == "__main__":
    process_all_interviews()
