# Audit Log: Rekonsiliasi Metrik Riset Startup Aceh 2026

Dokumen ini mencatat audit integritas data dan perbandingan antara klaim dalam draf laporan awal dengan data aktual yang dihitung ulang langsung dari dataset `combined_text.csv` (N=7097), `survey_structured.csv` (N=12), dan log pemrosesan scraping.

## 1. Tabel Rekonsiliasi Klaim Utama

| Item Analisis | Klaim Awal di Laporan | Angka Aktual Terverifikasi | Sumber Data Aktual | Tindakan Koreksi |
|---|---|---|---|---|
| **Sentimen Berita** | 86,5% netral | **81,21% netral** (0,51% negatif, 18,28% positif) | `combined_text.csv` (n=6.648) | Dikoreksi di semua slide & visualisasi |
| **Volume Paragraf Berita** | N = 13.840 | **N = 6.648 relevan** (13.840 total setelah cleaning; 7.192 out-of-domain dibuang) | `label_stats.json` & `quality_report.json` | Dijelaskan transparan dalam Funnel Data |
| **Prioritas Akses Pendanaan** | 58,3% responden menaruh di peringkat #1 | **50,0%** (6 dari 12 responden menaruh di ranking #1 tantangan) | `survey_structured.csv` (`tantangan_1`) | Angka diperbarui menjadi 50,0% |
| **Ketiadaan Akses Pendanaan** | *(Belum diangkat sebagai temuan utama)* | **83,3% (10 dari 12 founder) belum pernah menerima pendanaan** | `survey_structured.csv` (`pernah_pendanaan`) | Dijadikan headline utama Insight 3 & H1' |
| **Founder Mandiri Ber-revenue** | *(Belum diangkat)* | **6 dari 7 startup ber-revenue/scaling bertumbuh tanpa modal luar (100% bootstrap)** | `survey_structured.csv` (cross funding vs status) | Dijadikan bukti sentral Insight 3 |
| **Tindak Lanjut Program** | 91,7% founder nihil pendampingan | **66,7% dari peserta program (4 dari 6) tidak menerima tindak lanjut** (atau 33,3% dari total 12) | `survey_structured.csv` (`followup_program`) | Dikoreksi agar jujur terhadap basis responden |
| **Dukungan R&D vs Marketing** | 0% responden menerima dukungan R&D | **1 responden menerima Tech/Coding**; bukti survei untuk H6 sangat lemah (n=6) | `survey_structured.csv` (`jenis_dukungan`) | Ditopang bukti makro berita (UMKM 330 vs Startup 77) |
| **Asal Founder Luar Banda Aceh** | 100% founder luar BA lahir dari kampus | Hanya ada 5 responden luar BA (termasuk 1 Jakarta); yang menyebut kampus hanya 2 | `survey_structured.csv` | Diturunkan statusnya menjadi *Indikatif / Studi Kasus* |
| **Penyebutan Remote Work Sosmed** | 44 unit percakapan remote work | **Hanya 9 unit** yang secara eksplisit menyebut remote/wfa/freelance/jakarta | `combined_text.csv` (social_media n=311) | Narasi *Remote Arbitrage* dibuang dari insight utama |
| **Diskusi Investor di Sosmed** | Diskusi VC lokal bernilai nol | **34 unit** sosmed menyebut investor/venture/modal ventura/angel | `combined_text.csv` (social_media) | Klaim ekstrem "nol" dihapus |
| **Sebaran Pasar SuratPlus** | 95%+ pendapatan berasal dari Jawa | **200.000+ pengguna terdaftar (1,8 juta kunjungan web) di 250 kab/kota; Banda Aceh urutan ke-30** | Transkrip wawancara narasumber SuratPlus | Diganti dengan angka riil yang jauh lebih impresif |
| **Tingkat Validasi Hipotesis** | "TERVALIDASI SEMPURNA 4/4" untuk semua H1–H6 | **Rubrik Kekuatan Bukti**: 2 Kuat, 4 Sedang, 1 Indikatif | Triangulasi metodologi campuran | Standar kejujuran akademik diterapkan penuh |

---

## 2. Ringkasan Funnel Pemrosesan Data

```
[1.350 Artikel Ditemukan (Discovery)]
       ↓
[1.347 URL Berhasil Di-resolve] (746 percobaan gagal / anti-bot handled)
       ↓
[1.231 Artikel Diekstrak dari 243 Portal]
       ↓
[14.818 Paragraf Mentah]
       ↓
[13.840 Paragraf Setelah Pembersihan & Deduplikasi]
       ↓
[7.192 Paragraf Out-of-Domain Dibuang ke Ingestion Shield]
       ↓
[6.648 Paragraf Berita Relevan] + [311 Sosmed] + [113 Wawancara] + [25 Teks Survei]
       ↓
[7.097 Unit Teks Dianalisis dalam Triangulasi] + [12 Responden Survei Terstruktur]
```

---

## 3. Matriks Kekuatan Bukti Final

| Insight | Status Bukti | Justifikasi Metodologis |
|---|---|---|
| **Insight 1: Paling Terlihat, Paling Tidak Dipercaya** | ✅ **KUAT** | Triangulasi 3 pilar: Berita (55,9% exposure, rasio seremoni 3,3:1) + Survei (skor kepuasan 1,67/5) + Wawancara (SuratPlus & PST). |
| **Insight 2: Ekosistem Startup rasa UMKM** | 🟡 **SEDANG–KUAT** | Berita makro kuat (UMKM 330 vs Startup 77 artikel) + Wawancara PST (pelatihan marketplace vs kebutuhan mesin cetak). |
| **Insight 3: Tumbuh Tanpa Modal, Tapi Lambat** | ✅ **KUAT** | Kuantitatif survei solid (10/12 unbacked, 6/7 ber-revenue tanpa modal, keyakinan 4,08 vs ekosistem 2,58) + Narasi bootstrap SuratPlus & Bepal. |
| **Insight 4: Jurang Pasca-Hibah** | 🟡 **SEDANG** | Kualitatif mendalam PST (vakum pasca-kontrak) + Survei (4/6 tanpa tindak lanjut) + Berita (hanya 13,8% liputan hasil). |
| **Insight 5: Defisit Talenta Mendalam & Panutan** | 🟡 **SEDANG** | Wawancara 3 narasumber (ahli molding diimpor dari Batan, mentor hijrah ke Jakarta) + Survei (skor mentor 2,08/5, talenta masuk top-3). |
| **Insight 6: Pasarnya Ada, Tapi Bukan di Aceh** | 🟡 **SEDANG–KUAT** | Data riil SuratPlus (200.000+ user terdaftar & 1,8 juta kunjungan web di 250 kota, Banda Aceh #30) + Bepal (antusiasme 8,5 tapi WTP rendah) + Survei kemudahan pasar 3,75 tapi lokal minta gratisan. |
| **Temuan Emergen: Ketergantungan Kampus Luar Banda Aceh** | ⚪ **INDIKATIF** | Sampel survei luar Banda Aceh kecil (n=5) dan 1 studi kasus PST di Lhokseumawe. Diposisikan sebagai hipotesis riset lanjutan. |

---
*Catatan: Dokumen ini digenerate secara otomatis oleh `scraping/13_verified_metrics.py` sebagai rujukan utama semua visualisasi dan slide deck.*
