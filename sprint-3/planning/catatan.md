# 📓 Catatan Belajar: Konsep Shingling, MinHash, & LSH

> Dokumen ini mencatat penjelasan mendalam tentang cara kerja **k-Shingling**, **MinHash**, dan **LSH (Locality-Sensitive Hashing)** dengan bahasa sederhana, tabel skenario, serta studi kasus nyata.

---

## 1. Pertanyaan Kunci: Kenapa Harus "Angka Terkecil" (Minimum)?

Ketika kita memecah kalimat menjadi potongan kata (*shingles*), kita memasukkan kata-kata tersebut ke dalam mesin pengacak angka (*Fungsi Hash*).
Lalu kita memilih **angka yang paling kecil**.

**Pertanyaan kritis**:
*Bagaimana mungkin hanya dengan mengambil satu angka terkecil, komputer bisa tahu dua teks itu mirip 50%, 80%, atau tidak mirip sama sekali?*

---

## 2. Bedah Kasus Nyata: Mengapa Peluangnya Bisa Tepat Sama?

Bayangkan kita punya dua paragraf berita yang mirip:
- **Dokumen A**: memuat kata `[kopi, aceh, gayo]` (3 kata)
- **Dokumen B**: memuat kata `[kopi, aceh, enak]` (3 kata)

Mari kita rekap faktanya:
- Kata yang **sama di kedua dokumen (irisan)**: `kopi`, `aceh` (ada **2 kata**)
- Total **seluruh kata unik (gabungan)**: `kopi`, `aceh`, `gayo`, `enak` (ada **4 kata**)
- **Tingkat kemiripan asli**:  
  `2 dibagi 4 = 0.5 (atau 50% mirip)`

---

## 3. Pembuktian: Tabel 4 Skenario Pengacakan

Mesin hash mengocok ke-4 kata tersebut dan membagikan nomor tiket acak.
Siapa pun kata yang memegang nomor tiket paling kecil, dia yang menjadi **Juara 1 (Pemenang Tiket Terkecil)**.

Karena ada 4 kata yang bertanding, ada **4 skenario pemenang yang mungkin terjadi**:

| Skenario | Pemenang Juara 1 (Tiket Terkecil) | Kata Terkecil Dokumen A | Kata Terkecil Dokumen B | Apakah Angka MinHash A dan B Sama? |
|:---:|:---:|:---:|:---:|:---:|
| **Skenario 1** | Kata **`kopi`** menang tiket terkecil (misal dapat nomor 5) | `kopi` (5) | `kopi` (5) | **SAMA ✅** (karena `kopi` ada di A dan B) |
| **Skenario 2** | Kata **`aceh`** menang tiket terkecil (misal dapat nomor 8) | `aceh` (8) | `aceh` (8) | **SAMA ✅** (karena `aceh` ada di A dan B) |
| **Skenario 3** | Kata **`gayo`** menang tiket terkecil (misal dapat nomor 2) | `gayo` (2) | `kopi` atau `aceh` (angka lebih besar) | **BEDA ❌** (karena `gayo` hanya ada di Dokumen A) |
| **Skenario 4** | Kata **`enak`** menang tiket terkecil (misal dapat nomor 1) | `kopi` atau `aceh` (angka lebih besar) | `enak` (1) | **BEDA ❌** (karena `enak` hanya ada di Dokumen B) |

---

## 4. Kesimpulan Sederhana MinHash

Mari hitung hasilnya dari tabel di atas:
- Total skenario yang mungkin terjadi: **4 skenario**.
- Skenario di mana angka MinHash A dan B bernilai **SAMA**: **2 skenario** (yaitu jika yang menang adalah `kopi` atau `aceh`).
- Peluang MinHash bernilai SAMA:  
  **`2 dibagi 4 = 50%`**!

> 💡 **TITIK TERANGNYA:**  
> Persentase peluang angka MinHash bernilai sama (**50%**) ternyata **PERSIS SAMA** dengan persentase kemiripan kata asli kedua teks tersebut (**50%**)!
>
> Inilah mengapa kita mengocoknya sebanyak **128 kali pengacakan berbeda**:
> - Jika dua teks mirip 85%, maka dari 128 kali pengocokan, rata-rata sekitar **109 kali** angka terkecilnya akan sama persis.
> - Komputer tidak perlu lagi membaca teks kalimat, cukup menghitung berapa kali angka terkecil mereka kembar!

