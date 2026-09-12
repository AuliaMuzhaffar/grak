# 🧠 Deep Dive Konsep & Arsitektur Fase 3: Semi-Automated Labeling & Human-in-the-Loop

> **GRAK 2026 · Sprint 3 · Materi 4**  
> **Tujuan Dokumen**: Membedah fondasi konseptual pelabelan data semi-otomatis (Programmatic Weak Supervision), arsitektur Active Learning, taksonomi topik & sentimen, serta bahan persiapan interview/presentasi teknis.

---

## 📌 DAFTAR ISI
1. [Mengapa Fase 3 Sangat Kritis? (The "Why")](#1-mengapa-fase-3-sangat-kritis-the-why)
2. [Spektrum Metode Pelabelan: Heuristik vs LLM vs Manual](#2-spektrum-metode-pelabelan-heuristik-vs-llm-vs-manual)
3. [Arsitektur Semi-Automated Pipeline & Human-in-the-Loop](#3-arsitektur-semi-automated-pipeline--human-in-the-loop)
4. [Bedah Taksonomi Label: 8 Topik Ekosistem & Batasannya](#4-bedah-taksonomi-label-8-topik-ekosistem--batasannya)
5. [Bedah Taksonomi Sentimen: Jebakan Jurnalisme Berita](#5-bedah-taksonomi-sentimen-jebakan-jurnalisme-berita)
6. [Logika & Matematika Scoring Multi-Tier Keyword](#6-logika--matematika-scoring-multi-tier-keyword)
7. [Mitigasi Bias & Validasi Distribusi Data (Class Imbalance)](#7-mitigasi-bias--validasi-distribusi-data-class-imbalance)
8. [Bahan Interview & Presentasi: Cara Menjawab Pertanyaan Kunci](#8-bahan-interview--presentasi-cara-menjawab-pertanyaan-kunci)

---

## 1. Mengapa Fase 3 Sangat Kritis? (The "Why")

Di Fase 4 nanti, kita akan melatih model **Supervised Machine Learning** (seperti SVM, Logistic Regression, atau Naive Bayes) untuk mengklasifikasi topik dan sentimen berita startup secara otomatis.

Syarat mutlak algoritma *Supervised Learning* adalah tersedianya **Ground Truth Label** (data latih yang sudah memiliki label acuan yang akurat).

### A. Hambatan Utama: "Labeling Bottleneck"
Kita memiliki **13.840 paragraf berita bersih** hasil Fase 2.
- Jika 1 orang manusia melabeli 1 paragraf dalam **30 detik** (membaca teks, memahami konteks, memilih topik dari 8 opsi, dan menentukan sentimen dari 3 opsi):
  $$\text{Waktu} = 13.840 \times 30\text{ detik} = 415.200\text{ detik} \approx 115,3\text{ jam kerja non-stop}$$
- Dengan asumsi jam kerja efektif 8 jam per hari, pelabelan manual penuh membutuhkan **~14,5 hari kerja kalender!**
- Di industri modern, menunda proyek selama berminggu-minggu hanya untuk pelabelan manual adalah inefisiensi besar.

### B. Bahaya Labeling Asal-asalan (Noisy Labels)
Jika kita terburu-buru melakukan pelabelan manual atau menggunakan aturan yang terlalu longgar, model ML di Fase 4 akan mempelajari pola yang salah (*label noise*).
- Model ML tidak pernah lebih pintar daripada data latihnya:
  $$\text{Model Quality} \le \text{Label Quality}$$
- Jika data latih memiliki tingkat kesalahan label (error rate) sebesar 20%, maka akurasi model di data produksi mustahil konsisten di atas 80%.

---

## 2. Spektrum Metode Pelabelan: Heuristik vs LLM vs Manual

Di dunia data science profesional, ada 3 pendekatan utama untuk menghasilkan data berlabel:

| Dimensi Evaluasi | Manual Penuh (Human Annotator) | Zero-Shot LLM API (GPT-4 / Claude / Gemini) | Programmatic Weak Supervision (Pendekatan Kita) |
|---|---|---|---|
| **Waktu / Kecepatan** | Sangat Lambat (2-3 minggu) | Cepat (15-30 menit) | **Instan (beberapa detik untuk 13.840 data)** |
| **Biaya Finansial** | Tinggi (gaji annotator / tenaga kerja) | Sedang - Tinggi (biaya token API untuk 14k paragraf) | **Nol Rupiah (100% lokal & gratis)** |
| **Transparansi / Auditability** | Subjektif (tergantung mood annotator) | *Black Box* (susah diaudit mengapa LLM memilih label tertentu) | **100% Transparan (setiap skor kata kunci tercatat)** |
| **Reproducibility** | Rendah (manusia bisa inkonsisten di hari berbeda) | Sedang (ada faktor temperature/stochasticity) | **Sempurna (Deterministic: input sama = output sama)** |
| **Kemampuan Menangani Ambiguitas** | Tinggi (manusia paham konteks halus) | Tinggi | Terbatas (perlu diarahkan ke Human Review) |

### Mengapa Kita Memilih Pendekatan Semi-Automated (Weak Supervision)?
Kita menggabungkan keunggulan kecepatan aturan heuristik dengan ketelitian manusia melalui konsep **Human-in-the-Loop (Active Learning)**:
1. **Aturan Heuristik (Rules)** menyelesaikan **60-70%** kasus yang berkarakter kuat dan tidak ambigu (misal paragraf yang eksplisit menyebut "angel investor dan modal ventura" pasti `funding`).
2. **Manusia (Human Annotator)** memusatkan 100% energinya hanya pada **30-40%** kasus yang ambigu, tidak memiliki kata kunci dominan, atau terjadi konflik skor (*Uncertainty Sampling*).
3. **Efisiensi Waktu**: Dari 14 hari kerja berkurang menjadi **2-3 jam review terfokus**!

---

## 3. Arsitektur Semi-Automated Pipeline & Human-in-the-Loop

Pipeline Fase 3 didesain dengan konsep **Siklus Tertutup (Closed Feedback Loop)**:

```text
               ┌──────────────────────────────────────────────┐
               │ 13.840 Paragraf Bersih Fase 2                │
               │ (public_text_news_clean.csv)                 │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
                      ┌──────────────────────────────┐
                      │    05_labeling.py Engine     │
                      │  (Multi-tier Keyword Scoring) │
                      └──────────────┬───────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼ (Confidence >= Threshold)                         ▼ (Confidence < Threshold / Ties)
┌──────────────────────────────────────┐            ┌──────────────────────────────────────┐
│       auto_labeled.csv               │            │       needs_review.csv               │
│       (~60 - 70% data)               │            │       (~30 - 40% data)               │
└──────────────────┬───────────────────┘            └──────────────────┬───────────────────┘
                   │                                                   │
                   ▼ (Spot Check 50-100 baris)                         ▼ (Manual Review terfokus)
         [ Hitung Error Rate ]                              [ Review & Isi Kolom Label ]
                   │                                                   │
                   └───────────────────┬───────────────────────────────┘
                                       │
                                       ▼
                       [ Ditemukan Pola Baru / Koreksi? ]
                                      ╱ ╲
                                    YA   TIDAK
                                   ╱       ╲
                                  ▼         ▼
                     ┌──────────────────┐  ┌──────────────────────────────────────┐
                     │ Update Rules di  │  │        06_merge_labels.py            │
                     │labeling_rules.py │  │  (Gabungkan Auto + Human Review)     │
                     └────────┬─────────┘  └──────────────────┬───────────────────┘
                              │                               │
                              ▼ (Re-run idempotent)           ▼
                      [ Putar Ulang ]              ┌──────────────────────────────────────┐
                                                   │    labeled_dataset_final.csv         │
                                                   │    (Ready for ML Training Fase 4)    │
                                                   └──────────────────────────────────────┘
```

### Prinsip Desain Kunci:
1. **Pemisahan Logika & Rules**: `labeling_rules.py` menyimpan kamus aturan, sedangkan `05_labeling.py` mengeksekusi perhitungan. Analis bisa menambah kata kunci tanpa risiko merusak kode mesin.
2. **Idempotensi & Proteksi Label Manual**: Jika sebuah baris sudah pernah diberi label manual oleh manusia, saat skrip dijalankan ulang, label manual tersebut **tidak akan pernah ditimpa (overwritten)** oleh mesin auto-label.

---

## 4. Bedah Taksonomi Label: 8 Topik Ekosistem & Batasannya

Sebagai Data Scientist yang meneliti ekosistem startup, kita tidak memilih topik secara acak. Kedelapan topik ini memetakan pilar-pilar penting dalam teori pengembangan ekosistem kewirausahaan (seperti model *Isenberg Entrepreneurship Ecosystem*):

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TAKSONOMI 8 TOPIK STARTUP ACEH                           │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Topik           │ Definisi Operasional & Ruang Lingkup                      │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ funding         │ Akses permodalan: hibah, angel investor, venture capital,  │
│                 │ KUR, pinjaman perbankan, crowdfunding, seed round.       │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ talent          │ Pengembangan kapasitas SDM: programmer, desainer UI/UX,   │
│                 │ digital marketer, kurikulum kampus, bootcamp coding.     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ infrastructure  │ Fondasi fisik & teknologi: jaringan internet, BTS, fiber  │
│                 │ optik, data center/server cloud, co-working space fisik.  │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ regulation      │ Kebijakan publik & hukum: qanun daerah, perda, perizinan  │
│                 │ OSS, regulasi OJK/BI, perpajakan, kemudahan berusaha.    │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ market_access   │ Akses pasar & komersialisasi: penetrasi pasar lokal/luar, │
│                 │ ekspor, rantai pasok (supply chain), omzet & konsumen.   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ ecosystem       │ Lingkungan pembinaan & jejaring: inkubator bisnis,        │
│                 │ akselerator, program mentoring, komunitas tech, meetup.   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ digitalization  │ Adopsi teknologi & transformasi digital: digitalisasi     │
│                 │ UMKM, integrasi e-commerce, POS, QRIS/fintech, go-online. │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ success_story   │ Bukti pencapaian & milestone: prestasi startup daerah,   │
│                 │ juara kompetisi inovasi, pertumbuhan skala bisnis, award. │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### Zona Abu-abu (Edge Cases) & Panduan Penegakan Batas:

Di teks berita jurnalisme nyata, batas antar kategori sering bersinggungan. Berikut aturan pembeda yang jelas:

1. **`ecosystem` vs `talent`**:
   - *Kasus*: "Universitas Syiah Kuala menggelar pelatihan coding 3 bulan untuk mahasiswa."
   - *Pembeda*: Fokusnya adalah peningkatan keahlian individu/SDM -> Label: **`talent`**.
   - *Kasus*: "Inkubator USK menjembatani founder startup dengan mentor bisnis industri."
   - *Pembeda*: Fokusnya adalah jejaring/fasilitasi ekosistem kewirausahaan -> Label: **`ecosystem`**.

2. **`digitalization` vs `infrastructure`**:
   - *Kasus*: "Pemerintah membangun jaringan fiber optik dan tower BTS di pelosok Aceh."
   - *Pembeda*: Infrastruktur keras/konektivitas fisik -> Label: **`infrastructure`**.
   - *Kasus*: "Pedagang pasar Peunayong mulai menggunakan QRIS dan mendaftar di marketplace."
   - *Pembeda*: Adopsi tools digital oleh pelaku usaha mikro -> Label: **`digitalization`**.

3. **`funding` vs `success_story`**:
   - *Kasus*: "Startup Agritech asal Banda Aceh berhasil meraih seed funding 2 Miliar Rupiah."
   - *Pembeda*: Jika penekanannya adalah instrumen permodalan dan rencana alokasi dana -> **`funding`**. Jika penekanannya adalah perayaan tonggak pencapaian/prestasi startup lokal -> **`success_story`**. Aturan skor keyword akan membantu memilih yang paling dominan di paragraf tersebut.

---

## 5. Bedah Taksonomi Sentimen: Jebakan Jurnalisme Berita

Sentimen berita bisnis di media massa Indonesia memiliki karakteristik yang sangat berbeda dibandingkan ulasan produk di e-commerce atau tweet media sosial.

### A. Tiga Kelas Sentimen
1. **`positive`**: Paragraf mengandung optimisme, pencapaian target, peluang pasar, penggelontoran dana stimulus, apresiasi, atau kemitraan strategis yang saling menguntungkan.
2. **`negative`**: Paragraf membahas hambatan regulasi, keluhan internet lambat, kelangkaan talenta lokal, startup gulung tikar, penurunan omzet, atau pemangkasan anggaran.
3. **`neutral`**: Paragraf jurnalisme deskriptif obyektif. Menyampaikan informasi fakta (5W1H) seperti tanggal acara, daftar hadir pejabat, atau kutipan regulasi tanpa muatan emosional.

### B. Jebakan Jurnalisme: "Framing Netral atas Masalah Negatif"
Wartawan Indonesia sering menggunakan gaya bahasa diplomatis dan pasif:
> *"Dinas Koperasi dan UKM menggelar rapat koordinasi guna mengevaluasi kendala akses pembiayaan yang dihadapi pelaku usaha."*

- Ada kata *"kendala"* dan *"masalah pembiayaan"* (indikasi negatif).
- Tetapi tujuan kegiatannya adalah *"rapat evaluasi pemerintah"* (netral/konstruktif).
- **Aturan Solusi Kita**: Kami menerapkan ambang batas `SENTIMENT_MIN_MATCHES = 2`. Kata negatif tunggal dalam kalimat formal tidak langsung menjadikannya negatif kecuali jika bobot masalahnya nyata dan dominan.

---

## 6. Logika & Matematika Scoring Multi-Tier Keyword

Mengapa kita tidak memakai pencocokan kata kunci biner (ada kata X = Topik Y)?
Karena kata-kata dalam bahasa manusia memiliki **tingkat ketegasan makna (specificity)** yang berbeda-beda.

### A. Sistem Pembobotan 3 Tingkat (Tiered Weights)

```text
┌─────────────────┬──────────┬─────────────────────────────┬───────────────────────────────────────────┐
│ Tier            │ Bobot    │ Karakteristik               │ Contoh                                    │
├─────────────────┼──────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ 1. Strong       │ 3 Poin   │ Sangat spesifik dan unik    │ "venture capital", "angel investor",      │
│                 │          │ pada satu topik tertentu.   │ "co-working space", "qanun", "bootcamp"   │
├─────────────────┼──────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ 2. Medium       │ 2 Poin   │ Relevan, tetapi butuh kata  │ "modal", "pelatihan", "pasar", "aturan",  │
│                 │          │ pendukung agar definitif.   │ "komunitas", "aplikasi", "sukses"         │
├─────────────────┼──────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ 3. Weak         │ 1 Poin   │ Kata umum/kontekstual.      │ "uang", "bisnis", "acara", "mahasiswa",   │
│                 │          │ Tidak boleh menentukan      │ "modern", "hebat"                         │
│                 │          │ topik secara sendirian.     │                                           │
└─────────────────┴──────────┴─────────────────────────────┴───────────────────────────────────────────┘
```

### B. Formulasi Perhitungan Skor Topik (Intuisi Papan Skor)

Untuk setiap teks paragraf $T$ dan setiap topik kandidat $k \in \{1, 2, \dots, 8\}$:

$$\text{Score}(T, k) = \Big(3 \times \sum_{w \in \text{Strong}_k} \mathbb{I}(w \in T)\Big) + \Big(2 \times \sum_{w \in \text{Medium}_k} \mathbb{I}(w \in T)\Big) + \Big(1 \times \sum_{w \in \text{Weak}_k} \mathbb{I}(w \in T)\Big)$$

> 💡 **Arti Simbol Matematika Tanpa Rumit**:
> - $\sum$: Jumlahkan seluruh kata kunci yang ditemukan.
> - $\mathbb{I}(w \in T)$: Fungsi indikator, bernilai **1** jika kata $w$ ada di teks, dan **0** jika tidak ada.
> - Intinya: **Total Skor = (3 × jumlah kata Strong) + (2 × jumlah kata Medium) + (1 × jumlah kata Weak)**.

---

### C. Keputusan Klasifikasi: Apa Itu $\arg\max$?
Setelah komputer menghitung skor untuk ke-8 topik, komputer mengumpulkan skornya:
- Nilai maksimumnya ($\max$) = skor tertinggi di antara ke-8 topik.
- Siapa topik yang memegang skor tertinggi itu? Itulah **$\arg\max$**:
  $$k^* = \arg\max_k \text{Score}(T, k)$$

---

### D. Ambang Batas (Thresholding) & Quality Gate
Mengapa kita menetapkan ambang batas minimal $\text{TOPIC\_MIN\_SCORE} = 3$?
Jika tidak ada ambang batas, sebuah berita seremonial pejabat umum yang memuat 1 kata lemah (*"acara"*, skor = 1) akan otomatis dicap sebagai ekosistem startup! Ini adalah bencana **False Positive**.

$$\text{Label}(T) = \begin{cases} 
k^*, & \text{jika } \text{Score}(T, k^*) \ge 3 \\ 
\text{"unclassified"}, & \text{jika } \text{Score}(T, k^*) < 3 \quad \longrightarrow \text{Kirim ke needs\_review.csv}
\end{cases}$$

#### Tabel Skenario Kelolosan Ambang Batas:
| Kombinasi Kata yang Ditemukan | Hitungan Poin | Skor Akhir | Lolos Threshold ($\ge 3$)? | Keputusan Mesin |
|---|:---:|:---:|:---:|---|
| **1 kata Strong** (misal: `"modal ventura"`) | $1 \times 3$ | **3** | **YA ✅** | Auto-label langsung sebagai `funding` |
| **1 kata Medium + 1 kata Weak** (misal: `"modal"` + `"bisnis"`) | $2 + 1$ | **3** | **YA ✅** | Auto-label langsung sebagai `funding` |
| **2 kata Medium** (misal: `"pelatihan"` + `"skill"`) | $2 + 2$ | **4** | **YA ✅** | Auto-label langsung sebagai `talent` |
| **2 kata Weak saja** (misal: `"uang"` + `"bisnis"`) | $1 + 1$ | **2** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |
| **1 kata Medium saja** (misal: `"pasar"`) | $1 \times 2$ | **2** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |
| **Tidak ada kata kunci cocok** | 0 | **0** | **TIDAK ❌** | Dianggap **Unclassified** $\rightarrow$ kirim ke `needs_review.csv` |

---

### E. Empat (4) Use Case Nyata dari Berita Ekosistem Startup Aceh

#### 📌 Use Case 1: Kemenangan Telak Satu Topik (Clear Winner)
> **Teks**: *"Startup agritech asal Banda Aceh berhasil mengamankan **seed funding** sebesar 1,5 Miliar Rupiah dari konsorsium **angel investor** Jakarta. Dana ini akan digunakan sebagai **modal** ekspansi."*
- Papan Skor `funding`: Strong: `"seed funding"` (3) + `"angel investor"` (3) + Medium: `"modal"` (2) = **8 poin**.
- Topik lain: 0 poin.
- **Keputusan**: Skor 8 ($\ge 3$) $\rightarrow$ ✅ **Auto-label: `funding`**.

#### 📌 Use Case 2: Persaingan Sengit Antar-Topik (Competition & $\arg\max$)
> **Teks**: *"Dinas Koperasi Aceh menggelar program **inkubator bisnis** bersama **komunitas startup**. Di dalamnya, para founder diberikan **pelatihan** validasi ide bisnis digital."*
- Papan Skor:
  - `ecosystem`: Strong: `"inkubator bisnis"` (3) + `"komunitas startup"` (3) = **6 poin**.
  - `talent`: Medium: `"pelatihan"` (2) = **2 poin**.
  - `digitalization`: Medium: `"digital"` (2) = **2 poin**.
- Evaluasi $\arg\max$: Skor tertinggi adalah `ecosystem` (6 poin vs 2 poin).
- **Keputusan**: Skor 6 ($\ge 3$) $\rightarrow$ ✅ **Auto-label: `ecosystem`**.

#### 📌 Use Case 3: Penyelamatan dari Jebakan False Positive (Quality Gate Rejection)
> **Teks**: *"Bupati Aceh Besar secara resmi membuka **acara** perayaan hari ulang tahun kota yang dihadiri ratusan warga di lapangan terbuka."*
- Papan Skor: `ecosystem` hanya mendapat Weak: `"acara"` (1 poin).
- Evaluasi Threshold: $1 < 3$ (**GAGAL**).
- **Keputusan**: 🛡️ **Tolak Auto-label! Label = `"unclassified"` $\rightarrow$ Dialirkan ke `needs_review.csv`**.

#### 📌 Use Case 4: Skenario Skor Imbang / Seri (Tie-Break Dilemma)
> **Teks**: *"Pemerintah meluncurkan program **subsidi modal** untuk pelaku usaha sekaligus menyediakan sertifikasi **keterampilan digital** bagi para pemuda."*
- Papan Skor:
  - `funding`: Medium `"subsidi"` (2) + Medium `"modal"` (2) = **4 poin**.
  - `talent`: Medium `"keterampilan"` (2) + Medium `"digital"` (2) = **4 poin**.
- Evaluasi: Skor seimbang (4 vs 4). Tingkat ketidakpastian (*uncertainty*) tinggi.
- **Keputusan**: ⚠️ **Dialirkan ke `needs_review.csv`** agar manusia yang membaca kalimat utuh menentukan fokus utamanya.


---

## 7. Mitigasi Bias & Validasi Distribusi Data (Class Imbalance)

Dalam Machine Learning, jika 1 kelas menguasai 80% dataset (*majority class*), model akan malas belajar dan cenderung selalu menebak kelas mayoritas tersebut.

### Dua Skenario Bias yang Harus Diantisipasi:

1. **Bias Dominasi Topik (*Topic Skewness*)**:
   - *Gejala*: Topik `digitalization` muncul di 60% data karena kata "digital" atau "aplikasi" sangat sering disebut di era modern.
   - *Solusi*: Turunkan kata yang terlalu umum (seperti "digital" atau "online") dari tingkat `strong`/`medium` ke tingkat `weak`. Pastikan tidak ada satu topik pun yang mendominasi $>40\%$ dari total dataset.

2. **Bias Sentimen Netral (*Neutral Bias*)**:
   - *Gejala*: Media berita secara alami cenderung faktual, sehingga sentimen `neutral` bisa mencapai 80-90%.
   - *Solusi*: Ini adalah sifat alami domain berita jurnalistik (*domain reality*), bukan error. Namun, kita harus memastikan kata-kata hambatan (*bottleneck*, *birokrasi lambat*, *gagal*) benar-benar ditangkap sebagai sentimen `negative`.

---

## 8. Bahan Interview & Presentasi: Cara Menjawab Pertanyaan Kunci

Berikut panduan menjawab pertanyaan penguji, dosen, atau recruiter saat presentasi proyek ini:

### Pertanyaan 1: *"Kenapa kalian tidak melabeli 13.840 baris ini pakai LLM API (seperti GPT-4 / Claude) saja?"*
> **Jawaban Profesional**:  
> *"Ada 3 pertimbangan utama dalam arsitektur ML kami:  
> 1. **Explainability & Auditability**: Dengan Programmatic Weak Supervision berbasis aturan terbobot, setiap label memiliki bukti matematis kata kunci mana yang memicunya. Pada LLM API, keputusannya bersifat 'black-box' dan rentan halusinasi.  
> 2. **Reproducibility**: Aturan heuristik kami 100% deterministik. Dataset yang sama selalu menghasilkan label yang identik tanpa variasi temperatur.  
> 3. **Efisiensi Sumber Daya & Latensi**: Memproses 13.840 baris dengan LLM API memerlukan ribuan panggilan jaringan, potensi rate-limiting, dan biaya token yang signifikan. Pipeline heuristik kami selesai dalam beberapa detik secara offline di mesin lokal."*

### Pertanyaan 2: *"Bagaimana kalian menjamin data hasil auto-labeling ini tidak bias dan menyesatkan model ML di Fase 4?"*
> **Jawaban Profesional**:  
> *"Kami menerapkan pendekatan **Human-in-the-Loop** dengan **Uncertainty Sampling**:  
> Data tidak langsung ditelan mentah-mentah. Kami membaginya menjadi dua jalur: data dengan skor confidence tinggi ($\ge 3$) masuk ke `auto_labeled.csv`, sedangkan data dengan confidence rendah atau ambigu masuk ke `needs_review.csv` untuk diverifikasi manual oleh manusia.  
> Selain itu, kami melakukan **Spot Check** acak pada data hasil auto-label untuk memastikan Error Rate di bawah 10% sebelum data disatukan ke `labeled_dataset_final.csv`."*

### Pertanyaan 3: *"Mengapa menggunakan pembobotan kata 3-tier (strong, medium, weak) daripada hitungan frekuensi Bag-of-Words biasa?"*
> **Jawaban Profesional**:  
> *"Karena specificity kata dalam domain kewirausahaan tidak setara. Frasa seperti 'modal ventura' memiliki Information Gain yang sangat tinggi untuk topik `funding`, sehingga layak mendapatkan bobot Strong (3). Sebaliknya, kata seperti 'bisnis' atau 'uang' bisa muncul di topik apa saja, sehingga jika diberi bobot yang sama akan menyebabkan False Positive yang tinggi. Sistem multi-tier ini mengemulasi cara kerja Naive Bayes secara terarah tanpa memerlukan prior distribution yang kompleks."*

### Pertanyaan 4: *"Bagaimana jika satu paragraf membahas dua topik sekaligus (misalnya pendanaan dan pelatihan talenta)?"*
> **Jawaban Profesional**:  
> *"Dalam taksonomi single-label multiclass, kami menggunakan mekanisme **Argmax Competition**. Topik dengan akumulasi skor bobot kata tertinggi yang akan dipilih sebagai topik utama (primary topic). Jika terjadi persaingan seimbang (skor sama kuat antar topik), confidence score menjadi rendah dan sistem secara otomatis mengalirkannya ke jalur `needs_review.csv` agar diputuskan oleh manusia berdasarkan konteks kalimat intinya."*

---
*Dokumen ini merupakan panduan resmi konseptual Fase 3 GRAK 2026 Sprint 3.*
