# Catatan Hasil Sprint 3: Ekosistem Startup Aceh

Rangkuman santai dan padat tentang apa yang udah kita selesaikan di Sprint 3, kondisi dataset, hasil model ML, dan bahan buat ngobrol ke leader.

---

## 1. File yang Ada di Folder Ini

- **`dataset_aceh_sprint3.xlsx`**: File Excel utama. Teksnya udah dirapikan, bebas noise (0% bot, spam, atau teks luar topik), ada pewarnaan sentimen, autofilter, dan tab ringkasan pilar.
- **`dataset_aceh_sprint3.csv`**: Versi CSV bersih buat kebutuhan olah data teknis / koding.
- **`slides.html`**: Slide web ringkas gelap (Vercel style). Tinggal double click, langsung jalan di browser buat nunjukin poin-poin hasil riset tanpa perlu setup apa-apa.
- **`5_insight_utama.md`**: Detail 5 temuan utama dari data pengguna beserta baris bukti sitasinya.

---

## 2. Status Data & Machine Learning

- **Total Data Bersih**: 311 postingan murni ekosistem Aceh (Twitter: 239, LinkedIn + OCR: 36, YouTube: 36).
- **Distribusi 7 Pilar Seimbang**: Rata ~44-45 per pilar (Teknologi, Kampus, Funding, Market, Program, Talent, Infrastruktur).
- **Akurasi Model**:
  - Klasifikasi Topik: **85.71%** (Holdout) dan **81.33%** (5-Fold CV).
  - False Positive Rate rata-rata rendah: **2.38%** (bahkan 0% di pilar infrastruktur & kampus).
- **Filter Anti-Nyasar (Ingestion Shield)**: Teks di luar dunia teknologi (razia pedagang, lowongan sawit, turnamen futsal) otomatis ditolak dan gak bakal salah masuk ke kategori startup.

---

## 3. 5 Poin Penting Buat Dibawa ke Leader

Kalau mau sharing atau presentasi ke leader, fokus ke 5 hal ini aja:

1. **Jebakan Pemburu Hibah**: Startup lokal kebanyakan hidup dari lomba/hibah tahunan karena belum ada investor malaikat (angel network) lokal. Begitu hadiah habis, operasional mandek.
2. **Talenta Senior Menghilang ke Remote Work**: Lulusan teknik di Aceh banyak, tapi yang level mid-to-senior milih kerja WFH ke Jakarta/luar negeri karena standar gajinya 3x lipat UMR lokal. Startup lokal susah rekrut tech lead.
3. **Kampus Jadi Tumpuan Utama di Luar Banda Aceh**: Di Lhokseumawe atau Meulaboh gak ada coworking space swasta. Dosen dan lab kampus (PNL, Unimal, UTU) jadi satu-satunya pusat inovasi digital.
4. **Masalah Listrik & Internet di Pesisir/Barsela**: Seringnya mati lampu dan internet putus di Barat-Selatan bikin pekerja tech tekor di genset dan kuota cadangan. Kalau bikin aplikasi lokal, wajib arsitektur *offline-first*.
5. **Peluang Riil Ada di B2B Komoditas**: Model B2C konsumtif mentok di daya beli. Tapi startup yang garap rantai pasok kopi Gayo atau minyak nilam (ARC USK) justru punya potensi pasar nyata.

---

## 4. Rencana Langkah ke Sprint 4

- Bikin prototipe sistem yang ramah koneksi minim (*offline-first* PWA).
- Validasi sistem ketertelusuran (*traceability*) untuk komoditas kopi Gayo/nilam.
- Wacanakan wadah investor diaspora (*angel syndicate*) bareng pengusaha Aceh di perantauan.