---

## 5. Tahap C: LSH (Locality-Sensitive Hashing) & Sistem Keranjang

Meskipun MinHash sudah mengubah teks menjadi 128 angka, kita masih punya masalah:
Jika kita punya **14.818 dokumen**, membandingkan deretan 128 angka secara berpasangan satu per satu tetap membutuhkan:
`14.818 x 14.817 / 2 = 109.779.153 kali perbandingan (hampir 110 juta kali)!`

Komputer masih akan bekerja keras selama berjam-jam jika harus membandingkan semuanya. 

Di sinilah **LSH** menjadi solusi penyelamat.

### A. Konsep Dasar LSH: "Sengaja Bikin Tabrakan" (Intentional Collisions)
- Pada fungsi hash biasa (misal password / kriptografi): jika data beda sedikit saja, kodenya dibuat beda total.
- Pada **LSH**: jika data mirip, kodenya **sengaja diarahkan agar jatuh ke dalam keranjang (bucket) yang sama**.

### B. Cara Kerja LSH: Membagi Menjadi Bands (Kelompok Pita)
Vektor 128 angka MinHash dibagi menjadi beberapa kelompok pita (*Bands*).
Misalnya: 128 angka dibagi menjadi **16 Bands**, masing-masing Band berisi **8 angka** (16 x 8 = 128).

```text
Vektor 128 Angka dari Satu Dokumen:
┌────────────────────────────────────────────────────────┐
│ Band 1  (angka ke 1 - 8)   : [12, 85, 40, 91, 04, ...] │ ──► Masuk ke Keranjang A
│ Band 2  (angka ke 9 - 16)  : [77, 13, 02, 90, 55, ...] │ ──► Masuk ke Keranjang B
│ Band 3  (angka ke 17 - 24) : [31, 44, 88, 12, 60, ...] │ ──► Masuk ke Keranjang C
│ ...                                                    │
│ Band 16 (angka ke 121 - 128): [09, 18, 73, 25, 41, ...]│ ──► Masuk ke Keranjang X
└────────────────────────────────────────────────────────┘
```

### C. Aturan Emas Keranjang LSH
1. **Kandidat Pasangan Mirip (*Candidate Pairs*)**:
   Jika Dokumen 1 dan Dokumen 2 memiliki potongan 8 angka yang SAMA PERSIS di **minimal salah satu Band saja**, kedua dokumen tersebut akan **jatuh ke dalam keranjang yang sama**.
2. **Pengabaian Otomatis**:
   Jika dua dokumen tidak pernah satu keranjang di ke-16 Band, komputer **tidak akan pernah membandingkan keduanya sama sekali**!

### D. Mengapa LSH Super Cepat?
- Dokumen tentang *"Startup Kopi Takengon"* mungkin hanya akan satu keranjang dengan **3 dokumen lain** yang merupakan sindikasi berita serupa.
- Komputer **HANYA membandingkan dokumen tersebut dengan 3 dokumen tadi**.
- Komputer **TIDAK PERLU** membandingkannya dengan 14.815 dokumen lain yang membahas topik berbeda!
- Jumlah perbandingan turun dari **110 juta kali** menjadi hanya **beberapa ribu kali**.
- Waktu komputasi turun drastis dari **3 jam menjadi 10-30 detik saja!**

---

## 6. Rangkuman Pipeline Lengkap (A -> B -> C)

```text
[ Teks Paragraf Asli ]
        │
        ▼ (Tahap A: k-Shingling, k=3)
[ Kumpulan Potongan Frasa 3 Kata ]
        │
        ▼ (Tahap B: MinHash, num_perm=128)
[ Vektor Berisi 128 Angka Integer ]
        │
        ▼ (Tahap C: LSH Bands & Buckets)
[ Dokumen Mirip Otomatis Masuk ke Keranjang yang Sama ]
        │
        ▼
[ Hapus Duplikat Hanya dari Dokumen yang Berada di Keranjang yang Sama ]
        │
        ▼
[ Dataset Bersih Bebas Duplikasi Sindikasi! ✅ ]
```
