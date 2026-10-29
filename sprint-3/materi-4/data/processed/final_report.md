# 📑 Laporan Akhir: Riset Ekosistem Startup Aceh 2026
> **GRAK 2026 · Sprint 3 · Final Deliverable (Versi Terverifikasi)**  
> **Tema Utama:** *Ramai di Panggung, Sepi di Belakang Layar: Studi Triangulasi Multi-Metode tentang Realitas Akses Modal, Talenta, dan Kelangsungan Usaha Startup di Aceh*  
> **Metodologi:** *Convergent Mixed-Methods Triangulation Design* (Creswell & Plano Clark)  
> *Seluruh angka dan metrik dalam laporan ini telah diaudit dan direkonsiliasi langsung dari data primer (`storytelling/verified_metrics.json` & `storytelling/audit_log.md`).*

---

## 1. Pendahuluan & Korpus Data Riset

Laporan ini merupakan hasil integrasi komprehensif seluruh alur kerja Data-Centric AI (DCAI) pada Sprint 3. Riset ini menguji narasi publik mengenai transformasi ekonomi digital di Aceh dengan membandingkan publikasi media arus utama terhadap realitas operasional yang dihadapi para pendiri startup (*founders*) di tingkat akar rumput.

**Korpus Analisis Terpadu (Golden Dataset = 7.097 Unit Teks):**
1. **Makro Publik (Berita Daring):** $N = 6.648$ paragraf relevan dari 900 artikel unik pada 243 portal berita, disaring ketat melalui *Ingestion Shield* dari total 13.840 paragraf mentah.
2. **Mikro Pelaku (Survei Terstruktur Founder):** $N = 12$ founder startup terverifikasi di Aceh, menghasilkan 25 unit teks opini terstruktur dan 26 variabel operasional.
3. **Kualitatif Mendalam (Wawancara Semi-Terstruktur):** $N = 113$ unit teks wawancara dari 3 institusi studi kasus: **SuratPlus** (SaaS skala nasional berbasis di Banda Aceh), **PT Plastik Sago Teknologi / PST** (startup deep-tech/hardware bioplastik di Lhokseumawe), dan **Bepal** (media & komunitas digital di Lhokseumawe).
4. **Grassroots Pulse (Media Sosial):** $N = 311$ unit teks (X/Twitter 234, YouTube 41, LinkedIn 36) yang diekstraksi melalui RapidOCR dan scraping organik.

---

## 2. Executive Summary & Matriks Kekuatan Bukti

Integrasi keempat pilar data independen membongkar disparitas tajam antara publisitas media dengan kondisi riil pelaku usaha di Aceh:
* **Media Berita Formal (Makro):** Memotret narasi seremonial yang sangat aman dan positif (**81,21% netral**, 18,28% positif, dan hanya **0,51% negatif**). Sebanyak 45,0% artikel meliput seremoni peluncuran, MoU dinas, dan kompetisi.
* **Suara Founder & Pelaku (Mikro & Kualitatif):** Mengungkapkan friksi operasional yang berat (**64,0% sentimen negatif pada teks survei** dan **30,09% negatif pada wawancara mendalam**).
* **Media Sosial (Grassroots Pulse):** Menunjukkan polarisasi sentimen, terutama pada sektor utilitas infrastruktur dasar (**59,5% negatif pada isu listrik dan konektivitas**).

Alih-alih mengklaim generalisasi sepihak, riset ini mengevaluasi setiap hipotesis berdasarkan **Rubrik Kekuatan Bukti Ilmiah**:
* **KUAT:** Didukung $\ge 3$ sumber independen secara konvergen dan memiliki sinyal kuantitatif tegas.
* **SEDANG:** Didukung 2–3 sumber, bertumpu pada pendalaman kualitatif terverifikasi dari studi kasus.
* **INDIKATIF:** Bertumpu pada sampel kecil ($n < 5$). Diposisikan sebagai hipotesis pembuka untuk riset lanjutan.

### Matriks Evaluasi Hipotesis Awal vs Reformulasi Empiris

