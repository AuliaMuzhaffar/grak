# 🧠 Deep Dive Konsep & Arsitektur Fase 2: Data Cleaning & Deduplication

> **GRAK 2026 · Sprint 3 · Materi 4**  
> **Tujuan Dokumen**: Panduan konsep mendalam, intuisi matematika tanpa rumus rumit, dan bahan persiapan interview / presentasi proyek.

---

## 📌 DAFTAR ISI
1. [Mengapa Fase 2 Sangat Kritis? (The "Why")](#1-mengapa-fase-2-sangat-kritis-the-why)
2. [Arsitektur Pipeline 6-Tahap](#2-arsitektur-pipeline-6-tahap)
3. [Bedah Masalah: Mengapa Exact Dedup Saja Tidak Cukup?](#3-bedah-masalah-mengapa-exact-dedup-saja-tidak-cukup)
4. [Jaccard Similarity & Jebakan O(N^2)](#4-jaccard-similarity--jebakan-on2)
5. [Solusi Skala Besar: Shingling + MinHash + LSH](#5-solusi-skala-besar-shingling--minhash--lsh)
6. [Klasifikasi Relevansi Wilayah (Aceh Confidence)](#6-klasifikasi-relevansi-wilayah-aceh-confidence)
7. [Bahan Interview & Presentasi: Cara Menjawab Pertanyaan Kunci](#7-bahan-interview--presentasi-cara-menjawab-pertanyaan-kunci)

---

## 1. Mengapa Fase 2 Sangat Kritis? (The "Why")

Di dunia nyata Machine Learning dan NLP (Natural Language Processing), ada pepatah terkenal:
> *"Garbage In, Garbage Out."*

Jika kita langsung memasukkan 14.818 paragraf mentah hasil scraping ke model ML di Fase 4, kita akan menghadapi 3 masalah fatal:

### A. Kebocoran Data (Data Leakage) Antar Train dan Test Split
Media online di Indonesia sangat sering melakukan **sindikasi berita** (berita yang sama diterbitkan ulang di berbagai portal daerah dengan sedikit modifikasi pembuka/penutup).
- **Contoh**:
  - *Portal Antara*: "BANDA ACEH - Pemerintah Aceh mengumumkan program pendanaan inkubator bisnis digital..."
  - *Portal Daerah*: "SERAMBINEWS.COM, BANDA ACEH - Pemerintah Aceh mengumumkan program pendanaan inkubator bisnis digital..."
- Kedua teks ini **mirip 95%**, tetapi beda sedikit di awal kata.
- Jika satu masuk ke data latih (*training set*) dan yang satu lagi masuk ke data uji (*test set*), model akan mendapatkan skor akurasi tinggi palsu (*overfitting*) karena model hanya "menghafal" berita yang sama, bukan belajar polanya secara riil.

### B. Distorsi Bobot TF-IDF (Feature Space Poisoning)
TF-IDF memberikan bobot tinggi pada kata-kata yang spesifik. Teks navigasi berita seperti *"Baca Juga"*, *"Simak breaking news"*, atau *"Editor: Redaksi"* jika tidak dibersihkan akan dianggap fitur penting oleh algoritma, sehingga merusak topik model (Topic Modeling).

### C. Bias Sentimen Palsu
Paragraf non-artikel (misal copyright atau ajakan follow medsos) akan membingungkan pelabelan sentimen bisnis/startup.

---

## 2. Arsitektur Pipeline 6-Tahap

Data mentah disaring secara bertahap menggunakan prinsip corong (*funnel filtration*):

```text
[ 14.818 Paragraf Mentah ] (paragraphs_raw.csv)
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 1: Text Normalization                            │
│ → Hapus URL, alamat email, dan emoji                   │
│ → Hapus karakter non-printable                         │
│ → Rapikan multiple spasi menjadi 1 spasi               │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 2: Structural Validation Heuristics              │
│ → Minimal 5 kata, Maksimal 500 kata                    │
│ → Rasio huruf alfabet minimal 50% (bukan angka/simbol) │
│ → Minimal 3 kata unik (bukan teks berulang)            │
│ → Panjang karakter minimal 50                          │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 3: Boilerplate Stripping                         │
│ → Cek 60+ pola kata media ("baca juga", "penulis:")   │
│ → Regex pola navigasi: "foto:", "halaman 1", dsb.      │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 4: Exact Deduplication (O(N))                    │
│ → Hapus teks yang 100% sama persis                     │
│ → Cukup simpan kemunculan pertama                      │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 5: Near-Duplicate Detection (MinHash LSH)        │
│ → Deteksi teks yang mirip >= 85%                       │
│ → Tangani sindikasi berita dan parafrase editorial    │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TAHAP 6: Aceh Context Tagging                          │
│ → Klasifikasi confidence: HIGH, MEDIUM, LOW            │
│ → Berdasarkan kemunculan kata kunci di teks vs judul   │
└────────────────────────────────────────────────────────┘
          │
          ▼
[ ~6.000 - 8.000 Paragraf Bersih ] (public_text_news_clean.csv)
```

---

## 3. Bedah Masalah: Mengapa Exact Dedup Saja Tidak Cukup?

**Exact Deduplication** hanya mengecek kesamaan 100% string:
```python
text_a == text_b
```
Atau menggunakan hash tabel (seperti `df.drop_duplicates(subset=['text'])`). Ini sangat cepat (kompleksitas Waktu O(N)).

Tetapi pada berita online:
- Teks A: *"DiskopUKM Aceh gelar pelatihan startup di Banda Aceh."*
- Teks B: *"DiskopUKM Aceh gelar pelatihan startup di Banda Aceh hari ini."* (ada tambahan kata 'hari ini')

Bagi komputer, `Text A == Text B` bernilai **FALSE**. Akibatnya, kedua teks ini tetap disimpan padahal pesannya sama persis! Itulah mengapa kita wajib memiliki **Near-Duplicate Detection (Fuzzy Matching)**.

---

## 4. Jaccard Similarity & Jebakan O(N^2)

### Konsep Dasar Jaccard Similarity
Bagaimana cara kita mengukur kemiripan antara dua teks A dan B secara matematis?
Caranya adalah melihat irisan kata (kata yang muncul di kedua teks) dibagi dengan gabungan kata (semua kata unik dari kedua teks):

```text
Kemiripan Jaccard = (Jumlah kata yang SAMA di teks A dan B)
                    ──────────────────────────────────────────
                    (Jumlah TOTAL seluruh kata unik A dan B)
```

**Contoh Sederhana**:
- Teks A: `[saya, suka, kopi, gayo]` (4 kata unik)
- Teks B: `[saya, suka, kopi, robusta]` (4 kata unik)
- Kata yang sama (irisan): `[saya, suka, kopi]` = 3 kata
- Total seluruh kata unik (gabungan): `[saya, suka, kopi, gayo, robusta]` = 5 kata

Maka nilai kemiripannya adalah:
```text
Kemiripan = 3 / 5 = 0.60 (atau 60%)
```

### Jebakan Perbandingan Berpasangan: Kompleksitas O(N^2)
Jika kita ingin membandingkan setiap paragraf dengan semua paragraf lainnya dalam kumpulan data sebesar N baris:
- Dokumen ke-1 harus dibandingkan dengan (N - 1) dokumen lain.
- Dokumen ke-2 harus dibandingkan dengan (N - 2) dokumen lain.
- Dan seterusnya...

Rumus total perbandingan berpasangan adalah:
```text
Total Pasangan = (N x (N - 1)) / 2
```

Mari kita hitung dengan data kita yang berjumlah **14.818 baris**:
```text
Total Pasangan = (14.818 x 14.817) / 2
               = 219.558.306 / 2
               = 109.779.153 perbandingan!
```

**Hampir 110 JUTA kali operasi!**
Jika satu kali operasi perbandingan teks butuh 0.0001 detik di Python:
`110.000.000 x 0.0001 detik = 11.000 detik = sekitar 3 JAM LEBIH!`

Itulah alasan mengapa pada script lama (`03_cleaning.py`), pembuat script terpaksa menulis:
```python
if len(df) > 2000:
    print("Dataset besar, skip near-duplicate check")
```
Karena komputernya tidak sanggup menjalankan 110 juta perbandingan jika datanya lebih dari 2.000 baris.

---

## 5. Solusi Skala Besar: Shingling + MinHash + LSH

Untuk memproses 14.818 data dalam hitungan **detik**, kita menggunakan teknik yang dipakai Google dan Twitter: **MinHash LSH**.

Teknik ini terdiri dari 3 tahapan:

### Tahap A: k-Shingling (Memecah Kalimat Jadi Potongan Frasa)
Daripada memecah kalimat menjadi kata tunggal (Bag-of-Words) yang menghilangkan urutan kalimat, kita memecahnya menjadi potongan 3 kata berurutan (k-shingles dengan k=3).

**Contoh**:
Kalimat: *"Pemerintah Aceh mendukung startup digital"*
Potongan 3-shingles:
1. `pemerintah aceh mendukung`
2. `aceh mendukung startup`
3. `mendukung startup digital`

Dengan cara ini, susunan konteks kalimat tetap terjaga.

---

### Tahap B: MinHash (Kompresi Vektor Ekstrem)
Jika kita punya ribuan potongan frasa di seluruh dataset, menyimpan dan mencocokkannya akan memakan memori sangat besar.

MinHash bekerja dengan prinsip yang ditemukan oleh ilmuwan Andrei Broder:
- Setiap teks dikompresi menjadi sebuah deretan kecil angka tetap, yang disebut **Signature Vektor** (biasanya sepanjang 128 angka).
- Sifat ajaib MinHash: **Probabilitas dua teks memiliki angka hash yang sama bernilai sama persis dengan tingkat kemiripan Jaccard kedua teks tersebut.**
- Jadi, jika Teks A dan Teks B kembarannya 85%, maka sekitar 85% dari 128 angka pada signature mereka akan identik!
- Kita tidak lagi membandingkan teks panjang, cukup membandingkan 128 angka integer.

---

### Tahap C: LSH (Locality-Sensitive Hashing) — Membunuh Beban O(N^2)
Meskipun setiap teks sudah diringkas menjadi 128 angka, membandingkan 14.818 vektor secara berpasangan masih memakan waktu. 

Di sinilah peran **LSH**:
1. Vektor 128 angka tersebut dibagi menjadi beberapa kelompok (disebut **Bands**), misalnya 16 bands di mana masing-masing band berisi 8 angka.
2. Setiap band dimasukkan ke dalam keranjang (*hash bucket*).
3. Dua teks yang memiliki kemiripan tinggi (misalnya >= 85%) dipastikan memiliki probabilitas hampir 100% untuk jatuh ke dalam **keranjang yang sama** di setidaknya salah satu band.
4. **Hasilnya**: Kita TIDAK PERLU membandingkan Dokumen A dengan 14.817 dokumen lain! Kita HANYA membandingkan Dokumen A dengan dokumen yang jatuh di keranjang yang sama.

```text
ANALOGI SEDERHANA:
Bayangkan kamu mencari orang yang wajahnya mirip denganmu di stadion berisi 15.000 orang.

- Cara Lama (Pairwise O(N^2)):
  Kamu mendatangi 15.000 orang satu per satu dan menatap wajah mereka. 
  Kamu harus melakukan 110 juta kali tatap muka.

- Cara MinHash LSH:
  Panitia stadion membuat pengumuman di pengeras suara:
  "Semua orang dengan warna baju biru, tinggi 170-175 cm, kumpul di Pintu Barat!"
  Kamu hanya perlu pergi ke Pintu Barat dan melihat segelintir orang yang ada di sana.
  Waktu pencarian turun dari berjam-jam menjadi hitungan detik!
```

---

## 6. Klasifikasi Relevansi Wilayah (Aceh Confidence)

Mengapa kita tidak langsung membuang paragraf yang tidak ada kata "Aceh"-nya?

Perhatikan contoh struktur berita media:
- **Judul Artikel**: *"DiskopUKM Dorong Akselerasi Startup Digital di Banda Aceh"*
- **Paragraf 1**: *"Pemerintah Aceh terus meningkatkan literasi digital generasi muda..."* 
  *(Menyebut kata Aceh -> **HIGH**)*
- **Paragraf 2**: *"Mentor program menjelaskan pentingnya validasi ide dan product-market fit sebelum mencari investor."* 
  *(TIDAK menyebut kata Aceh sama sekali)*

Jika kita memakai aturan kaku "Hapus semua teks tanpa kata Aceh", maka **Paragraf 2 akan terbuang**. Padahal Paragraf 2 adalah substansi utama tentang dunia startup!

Oleh karena itu kita membuat sistem tingkatan (Confidence Scoring):

| Level | Aturan Logika | Arti Bisnis |
|---|---|---|
| **HIGH** | Teks paragraf itu sendiri secara langsung menyebut kata "Aceh" atau nama kota/kabupaten/kampus di Aceh (Banda Aceh, Lhokseumawe, USK, Gayo, Pidie, dll.) | Paragraf ini 100% spesifik berbicara tentang wilayah Aceh. |
| **MEDIUM** | Teks paragraf tidak menyebut Aceh, TETAPI judul artikelnya menyebut Aceh. | Paragraf ini adalah bagian dari artikel lokal Aceh, memuat konteks yang tetap relevan. |
| **LOW** | Teks paragraf DAN judul artikel sama-sama tidak menyebut kata kunci Aceh. | Kemungkinan berita nasional yang tidak sengaja tersaring saat pencarian awal. |

---

## 7. Bahan Interview & Presentasi: Cara Menjawab Pertanyaan Kunci

Jika penguji atau interviewer bertanya:

**Pertanyaan 1**: *"Kenapa kalian tidak hanya pakai `drop_duplicates()` bawaan pandas?"*
> **Jawaban**: 
> "`drop_duplicates()` di Pandas hanya menangani duplikasi persis (exact match 100%). Pada data media berita online, terjadi banyak sindikasi artikel di mana isi beritanya 90% sama tetapi ada sedikit perbedaan seperti atribusi kota di awal paragraf ('Banda Aceh (Antara) -') atau nama editor di akhir. Jika hanya exact match, data duplikat ini akan lolos dan menyebabkan data leakage antara train dan test split. Oleh karena itu kami menerapkan near-duplicate detection."

**Pertanyaan 2**: *"Kenapa memilih MinHash LSH dibanding cosine similarity atau Jaccard biasa?"*
> **Jawaban**:
> "Karena masalah skalabilitas. Jaccard similarity berpasangan membutuhkan perbandingan O(N^2). Dengan 14.818 paragraf, ada sekitar 110 juta perbandingan yang memakan waktu berjam-jam di memori. MinHash mengompresi dokumen menjadi signature berdimensi tetap (128 nilai hash), dan LSH (Locality-Sensitive Hashing) mengelompokkan dokumen serupa ke dalam ember yang sama via hash tables, sehingga kita hanya membandingkan kandidat yang berada di bucket yang sama. Kompleksitasnya turun mendekati O(N), selesai hanya dalam waktu 1-2 menit."

**Pertanyaan 3**: *"Bagaimana kalian menentukan ambang batas (threshold) 0.85?"*
> **Jawaban**:
> "Threshold 0.85 (85% kemiripan) adalah titik temu optimal antara Precision dan Recall. Jika threshold terlalu rendah (misal 0.60), dua paragraf yang membahas topik sama tetapi kalimatnya berbeda bisa terhapus secara tidak sengaja (False Positive). Jika threshold terlalu tinggi (misal 0.95), variasi parafrase jurnalisme berita akan lolos (False Negative). Angka 0.85 memastikan hanya parafrase editorial dan kutipan sindikasi yang dibersihkan."