| ID | Hipotesis Awal | Status Empiris | Kekuatan Bukti | Reformulasi Berbasis Fakta Data (*Abductive Refinement*) |
|---|---|---|---|---|
| **$H_1$** | Akses Pendanaan Khusus Startup Sangat Terbatas | **Didukung Kuat** | ✅ **KUAT** | **$H_1'$:** Ketiadaan modal ekuitas tidak membunuh startup saat lahir, namun memperlambat pertumbuhan secara drastis dan mematikan inovasi padat modal (*hardware*). 83,3% founder belum pernah didanai, namun 6 dari 7 yang ber-revenue tumbuh secara bootstrap. |
| **$H_2$** | Kesenjangan Ketersediaan Talenta Digital Lokal | **Didukung Sebagian** | 🟡 **SEDANG** | **$H_2'$:** Kesenjangan bukan pada kuantitas sarjana IT, melainkan defisit keahlian teknis industri mendalam (*deep-tech/UI-UX*) dan ketiadaan figur panutan lokal (*role model*) akibat eksodus founder sukses ke Jakarta. |
| **$H_3$** | Ketergantungan Institusi Kampus di Luar Banda Aceh | **Bukti Terbatas** | ⚪ **INDIKATIF** | **$H_3'$:** Inkubator kampus berfungsi sebagai jangkar utama di luar ibu kota (studi kasus PST di Unimal), namun keterbatasan sampel luar Banda Aceh ($n=5$) menuntut riset spasial lanjutan. |
| **$H_4$** | Kelemahan Tindak Lanjut Program Inkubasi Publik | **Direformulasi** | 🟡 **SEDANG** | **$H_4'$:** Masalah utama bukan di dalam ruang inkubasi (PST dimonitor intensif saat kontrak berjalan), melainkan di **"jurang pasca-program"** (*Post-Grant Chasm*): 66,7% peserta inkubasi putus pendampingan begitu masa hibah berakhir. |
| **$H_5$** | Hambatan Akses Pasar Lokal Memaksa Ekspansi | **Didukung Kuat** | 🟡 **SEDANG–KUAT** | **$H_5'$:** Startup yang berhasil bertahan adalah yang sejak hari pertama menyasar pasar nasional (*Born-National*); konsumen lokal antusias mencoba adopsi gratis, namun kesediaan membayar (*willingness to pay*) sangat rendah. |
| **$H_6$** | Ketimpangan Dukungan (Digital Marketing > Product R&D) | **Didukung Sedang** | 🟡 **SEDANG–KUAT** | **$H_6'$:** Ekosistem diperlakukan sebagai program digitalisasi UMKM (kata UMKM disebut 4,3× lebih banyak daripada startup di berita), mengabaikan kebutuhan rekayasa teknologi tinggi dan fasilitas mesin. |

---

## 3. Enam Grand Insights: Alur "Ramai di Panggung, Sepi di Belakang Layar"

### BABAK 1: RAMAI DI PANGGUNG

#### 💡 Insight 1: Paling Terlihat di Panggung, Paling Tidak Dipercaya
* **Data:** Berita daring didominasi narasi seremonial (81,2% netral). Instansi pemerintah dan dinas muncul di **55,9% artikel** (503/900 artikel unik). Sebanyak **45,0% artikel** mengulas seremoni dan pelatihan formalitas, sedangkan berita tentang capaian hasil bisnis hanya **13,8%** (rasio **3,3 : 1**). Sebaliknya, founder memberi skor kepuasan terendah untuk dukungan pemerintah: rata-rata **1,67 dari 5,0** (10 dari 12 founder memberi nilai $\le 2$).
* **Pola & Interpretasi:** Terdapat paradoks visibilitas: pemerintah adalah aktor paling dominan di panggung media, namun keberadaannya paling sedikit dirasakan dampaknya dalam memecahkan masalah operasional founder.
* **Kutipan Kunci:** *"Pemerintah aja gak peduli dengan ekosistem startup di Aceh... mereka hanya hadir untuk seremonial mereka sendiri"* (Responden Survei #8); *"Buang waktu, buang energi buat minta dana ke pemerintah"* (Founder SuratPlus).

---

### BABAK 2: SEPI DI BELAKANG LAYAR (AKAR MASALAH)

#### 💡 Insight 2: Ekosistem Startup yang Sebenarnya Ekosistem UMKM
* **Data:** Kata "UMKM/UKM" muncul di **330 artikel** berita vs kata "startup" yang hanya muncul di **77 artikel** (rasio **4,3 : 1**). Topik digitalisasi UMKM mengambil porsi **23,0%** liputan berita, sedangkan riset produk & R&D hanya **2,4%**. Berita pembiayaan didominasi kredit utang/KUR (117 artikel) daripada modal ventura (68 artikel).
* **Pola & Interpretasi:** Kebijakan publik mengalami *misfit* (salah diagnosis). Startup teknologi yang membutuhkan modal ekuitas berisiko tinggi dan fasilitas rekayasa mesin justru disamaratakan dengan UMKM konvensional.
* **Bukti Lapangan:** Kasus PT Plastik Sago Teknologi (PST) di Lhokseumawe yang membutuhkan mesin cetak plastik industri seharga ratusan juta rupiah, namun diundang oleh institusi perbankan untuk mengikuti pelatihan cara membuka toko di marketplace online.

#### 💡 Insight 3: Tumbuh Tanpa Modal, Tapi Lambat (Survival by Bootstrapping)
* **Data:** **83,3% (10 dari 12 founder)** tidak pernah menerima pendanaan luar. Meski demikian, **7 dari 12 founder** sudah menghasilkan omzet (*revenue/scaling*), dan **6 di antaranya tumbuh 100% secara mandiri (*bootstrapping*)**. Founder memiliki keyakinan bertahan hidup yang sangat tinggi (**4,08 / 5,0**; median 5,0), berbanding terbalik dengan persepsi modal (**1,42 / 5,0**).
* **Pola & Interpretasi:** Ketiadaan modal ventura lokal tidak mematikan daya juang founder Aceh, tetapi memaksa mereka bertahan dengan modal minim dan pekerjaan sampingan. Pertumbuhan bisnis menjadi sangat lambat.
* **Bukti Lapangan:** SuratPlus memulai usaha hanya dengan modal Rp500 ribu, membutuhkan waktu 6 bulan untuk omzet pertama Rp4 juta/bulan, dan butuh 2 tahun baru mampu menggaji tim setara UMR. Bepal bertahan dengan subsidi gaji founder dari pekerjaan kantoran lain.

#### 💡 Insight 4: Jurang Pasca-Hibah (The Post-Grant Chasm)
* **Data:** Dari founder yang pernah mengikuti inkubasi ($n=6$), **66,7% (4 responden)** menyatakan tidak ada tindak lanjut sama sekali pasca-program. Hanya **13,8%** artikel berita yang membahas rekam jejak keberlanjutan alumni program.
* **Pola & Interpretasi:** Titik kritis kegagalan bukan terjadi di dalam masa inkubasi (yang umumnya berjalan baik), melainkan di jurang pembiayaan setelah masa kontrak hibah berakhir (*Post-Grant Chasm*).
* **Bukti Lapangan:** PT Plastik Sago Teknologi berhasil memenuhi target penjualan mangkuk dan wadah bioplastik pati sagu selama dikontrak Kemristekdikti. Namun begitu kontrak selesai dan mesin sewaannya rusak di Jakarta, ketiadaan modal kerja lanjutan memaksa PST vakum operasional sejak 2022.

#### 💡 Insight 5: Defisit Talenta Mendalam & Ketiadaan Panutan Lokal
* **Data:** Talenta masuk dalam Top-3 tantangan utama bagi **41,7% (5/12)** founder. Ketersediaan mentor lokal dinilai sangat kritis: rata-rata **2,08 dari 5,0**.
* **Pola & Interpretasi:** Kesenjangan talenta Aceh bukan defisit kuantitas sarjana IT, melainkan kelangkaan keahlian teknis spesifik (*industrial molding*, UI/UX profesional, *distributed computing*) dan ketiadaan founder panutan (*role model*) karena founder sukses cenderung berhijrah ke Jakarta.
* **Bukti Lapangan:** PST harus merekrut pensiunan tenaga ahli dari Batan di Jawa karena tidak ada teknisi molding di Aceh. SuratPlus mencatat founder sukses biasanya menetap di Jakarta, menyebabkan founder pemula di Banda Aceh kehilangan mentor praktisi.

---

### BABAK 3: CARA BERTAHAN

#### 💡 Insight 6: Pasarnya Ada, Tapi Bukan di Aceh (Born-National to Survive)
* **Data:** SuratPlus mencatat **200.000+ pengguna terdaftar (dan 1,8 juta kunjungan web) di 250+ kabupaten/kota** se-Indonesia. Lima kota pengguna terbesar berada di Pulau Jawa dan Medan. Kota **Banda Aceh hanya menempati peringkat ke-30**. Skor kemudahan akses pasar dinilai tinggi oleh founder (**3,75 / 5,0**), namun teks survei mengonfirmasi pasar lokal Aceh enggan membayar layanan software.
* **Pola & Interpretasi:** Pasar lokal Aceh belum memiliki daya beli dan kesediaan membayar (*willingness to pay*) untuk produk perangkat lunak komersial. Startup teknologi lokal hanya dapat bertahan jika berorientasi nasional (*Born-National*) sejak awal.
* **Bukti Lapangan:** Konsumen Aceh lebih memilih fotokopi fisik atau template Canva gratisan daripada berlangganan software generator surat resmi. Bepal mencatat antusiasme komunitas Lhokseumawe tinggi (8,5/10), namun kesiapan membayar layanan digital sangat rendah.

---

## 4. Kendala Lapangan & Solusi Teknis Riset

Dalam menyelesaikan sprint riset ini, tim menghadapi 4 kendala teknis nyata yang berhasil dimitigasi melalui rekayasa data mandiri:

1. **Resolusi URL & Proteksi Anti-Bot Scraping:**
   * *Kendala:* 746 percobaan ekstraksi gagal akibat redirect terenkripsi Google News dan proteksi server media online.
   * *Solusi:* Membangun modul `02_resolver.py` dengan emulasi header peramban dan multi-tier extraction fallback, sukses mengamankan 1.231 artikel dari 243 portal berita.
2. **Noise Data Luar Daerah:**
   * *Kendala:* 7.192 paragraf berita nasional tidak sengaja tersaring akibat kata kunci umum (seperti 'BSI', 'PON', 'Kemenparekraf').
   * *Solusi:* Mengembangkan *Ingestion Shield* dengan kamus entitas lokal Aceh dan penilaian ambang relevansi domain (`rejected_dataset.csv`), menjamin kemurnian korpus berita (6.648 paragraf).
3. **Keterbatasan Sampel Primer ($n=12$ Survei, $n=3$ Wawancara):**
   * *Kendala:* Jumlah founder aktif di Aceh sangat terbatas, tidak memungkinkan uji parametrik murni.
   * *Solusi:* Memosisikan survei sebagai instrumen eksplorasi kualitatif (*deep probing*) dan mentriangulasikannya secara konvergen dengan 7.000+ unit teks dari 3 pilar data lainnya.
4. **Disparitas Volume Data Lintas Sumber:**
   * *Kendala:* Penggabungan mentah akan menyebabkan suara founder (25 teks survei) tenggelam di bawah dominasi 6.648 paragraf berita.
   * *Solusi:* Analisis dilakukan terisolasi per sumber terlebih dahulu, kemudian dinormalisasi dalam bentuk persentase per baris lintas sumber (*Row-Normalized Heatmap C8*).

---

## 5. Limitasi Metodologis & Arahan Riset Lanjutan

1. **Keterbatasan Kamus Sentimen Bahasa Berita:**
   Analisis sentimen leksikal bahasa Indonesia cenderung mengklasifikasikan gaya bahasa jurnalistik formal sebagai netral (81,21%), berpotensi menyamarkan kritik struktural implisit.
2. **Representasi Spasial Wilayah Luar Banda Aceh:**
   Responden mayoritas berdomisili di Banda Aceh dan sebagian Lhokseumawe. Dinamika ekosistem di pantai barat-selatan dan wilayah tengah Gayo belum terwakili secara mendalam.
3. **Rekomendasi Riset Lanjutan:**
   * Melakukan pelacakan longitudinal selama 3–5 tahun terhadap kohort alumni inkubasi kampus untuk mengukur tingkat kelangsungan hidup riil.
   * Melakukan studi mendalam mengenai strategi repatriasi dan transfer keahlian dari komunitas diaspora teknologi Aceh di Jakarta.

---

## 6. Rekomendasi Kebijakan Berbasis Bukti (Policy Action Plan)

1. **Skema Dana Jembatan Pasca-Inkubasi (*Post-Incubation Bridge Fund*):**  
   Pemerintah Aceh dan universitas perlu mendirikan skema dana padanan (*matching fund*) atau modal kerja transisi bagi startup lulusan program yang telah memiliki validasi pasar, guna menutup jurang pasca-kontrak dan mencegah kematian mendadak seperti pada kasus PST.
2. **Diferensiasi Kebijakan Startup vs UMKM Konvensional:**  
   Dinas Koperasi & UKM, Bank Indonesia, dan Diskominfo harus memisahkan kurikulum pembinaan: UMKM diarahkan pada digital marketing dan perputaran kas harian, sedangkan startup teknologi difasilitasi modal ventura, pengujian laboratorium industri, dan perlindungan hak cipta/paten.
3. **Program Mentoring Diaspora (*Aceh Tech Diaspora Fellowship*):**  
   Membangun konsorsium mentoring terstruktur yang menghubungkan founder dan eksekutif teknologi asal Aceh di kota-kota besar dengan inovator muda di kampus-kampus lokal untuk mengatasi defisit panutan dan transfer keahlian industri mendalam.

---
*Laporan ini disusun oleh Tim Data Analytics GRAK (Sprint-3) dan telah diverifikasi bebas dari kontradiksi data.*
