#!/usr/bin/env python3
"""
15_build_deck.py
----------------
Menghasilkan slide deck presentasi eksekutif untuk mentor (HTML interaktif + Print to PDF).
Output:
- data/processed/storytelling/deck/index.html

Fitur Deck:
1. Navigasi Keyboard: Panah Kiri / Kanan, Spacebar, atau Tombol Toolbar.
2. Fullscreen mode (Tombol 'F' atau ikon layar penuh).
3. Speaker Notes (Tombol 'N' atau tombol Notes) berisi narasi bicara, poin penekanan, dan antisipasi tanya-jawab mentor.
4. Plotly.js charts interaktif di-embed langsung dengan tooltip, zoom, dan hover effects.
5. CSS @media print teroptimasi: Ctrl+P / Cmd+P langsung mengekspor 1 slide per halaman PDF tanpa terpotong.
6. Design system GRAK: Clean executive theme, aksen oranye-merah (#E4572E), navy (#1F2A44), card glassmorphism halus.
"""

import os
import json
import base64
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def build_presentation_deck():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    story_dir = os.path.join(base_dir, 'data', 'processed', 'storytelling')
    deck_dir = os.path.join(story_dir, 'deck')
    os.makedirs(deck_dir, exist_ok=True)

    json_path = os.path.join(story_dir, 'verified_metrics.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    c1_png_path = os.path.join(story_dir, 'charts_png', 'c1_funnel_pipeline_16_9.png')
    c8_png_path = os.path.join(story_dir, 'charts_png', 'c8_topic_heatmap_16_9.png')
    c1_b64 = "data:image/png;base64," + base64.b64encode(open(c1_png_path, 'rb').read()).decode('utf-8') if os.path.exists(c1_png_path) else "../charts_png/c1_funnel_pipeline_16_9.png"
    c8_b64 = "data:image/png;base64," + base64.b64encode(open(c8_png_path, 'rb').read()).decode('utf-8') if os.path.exists(c8_png_path) else "../charts_png/c8_topic_heatmap_16_9.png"

    # 1. BUILD PLOTLY CHARTS AS HTML STRINGS
    print("Generating interactive Plotly figures...")
    
    # Chart C2: Kontras Sentimen Negatif
    c2_sources = ['Berita Media (N=6.648)', 'Media Sosial (N=311)', 'Wawancara (N=113)', 'Survei Founder (N=25)']
    c2_pcts = [
        metrics['sentiment_by_source']['news']['pct']['negative'],
        metrics['sentiment_by_source']['social_media']['pct']['negative'],
        metrics['sentiment_by_source']['interview']['pct']['negative'],
        metrics['sentiment_by_source']['survey']['pct']['negative']
    ]
    c2_colors = ['#9AA5B1', '#9AA5B1', '#E4572E', '#E4572E']
    
    fig_c2 = go.Figure(go.Bar(
        x=c2_pcts,
        y=c2_sources,
        orientation='h',
        marker=dict(color=c2_colors, line=dict(width=0)),
        text=[f"<b>{p:.1f}%</b>" for p in c2_pcts],
        textposition='outside',
        textfont=dict(family='Inter, sans-serif', size=13, color='#1F2A44')
    ))
    fig_c2.update_layout(
        title=dict(
            text="<b>Persentase Sentimen Negatif / Kritis per Sumber Data</b>",
            font=dict(size=16, color='#1F2A44', family='Inter, sans-serif')
        ),
        xaxis=dict(
            title="Persentase Negatif (%)",
            range=[0, 78],
            gridcolor='#E2E8F0',
            zerolinecolor='#CBD5E1'
        ),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=50, b=40),
        height=320
    )
    c2_html = fig_c2.to_html(include_plotlyjs=False, full_html=False, div_id="plotly_c2_chart")

    # Chart C3: Likert Dot Plot
    likert_data = metrics['survey_metrics']['likert_metrics']
    sorted_likert = sorted(likert_data.items(), key=lambda x: x[1]['mean'])
    c3_labels = [v['label'] for k, v in sorted_likert]
    c3_means = [v['mean'] for k, v in sorted_likert]
    c3_colors = ['#E4572E' if m < 2.5 else ('#9AA5B1' if m < 3.5 else '#2E7D32') for m in c3_means]
    
    fig_c3 = go.Figure()
    # Baseline 3.0
    fig_c3.add_vline(x=3.0, line_dash="dash", line_color="#94A3B8", annotation_text="Ambang Netral (3,0)", annotation_position="top right")
    fig_c3.add_trace(go.Scatter(
        x=c3_means,
        y=c3_labels,
        mode='markers+text',
        marker=dict(size=14, color=c3_colors, line=dict(width=1.5, color='#FFFFFF')),
        text=[f"<b>{m:.2f}</b>" for m in c3_means],
        textposition='middle right',
        textfont=dict(size=12, color='#1F2A44', family='Inter, sans-serif'),
        hoverinfo='x+y'
    ))
    fig_c3.update_layout(
        title=dict(
            text="<b>Rata-rata Skor Persepsi Founder Aceh (Skala Likert 1–5, n=12)</b>",
            font=dict(size=16, color='#1F2A44', family='Inter, sans-serif')
        ),
        xaxis=dict(
            title="Skor Likert (1=Sangat Rendah, 5=Sangat Tinggi)",
            range=[1.0, 5.0],
            gridcolor='#E2E8F0',
            dtick=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=50, b=40),
        height=350
    )
    c3_html = fig_c3.to_html(include_plotlyjs=False, full_html=False, div_id="plotly_c3_chart")

    # Chart C4: Top Tantangan Founder
    c4_items = sorted(metrics['survey_metrics']['challenges']['top3_overall'].items(), key=lambda x: x[1], reverse=True)[:6]
    c4_labels = [item[0] for item in c4_items]
    c4_counts = [item[1] for item in c4_items]
    c4_colors = ['#E4572E' if i == 0 else '#9AA5B1' for i in range(len(c4_items))]
    
    fig_c4 = go.Figure(go.Bar(
        x=c4_counts,
        y=c4_labels,
        orientation='h',
        marker=dict(color=c4_colors),
        text=[f"<b>{c} founder ({c/12*100:.1f}%)</b>" for c in c4_counts],
        textposition='outside',
        textfont=dict(family='Inter, sans-serif', size=12, color='#1F2A44')
    ))
    fig_c4.update_layout(
        title=dict(
            text="<b>Frekuensi Sebutan dalam Top-3 Tantangan Founder (n=12)</b>",
            font=dict(size=16, color='#1F2A44', family='Inter, sans-serif')
        ),
        xaxis=dict(title="Jumlah Responden yang Menyebut", range=[0, 8], gridcolor='#E2E8F0'),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=50, b=40),
        height=320
    )
    c4_html = fig_c4.to_html(include_plotlyjs=False, full_html=False, div_id="plotly_c4_chart")

    # Chart C7: Topik Berita Framing
    c7_topics = [
        ("Digitalisasi UMKM", 23.0, '#E4572E'),
        ("Pendanaan (KUR/Kredit)", 15.3, '#9AA5B1'),
        ("Talenta (Literasi)", 14.9, '#9AA5B1'),
        ("Regulasi & Pemda", 10.9, '#9AA5B1'),
        ("Akses Pasar", 9.5, '#9AA5B1'),
        ("Ekosistem & Lomba", 6.5, '#9AA5B1'),
        ("Kisah Sukses", 5.3, '#9AA5B1'),
        ("Infrastruktur & R&D", 2.4, '#E4572E')
    ]
    fig_c7 = go.Figure(go.Bar(
        x=[t[1] for t in c7_topics],
        y=[t[0] for t in c7_topics],
        orientation='h',
        marker=dict(color=[t[2] for t in c7_topics]),
        text=[f"<b>{t[1]:.1f}%</b>" for t in c7_topics],
        textposition='outside',
        textfont=dict(family='Inter, sans-serif', size=12, color='#1F2A44')
    ))
    fig_c7.update_layout(
        title=dict(
            text="<b>Porsi Liputan Media Online per Topik (N=6.648 Paragraf)</b>",
            font=dict(size=16, color='#1F2A44', family='Inter, sans-serif')
        ),
        xaxis=dict(title="Persentase Paragraf (%)", range=[0, 28], gridcolor='#E2E8F0'),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=50, b=40),
        height=350
    )
    c7_html = fig_c7.to_html(include_plotlyjs=False, full_html=False, div_id="plotly_c7_chart")

    # 2. ASSEMBLE SLIDES DATA
    slides = [
        # SLIDE 1: Cover
        {
            "id": 1,
            "badge": "LAPORAN RISET EKSEKUTIF",
            "title": "Analisis Ekosistem Startup Aceh 2026",
            "subtitle": "Ramai di Panggung, Sepi di Belakang Layar: Studi Triangulasi Multi-Metode tentang Realitas Akses Modal, Talenta, dan Kelangsungan Usaha",
            "speaker_notes": "Selamat pagi Bapak/Ibu mentor dan dewan penguji. Hari ini saya mempresentasikan riset komprehensif ekosistem startup Aceh 2026. Riset ini lahir dari satu premis besar: media massa memberitakan Aceh sedang giat bertransformasi digital, namun apa yang sebenarnya dialami para founder di lapangan? Kami menggabungkan 4 pilar data: 6.600+ paragraf berita, percakapan sosmed, survei founder, dan wawancara mendalam untuk menguji realitas ini secara jujur dan berbasis data.",
            "content": """
            <div class="hero-box">
                <div class="hero-stats-row">
                    <div class="stat-pill"><span class="num">7.097</span> Unit Teks Triangulasi</div>
                    <div class="stat-pill"><span class="num">900</span> Artikel Berita Unik</div>
                    <div class="stat-pill"><span class="num">243</span> Media Online</div>
                    <div class="stat-pill"><span class="num">12</span> Founder Startup Aceh</div>
                    <div class="stat-pill"><span class="num">3</span> Studi Kasus Mendalam</div>
                </div>
                <div class="hero-quote">
                    "Ekosistem startup Aceh ramai di panggung media, tetapi para founder berjuang sendirian di belakang layar: bertumbuh secara mandiri tanpa modal luar, menghadapi defisit talenta mendalam, dan terpaksa membidik pasar nasional karena pasar lokal belum siap membayar."
                </div>
                <div class="meta-footer">
                    <span><b>Penyusun:</b> Tim Riset Data GRAK (Sprint-3)</span>
                    <span><b>Metodologi:</b> Convergent Mixed-Methods Triangulation</span>
                    <span><b>Periode Analisis:</b> 2022–2026</span>
                </div>
            </div>
            """
        },

        # SLIDE 2: Executive Hook
        {
            "id": 2,
            "badge": "EKSEKUTIF SUMMARY & HOOK",
            "title": "Dua Dunia yang Bertolak Belakang",
            "subtitle": "Kesenjangan radikal antara citra keberhasilan di ruang publik vs perjuangan sepi para founder",
            "speaker_notes": "Slide ini adalah 'hook' cerita kita. Perhatikan dua angka yang sangat kontras di sini: di media massa, sentimen negatif nyaris tidak ada—hanya 0,5% dari 6.648 paragraf berita. Berita dipenuhi seremonial, MoU, dan festival. Tapi begitu kita menyodorkan survei teks dan wawancara langsung ke para founder, sentimen negatif melonjak hingga 64%. Ada jurang komunikasi yang lebar: panggungnya riuh oleh klaim keberhasilan, tetapi di balik layar, pelaku usaha merasa dibiarkan berjuang sendiri.",
            "content": f"""
            <div class="grid-2col">
                <div class="card card-accent-left">
                    <div class="card-tag">PANGGUNG PUBLIK (BERITA MEDIA)</div>
                    <div class="big-metric">81,2% <span class="unit">Netral / Seremoni</span></div>
                    <p class="card-desc">Dari <b>900 artikel berita unik</b> (6.648 paragraf), hanya <b>0,5%</b> yang memuat sentimen kritis. 45% liputan adalah seremoni peluncuran, pelatihan seremonial, dan MoU dinas.</p>
                    <div class="metric-bullet">
                        <span class="dot red"></span> Rasio liputan seremoni dibanding capaian hasil bisnis nyata adalah <b>3,3 : 1</b>
                    </div>
                </div>
                <div class="card card-accent-left active">
                    <div class="card-tag highlight">REALITAS LAPANGAN (SUARA FOUNDER)</div>
                    <div class="big-metric red">64,0% <span class="unit">Sentimen Frustrasi / Kritis</span></div>
                    <p class="card-desc">Dari teks survei dan wawancara mendalam para founder aktif, mayoritas menyuarakan keputusasaan terhadap ketiadaan infrastruktur pendukung dan komitmen nyata.</p>
                    <div class="metric-bullet">
                        <span class="dot red"></span> Skor kepercayaan founder terhadap dukungan pemerintah: <b>1,67 dari 5,0</b>
                    </div>
                </div>
            </div>
            <div class="mt-4">
                {c2_html}
            </div>
            """
        },

        # SLIDE 3: Hipotesis Awal & Pertanyaan Riset
        {
            "id": 3,
            "badge": "LANDASAN RISET",
            "title": "Pertanyaan Riset & 6 Hipotesis Awal",
            "subtitle": "Merumuskan kerangka uji empiris terhadap 6 asumsi umum ekosistem startup daerah",
            "speaker_notes": "Sebelum turun ke data, kami merumuskan 6 hipotesis awal H1 sampai H6 yang mencakup akses pendanaan, talenta, peran kampus luar daerah, efektivitas seremoni, daya serap pasar lokal, dan fokus program pemerintah. Kami tidak akan melakukan manipulasi hipotesis pasca-analisis (HARKing). Keenam hipotesis ini kami uji apa adanya, lalu kami lihat bagaimana data memaksa kita mempertajamnya.",
            "content": """
            <div class="grid-3col">
                <div class="hypo-card"><div class="hypo-id">H1</div><h4>Akses Modal Terbatas</h4><p>Startup Aceh kesulitan mengakses modal ventura & pendanaan ekuitas institusional.</p></div>
                <div class="hypo-card"><div class="hypo-id">H2</div><h4>Kesenjangan Talenta</h4><p>Sulit merekrut talenta teknis berkualitas karena kalah saing dengan peluang kerja remote.</p></div>
                <div class="hypo-card"><div class="hypo-id">H3</div><h4>Ketergantungan Kampus</h4><p>Inovator di luar Banda Aceh sangat bersandar pada inkubator universitas lokal.</p></div>
                <div class="hypo-card"><div class="hypo-id">H4</div><h4>Program Formalitas</h4><p>Dukungan pemerintah berhenti di seremoni & kompetisi tanpa tindak lanjut pembinaan komersial.</p></div>
                <div class="hypo-card"><div class="hypo-id">H5</div><h4>Pasar Lokal Lemah</h4><p>Daya beli dan kesiapan adopsi digital pasar Aceh rendah, memaksa ekspansi luar daerah.</p></div>
                <div class="hypo-card"><div class="hypo-id">H6</div><h4>Orientasi UMKM > R&D</h4><p>Bantuan didominasi pelatihan marketing instan daripada riset produk mendalam.</p></div>
            </div>
            <div class="callout-box mt-4">
                <b>Komitmen Integritas:</b> Setiap hipotesis dievaluasi dengan <i>rubrik kekuatan bukti</i> (Kuat / Sedang / Indikatif), bukan dengan klaim sepihak.
            </div>
            """
        },

        # SLIDE 4: Metodologi 1 - Desain Riset Triangulasi
        {
            "id": 4,
            "badge": "METODOLOGI [1/3]",
            "title": "Desain Riset: Triangulasi Konvergen 4 Pilar",
            "subtitle": "Mengintegrasikan perspektif makro institusional hingga pengalaman mikro founder",
            "speaker_notes": "Untuk menjawab pertanyaan riset secara utuh, kami memakai desain Convergent Mixed-Methods Triangulation. Kita memiliki 4 pilar data yang independen: Pilar Makro dari berita media online untuk memotret narasi kebijakan; Pilar Grassroots dari media sosial (X, LinkedIn, YouTube) untuk menangkap keluhan publik; Pilar Kualitatif dari wawancara mendalam 3 institusi startup; dan Pilar Mikro dari survei terstruktur founder. Keempat pilar ini saling mengoreksi dan memvalidasi.",
            "content": """
            <div class="grid-2col">
                <div class="card pilar-card">
                    <div class="pilar-header">
                        <span class="pilar-icon">📰</span>
                        <div><h4>Pilar 1: Makro Institusional (Berita Online)</h4><span class="sub">N = 6.648 paragraf | 900 artikel | 243 media</span></div>
                    </div>
                    <p>Memetakan agenda kebijakan pemerintah, fokus program dinas, dan narasi publik yang dipublikasikan media daring sejak 2022 hingga 2026.</p>
                </div>
                <div class="card pilar-card">
                    <div class="pilar-header">
                        <span class="pilar-icon">💬</span>
                        <div><h4>Pilar 2: Grassroots Komunitas (Media Sosial)</h4><span class="sub">N = 311 unit percakapan (X, LinkedIn, YouTube)</span></div>
                    </div>
                    <p>Menangkap sentimen organik talenta digital, keluhan infrastruktur listrik/internet, dan percakapan karir teknologi di Aceh.</p>
                </div>
                <div class="card pilar-card">
                    <div class="pilar-header">
                        <span class="pilar-icon">🎙️</span>
                        <div><h4>Pilar 3: Kualitatif Mendalam (Wawancara)</h4><span class="sub">N = 113 unit teks | 3 Studi Kasus Startup</span></div>
                    </div>
                    <p>Transkrip wawancara terstruktur dengan founder SuratPlus (SaaS nasional), PT Plastik Sago Teknologi (Bioplastik/Hardware), dan Bepal.</p>
                </div>
                <div class="card pilar-card">
                    <div class="pilar-header">
                        <span class="pilar-icon">📊</span>
                        <div><h4>Pilar 4: Mikro Empiris (Survei Founder)</h4><span class="sub">N = 12 Founder Terverifikasi (25 kutipan teks)</span></div>
                    </div>
                    <p>Instrumen survei 26 variabel Likert & isian bebas mengukur status traksi bisnis, permodalan, akses talenta, dan kepuasan pendampingan.</p>
                </div>
            </div>
            """
        },

        # SLIDE 5: Metodologi 2 - Pipeline & Data Funnel
        {
            "id": 5,
            "badge": "METODOLOGI [2/3]",
            "title": "Pipeline Data: Dari 1.350 Berita ke 7.097 Unit",
            "subtitle": "Standar pembersihan data bertingkat menjamin tidak ada noise data luar daerah",
            "speaker_notes": "Dewan penguji sering bertanya: bagaimana kalian memastikan artikel berita benar-benar membahas startup Aceh dan bukan berita nasional yang nyasar? Di slide ini terlihat data funnel kami. Dari 1.350 artikel discovery, kami me-resolve URL dengan menangani 746 kegagalan akibat proteksi anti-bot. Setelah ekstraksi 14.818 paragraf, kami membangun 'Ingestion Shield' berbasis regex entitas Aceh dan confidence scoring. Hasilnya, 7.192 paragraf out-of-domain dibuang. Hanya 6.648 paragraf berita yang 100% valid masuk ke tahap triangulasi bersama data primer.",
            "content": f"""
            <div class="grid-2col">
                <div>
                    <img src="{c1_b64}" class="slide-img" alt="Funnel Pipeline">
                </div>
                <div class="card">
                    <h4 class="mb-3">Tahapan Pembersihan & Kontrol Kualitas</h4>
                    <ul class="clean-list">
                        <li><b>URL Resolver (02_resolver.py):</b> Menangani redirect Google News dan link rusak dari 243 portal berita.</li>
                        <li><b>Ingestion Shield (03_cleaning.py):</b> Membuang 51,9% paragraf noise (berita nasional tanpa relevansi lokal Aceh).</li>
                        <li><b>Deduplikasi Teks:</b> Penghapusan duplikat eksak & <i>near-duplicate boilerplate</i> (footer berita, copyright media).</li>
                        <li><b>Auto-Labeling Rules (05_labeling.py):</b> 94,1% paragraf terlabel otomatis secara deterministik; 815 baris <i>needs_review</i> diaudit manual.</li>
                    </ul>
                    <div class="badge-row mt-3">
                        <span class="badge green">Kualitas Data Terverifikasi</span>
                        <span class="badge blue">Anti-Noise Shield Aktif</span>
                    </div>
                </div>
            </div>
            """
        },

        # SLIDE 6: Metodologi 3 - Kerangka Analisis & Rubrik Bukti
        {
            "id": 6,
            "badge": "METODOLOGI [3/3]",
            "title": "Dari Data Mentah Menuju Insight yang Kokoh",
            "subtitle": "Kerangka analisis 5 lapis dan rubrik kekuatan bukti ilmiah",
            "speaker_notes": "Bagaimana data mentah bertransformasi menjadi kesimpulan strategis? Kami menerapkan 5-layer analytical framework: Raw Data dikelompokkan menjadi Pola Statistik, diinterpretasikan melalui Konteks Lokal, disintesis menjadi Insight yang mengejutkan, dan diuji ulang dengan Rubrik Kekuatan Bukti. Kami mengklasifikasikan bukti menjadi Kuat jika didukung minimal 3 sumber independen, Sedang jika didukung 2 sumber kualitatif solid, dan Indikatif jika sampelnya kecil sehingga diposisikan sebagai hipotesis riset lanjutan.",
            "content": """
            <div class="workflow-grid">
                <div class="wf-step">
                    <div class="step-num">L1</div>
                    <h5>DATA</h5>
                    <p>7.097 teks terverifikasi & 12 survei founder</p>
                </div>
                <div class="wf-arrow">→</div>
                <div class="wf-step">
                    <div class="step-num">L2</div>
                    <h5>PATTERN</h5>
                    <p>Distribusi topik, rasio kata, cross-tab permodalan</p>
                </div>
                <div class="wf-arrow">→</div>
                <div class="wf-step">
                    <div class="step-num">L3</div>
                    <h5>CONTEXT</h5>
                    <p>Dinamika lokal: birokrasi, daya beli, modal ventura</p>
                </div>
                <div class="wf-arrow">→</div>
                <div class="wf-step">
                    <div class="step-num">L4</div>
                    <h5>INSIGHT</h5>
                    <p>Temuan counter-intuitive & implikasi bisnis</p>
                </div>
                <div class="wf-arrow">→</div>
                <div class="wf-step highlight">
                    <div class="step-num">L5</div>
                    <h5>EVIDENCE</h5>
                    <p>Rubrik Kuat / Sedang / Indikatif</p>
                </div>
            </div>
            <div class="grid-3col mt-4">
                <div class="card card-sm">
                    <span class="badge green">BUKTI KUAT</span>
                    <p class="mt-2 text-sm">Didukung &ge; 3 sumber independen secara konvergen dan memiliki bukti kuantitatif tegas.</p>
                </div>
                <div class="card card-sm">
                    <span class="badge amber">BUKTI SEDANG</span>
                    <p class="mt-2 text-sm">Didukung 2–3 sumber, didominasi pendalaman kualitatif terverifikasi dari studi kasus.</p>
                </div>
                <div class="card card-sm">
                    <span class="badge gray">BUKTI INDIKATIF</span>
                    <p class="mt-2 text-sm">Bertumpu pada sampel kecil (n &lt; 5). Diposisikan sebagai hipotesis untuk riset lanjutan.</p>
                </div>
            </div>
            """
        },

        # SLIDE 7: BABAK 1 - INSIGHT 1
        {
            "id": 7,
            "badge": "BABAK 1: RAMAI DI PANGGUNG",
            "title": "Insight 1: Paling Terlihat di Panggung, Paling Tidak Dipercaya",
            "subtitle": "Pemerintah mendominasi panggung berita media, tetapi meraih tingkat kepercayaan terendah dari founder",
            "speaker_notes": "Masuk ke Babak 1: Ramai di Panggung. Insight 1 ini memiliki kekuatan bukti KUAT. Pemerintah, kementerian, dan dinas disebut dalam 55,9% artikel berita startup Aceh (503 dari 900 artikel). Rasio berita tentang seremoni/acara peresmian mencapai 45%, sementara berita yang menyinggung hasil nyata omzet atau keberlanjutan bisnis hanya 13,8%—rasio 3,3 banding 1! Namun ketika founder ditanya bagaimana dukungan pemerintah terhadap perkembangan bisnis mereka, rata-rata skornya hanya 1,67 dari 5,0. 10 dari 12 founder memberi skor 1 atau 2. Founder merasa pemerintah hanya hadir untuk berfoto di panggung seremonial.",
            "content": """
            <div class="grid-2col">
                <div class="card">
                    <h4 class="mb-3">Bukti Kuantitatif Media & Survei</h4>
                    <div class="stat-highlight-row">
                        <div class="stat-box">
                            <div class="val">55,9%</div>
                            <div class="lbl">Artikel Berita Menyebut Instansi Pemerintah (503/900)</div>
                        </div>
                        <div class="stat-box">
                            <div class="val red">1,67 / 5</div>
                            <div class="lbl">Persepsi Founder atas Dukungan Pemerintah</div>
                        </div>
                    </div>
                    <div class="stat-highlight-row mt-3">
                        <div class="stat-box">
                            <div class="val">3,3 : 1</div>
                            <div class="lbl">Rasio Berita Seremoni (45%) vs Capaian Hasil (13,8%)</div>
                        </div>
                        <div class="stat-box">
                            <div class="val">10 / 12</div>
                            <div class="lbl">Founder Memberi Skor Kritis (&le; 2) untuk Pemerintah</div>
                        </div>
                    </div>
                </div>
                <div class="card card-accent-left">
                    <h4 class="mb-3">Suara Lapangan Narasumber</h4>
                    <div class="quote-box">
                        <p class="quote-text">"Pemerintah aja gak peduli dengan ekosistem startup di Aceh... mereka hanya hadir untuk seremonial mereka sendiri."</p>
                        <span class="quote-author">— Responden Survei Founder #8</span>
                    </div>
                    <div class="quote-box mt-3">
                        <p class="quote-text">"Buang waktu, buang energi buat minta dana sama pemerintah... mending jalan sendiri."</p>
                        <span class="quote-author">— Founder SuratPlus (200.000+ Pengguna &amp; 1,8 Juta Kunjungan)</span>
                    </div>
                    <div class="quote-box mt-3">
                        <p class="quote-text">"Dukungan dana dari pemerintah daerah Lhokseumawe itu sama sekali gak ada."</p>
                        <span class="quote-author">— Founder PT Plastik Sago Teknologi (PST)</span>
                    </div>
                </div>
            </div>
            <div class="evidence-tag mt-3"><span class="badge green">Kekuatan Bukti: KUAT</span> Triangulasi konvergen: Berita (N=900) + Survei (n=12) + Wawancara 2 Institusi</div>
            """
        },

        # SLIDE 8: BABAK 2 - INSIGHT 2
        {
            "id": 8,
            "badge": "BABAK 2: SEPI DI BELAKANG LAYAR",
            "title": "Insight 2: Ekosistem Startup yang Sebenarnya Ekosistem UMKM",
            "subtitle": "Kebutuhan rekayasa produk teknologi dan modal ventura tenggelam dalam program massal UMKM",
            "speaker_notes": "Memasuki Babak 2: Sepi di Belakang Layar. Mengapa program pemerintah tidak dirasakan founder? Insight 2 menjawab akarnya: Ekosistem startup Aceh sebenarnya diperlakukan sebagai digitalisasi UMKM. Di media, kata 'UMKM/UKM' disebut 330 artikel, sedangkan kata 'startup' hanya 77 artikel—rasio 4,3 kali lipat. Berita pembiayaan didominasi kredit perbankan dan KUR (117 artikel), bukan modal ventura atau angel investor (hanya 68 artikel). Akibatnya fatal: founder startup deep-tech seperti PST diundang oleh Bank Indonesia untuk ikut 'pelatihan jualan di Tokopedia/Shopee', padahal yang mereka butuhkan adalah mesin injection molding plastik seharga ratusan juta rupiah.",
            "content": f"""
            <div class="grid-2col">
                <div>
                    {c7_html}
                </div>
                <div class="card">
                    <h4 class="mb-3">Misfit Program: Salah Diagnosis Kebutuhan</h4>
                    <div class="compare-table">
                        <div class="compare-row header">
                            <span>Kebutuhan Riil Startup</span>
                            <span>Program yang Diberikan</span>
                        </div>
                        <div class="compare-row">
                            <span><b>Modal Ekuitas / R&D</b><br><small>Menyerap risiko inovasi teknologi baru</small></span>
                            <span><b>Kredit Utang / KUR</b><br><small>Hanya cocok untuk bisnis yang sudah untung harian</small></span>
                        </div>
                        <div class="compare-row">
                            <span><b>Mesin & Rekayasa Produk</b><br><small>PST butuh mesin cetak plastik industri</small></span>
                            <span><b>Pelatihan Marketplace</b><br><small>Diajak pelatihan bikin akun Shopee & Tokopedia</small></span>
                        </div>
                        <div class="compare-row">
                            <span><b>Mentoring Komersial Intensif</b><br><small>Strategi akuisisi user skala nasional</small></span>
                            <span><b>Webinar Literasi Umum</b><br><small>Sosialisasi teori satu arah bersertifikat</small></span>
                        </div>
                    </div>
                    <div class="evidence-tag mt-3"><span class="badge amber">Kekuatan Bukti: SEDANG–KUAT</span> Analisis teks media (4,3x rasio) + Studi kasus PST & survei kualitatif</div>
                </div>
            </div>
            """
        },

        # SLIDE 9: BABAK 2 - INSIGHT 3
        {
            "id": 9,
            "badge": "BABAK 2: SEPI DI BELAKANG LAYAR",
            "title": "Insight 3: Tumbuh Tanpa Modal, Tapi Lambat",
            "subtitle": "83% founder bertahan secara mandiri; mayoritas mencetak pendapatan tanpa pernah didanai",
            "speaker_notes": "Insight 3 adalah temuan paling mengejutkan (counter-intuitive) dari riset ini. Kita menemukan bahwa ketiadaan modal tidak serta-merta membunuh startup saat lahir. 10 dari 12 founder (83,3%) tidak pernah menerima pendanaan sepeser pun. Namun, 7 dari 12 founder sudah memiliki revenue atau tahap scaling, dan 6 di antaranya adalah 100% modal mandiri (bootstrapping). Founder SuratPlus memulai bisnis hanya dengan modal awal Rp500 ribu, butuh 6 bulan untuk meraih pendapatan Rp4 juta/bulan, dan butuh 2 tahun baru mampu menggaji tim setara UMR. Founder Bepal bertahan dengan bekerja sampingan di kantor lain. Founder memiliki resiliensi luar biasa (keyakinan bertahan 4,08/5), namun tanpa modal ekuitas, mereka tumbuh dengan kecepatan merangkak.",
            "content": f"""
            <div class="grid-2col">
                <div class="card">
                    <h4 class="mb-2">Paradoks Keyakinan Founder (Skala Likert)</h4>
                    <p class="text-sm text-muted mb-3">Founder sangat percaya pada daya tahan dirinya, tetapi pesimis pada ekosistem dan pendanaan:</p>
                    {c3_html}
                </div>
                <div class="card card-accent-left">
                    <h4 class="mb-3">Anatomi Ketahanan 12 Founder Aceh</h4>
                    <div class="stat-highlight-row">
                        <div class="stat-box">
                            <div class="val red">83,3%</div>
                            <div class="lbl">Tidak Pernah Didanai (10 dari 12 Founder)</div>
                        </div>
                        <div class="stat-box">
                            <div class="val green">6 / 7</div>
                            <div class="lbl">Startup Ber-Revenue Tumbuh 100% Bootstrap Mandiri</div>
                        </div>
                    </div>
                    <div class="quote-box mt-3">
                        <p class="quote-text">"Modal awal SuratPlus cuma Rp500 ribu. Enam bulan pertama baru dapat omzet Rp4 juta/bulan... Butuh waktu 2 tahun sampai akhirnya bisa menggaji tim setara standar UMR."</p>
                        <span class="quote-author">— Founder SuratPlus</span>
                    </div>
                    <div class="quote-box mt-2">
                        <p class="quote-text">"Serba sendiri dengan modal sendiri. Kebetulan juga aku masih kerja di tempat lain untuk nutupin operasional."</p>
                        <span class="quote-author">— Founder Bepal</span>
                    </div>
                    <div class="evidence-tag mt-3"><span class="badge green">Kekuatan Bukti: KUAT</span> Data kuantitatif survei (n=12) diperkuat detail nominal wawancara</div>
                </div>
            </div>
            """
        },

        # SLIDE 10: BABAK 2 - INSIGHT 4
        {
            "id": 10,
            "badge": "BABAK 2: SEPI DI BELAKANG LAYAR",
            "title": "Insight 4: Jurang Pasca-Hibah (The Post-Grant Chasm)",
            "subtitle": "Ketiadaan jembatan modal pasca-program menyebabkan startup padat karya dan hardware mati suri",
            "speaker_notes": "Insight 4 mengoreksi H4 awal kita. Awalnya kita menduga program inkubasi pemerintah gagal sejak di dalam ruangan. Namun data studi kasus PT Plastik Sago Teknologi (PST) menunjukkan hal yang berbeda: selama kontrak hibah Kemristekdikti berjalan, mereka dimonitor secara ketat, didampingi dosen, dan penjualannya melebihi target. Masalah fatal muncul saat kontrak selesai: ada 'jurang' permodalan. Tidak ada modal lanjutan. Ketika mesin sewaan mereka di Jakarta rusak, mereka tidak punya kas cadangan untuk membeli mesin sendiri. Akibatnya, PST terpaksa vakum sejak 2022. Dari survei terstruktur, 4 dari 6 founder peserta program inkubasi mengaku tidak ada tindak lanjut sama sekali.",
            "content": """
            <div class="grid-2col">
                <div class="card">
                    <h4 class="mb-3">Kronologi Kasus PST: Anatomi Kegagalan Pasca-Kontrak</h4>
                    <div class="timeline-box">
                        <div class="tl-item">
                            <div class="tl-dot green"></div>
                            <div class="tl-content"><b>Fase 1: Inkubasi Berhasil (Hibah Kemristekdikti)</b><br>R&D bioplastik sagu berhasil, dibina intensif, penjualan mangkuk &amp; wadah bioplastik pati sagu melampaui target indikator.</div>
                        </div>
                        <div class="tl-item">
                            <div class="tl-dot red"></div>
                            <div class="tl-content"><b>Fase 2: Jurang Pasca-Kontrak (Kontrak Selesai)</b><br>Pendanaan hibah berhenti resmi. Tidak ada skema jembatan modal kerja atau koneksi ke investor lanjutan.</div>
                        </div>
                        <div class="tl-item">
                            <div class="tl-dot red"></div>
                            <div class="tl-content"><b>Fase 3: Shock Operasional & Mati Suri (2022–Sekarang)</b><br>Mesin sewaan di Jakarta rusak. Biaya investasi mesin mandiri tak terjangkau. Operasional terpaksa vakum.</div>
                        </div>
                    </div>
                </div>
                <div class="card card-accent-left">
                    <h4 class="mb-3">Evaluasi Responden Program Pendampingan</h4>
                    <div class="stat-highlight-row">
                        <div class="stat-box">
                            <div class="val red">66,7%</div>
                            <div class="lbl">Alumni Program Mengalami Putus Hubungan Total (4/6)</div>
                        </div>
                        <div class="stat-box">
                            <div class="val">13,8%</div>
                            <div class="lbl">Artikel Berita yang Mengulas Dampak Keberlanjutan</div>
                        </div>
                    </div>
                    <div class="quote-box mt-3">
                        <p class="quote-text">"Banyak ide startup mahasiswa dan teman-teman di Aceh belum sampai ke tahap komersial selanjutnya sudah layu sebelum berkembang karena dana hibah habis."</p>
                        <span class="quote-author">— Responden Survei Founder #3</span>
                    </div>
                    <div class="evidence-tag mt-3"><span class="badge amber">Kekuatan Bukti: SEDANG</span> Studi kasus mendalam PST + Survei alumni program + Analisis berita</div>
                </div>
            </div>
            """
        },

        # SLIDE 11: BABAK 2 - INSIGHT 5
        {
            "id": 11,
            "badge": "BABAK 2: SEPI DI BELAKANG LAYAR",
            "title": "Insight 5: Defisit Talenta Mendalam & Ketiadaan Panutan",
            "subtitle": "Ketiadaan founder panutan lokal karena hijrah ke Jakarta memperparah kelangkaan keahlian teknis spesifik",
            "speaker_notes": "Insight 5 membahas talenta. Di laporan lama ada narasi bahwa talenta Aceh habis karena kerja remote. Namun data menunjukkan bukti remote work sangat tipis (hanya 9 penyebutan sosmed). Masalah talenta di Aceh sebenarnya bukan kuantitas lulusan IT, melainkan keahlian mendalam (deep expertise) dan ketiadaan figur panutan lokal. PST tidak bisa menemukan ahli permesinan dan molding plastik di Aceh, sehingga harus merekrut pensiunan tenaga ahli dari Batan di Jawa. Bepal mengeluhkan lulusan IT lokal tidak memahami UI/UX. Selain itu, founder SuratPlus mencatat: begitu sebuah startup sukses, foundernya biasanya hijrah ke Jakarta, meninggalkan kekosongan mentor praktisi di Banda Aceh. Skor mentor di survei hanya 2,08 dari 5.",
            "content": f"""
            <div class="grid-2col">
                <div>
                    {c4_html}
                </div>
                <div class="card card-accent-left">
                    <h4 class="mb-3">Dua Dimensi Hambatan Talenta di Lapangan</h4>
                    <div class="point-box">
                        <h5>1. Defisit Keahlian Teknis Spesifik (Bukan Jumlah Lulusan)</h5>
                        <p>Aceh memiliki ribuan lulusan IT/Teknik dari USK, Unimal, dan politeknik, namun keahlian industri spesifik (industrial molding, UI/UX profesional, sistem terdistribusi) nihil. PST harus mengimpor ahli cetak dari Batan Jawa.</p>
                    </div>
                    <div class="point-box mt-2">
                        <h5>2. Eksodus Founder Sukses (Ketiadaan Panutan Lokal)</h5>
                        <p>Ketiadaan mentor praktisi (skor Likert <b>2,08 / 5,0</b>) dipicu oleh migrasi: founder Aceh yang berhasil membesarkan startup biasanya memilih menetap di Jakarta untuk ekspansi pasar, sehingga tidak ada transfer ilmu langsung ke founder pemula.</p>
                    </div>
                    <div class="evidence-tag mt-3"><span class="badge amber">Kekuatan Bukti: SEDANG</span> Wawancara 3 Institusi (PST, SuratPlus, Bepal) + Survei tantangan top-3</div>
                </div>
            </div>
            """
        },

        # SLIDE 12: BABAK 3 - INSIGHT 6
        {
            "id": 12,
            "badge": "BABAK 3: CARA BERTAHAN",
            "title": "Insight 6: Pasarnya Ada, Tapi Bukan di Aceh",
            "subtitle": "Startup yang berhasil bertahan adalah yang sejak awal menyasar pasar nasional (Born-National)",
            "speaker_notes": "Babak 3: Cara Bertahan. Bagaimana startup Aceh bisa survive jika ekosistem lokal serba terbatas? Kuncinya adalah menjadi Born-National sejak hari pertama. Pasar Aceh terbuka untuk mencoba aplikasi digital, tetapi belum memiliki kesediaan membayar (willingness to pay). Bukti terkuat datang dari SuratPlus: mereka memiliki 200.000+ pengguna terdaftar dan 1,8 juta kunjungan web di 250 kota di seluruh Indonesia. Kota pengguna terbanyak adalah Jakarta, Surabaya, Semarang, Bandung, dan Medan. Kota Banda Aceh sendiri hanya berada di peringkat ke-30! Founder SuratPlus menegaskan: masyarakat lokal masih memilih opsi gratisan seperti Canva atau fotokopi. Hal serupa dialami Bepal di Lhokseumawe: antusiasme komunitas tinggi (skor 8,5/10), namun begitu masuk skema berbayar, adopsi anjlok.",
            "content": """
            <div class="grid-2col">
                <div class="card card-accent-left active">
                    <div class="card-tag highlight">BUKTI UTAMA: TRAKSI SURATPLUS</div>
                    <div class="big-metric red">200.000+ <span class="unit">Pengguna (1,8 Juta Kunjungan)</span></div>
                    <p class="card-desc">SuratPlus membuktikan bahwa startup teknologi dengan 200.000+ pengguna terdaftar dan 1,8 juta kunjungan web bisa lahir dan di-code dari Banda Aceh, dengan syarat pasarnya harus nasional.</p>
                    <div class="metric-bullet">
                        <span class="dot red"></span> <b>Top 5 Kota Konsumen:</b> Jakarta, Surabaya, Semarang, Bandung, Medan
                    </div>
                    <div class="metric-bullet">
                        <span class="dot red"></span> <b>Banda Aceh:</b> Hanya menempati urutan ke-30 dari 250 kab/kota
                    </div>
                </div>
                <div class="card">
                    <h4 class="mb-3">Tantangan Daya Beli & Budaya Lokal</h4>
                    <div class="quote-box">
                        <p class="quote-text">"Di Aceh orang lebih milih alternatif fotokopi atau template Canva gratisan dibanding bayar langganan software. Market lokal kurang tertarik jadi user berbayar, maunya gratisan."</p>
                        <span class="quote-author">— Wawancara SuratPlus & Teks Survei Founder</span>
                    </div>
                    <div class="quote-box mt-3">
                        <p class="quote-text">"Minat digital di komunitas Lhokseumawe sebenarnya tinggi (8,5/10), tapi kesiapan dan kemampuan finansial mereka untuk membayar layanan software sangat minim."</p>
                        <span class="quote-author">— Founder Bepal (Lhokseumawe)</span>
                    </div>
                    <div class="evidence-tag mt-3"><span class="badge amber">Kekuatan Bukti: SEDANG–KUAT</span> Data operasional SuratPlus (200rb+ user &amp; 1,8M kunjungan) + Bepal + Skor survei pasar 3,75</div>
                </div>
            </div>
            """
        },

        # SLIDE 13: Sintesis & Reformulasi Hipotesis
        {
            "id": 13,
            "badge": "SINTESIS DATA & REFLEKSI",
            "title": "Evaluasi Hipotesis Awal & Reformulasi Empiris",
            "subtitle": "Mengganti klaim sepihak 'Sempurna 4/4' dengan status metodologis yang matang dan jujur",
            "speaker_notes": "Berikut adalah rangkuman evaluasi hipotesis awal H1 sampai H6. Alih-alih mengklaim semua hipotesis tervalidasi sempurna seperti draf laporan lama, kami menempatkan status metodologis yang jujur. H1 tervalidasi kuat, namun kami reformulasi menjadi H1': ketiadaan modal tidak membunuh startup saat lahir, tetapi mematikan startup padat modal dan memperlambat pertumbuhan. H2 tervalidasi sebagian: defisitnya adalah keahlian mendalam dan mentor, bukan kuantitas sarjana. H3 kami turunkan statusnya menjadi indikatif karena keterbatasan sampel luar Banda Aceh. H4 kami reformulasi ke jurang pasca-program. H5 dipertajam bahwa startup sukses harus born-national. Dan H6 diperkuat dengan bukti framing UMKM di berita.",
            "content": """
            <div class="table-responsive">
                <table class="deck-table">
                    <thead>
                        <tr>
                            <th>Hipotesis Awal</th>
                            <th>Status Empiris</th>
                            <th>Reformulasi Setelah Menemukan Data (Abductive Refinement)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>H1: Akses Pendanaan Terbatas</b></td>
                            <td><span class="badge green">Didukung Kuat</span></td>
                            <td><b>H1′:</b> Ketiadaan modal ekuitas tidak mencegah lahirnya startup, namun memperlambat pertumbuhan dan mematikan startup padat modal (hardware).</td>
                        </tr>
                        <tr>
                            <td><b>H2: Kesenjangan Talenta Digital</b></td>
                            <td><span class="badge amber">Didukung Sebagian</span></td>
                            <td><b>H2′:</b> Yang kurang adalah talenta mendalam (deep tech) dan figur panutan/mentor lokal, bukan jumlah lulusan IT dasar.</td>
                        </tr>
                        <tr>
                            <td><b>H3: Ketergantungan Kampus Luar BA</b></td>
                            <td><span class="badge gray">Bukti Terbatas</span></td>
                            <td><b>H3′:</b> Berfungsi sebagai <i>studi kasus indikatif</i> (PST di Unimal), membutuhkan riset lanjutan dengan sampel wilayah lebih besar.</td>
                        </tr>
                        <tr>
                            <td><b>H4: Program Formalitas Seremoni</b></td>
                            <td><span class="badge amber">Direformulasi</span></td>
                            <td><b>H4′:</b> Kegagalan bukan di dalam program inkubasi, melainkan di <i>jurang pasca-program</i> ketiadaan tindak lanjut modal komersial.</td>
                        </tr>
                        <tr>
                            <td><b>H5: Pasar Lokal Lemah</b></td>
                            <td><span class="badge green">Didukung Kuat</span></td>
                            <td><b>H5′:</b> Startup yang bertahan adalah yang berorientasi nasional (<i>born-national</i>); pasar lokal berminat namun kesediaan membayar rendah.</td>
                        </tr>
                        <tr>
                            <td><b>H6: Orientasi UMKM > R&D</b></td>
                            <td><span class="badge amber">Didukung Sedang</span></td>
                            <td><b>H6′:</b> Ekosistem diperlakukan sebagai digitalisasi UMKM (rasio berita 4,3:1), mengabaikan kebutuhan riset teknologi tinggi.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """
        },

        # SLIDE 14: Rekomendasi Strategis
        {
            "id": 14,
            "badge": "REKOMENDASI STRATEGIS",
            "title": "3 Rekomendasi Aksi: Menjembatani Jurang Ekosistem",
            "subtitle": "Langkah konkret bagi pembuat kebijakan, inkubator universitas, dan komunitas startup",
            "speaker_notes": "Lalu, so what? Apa yang harus dilakukan? Kami merekomendasikan 3 langkah konkret. Pertama: Bangun Dana Jembatan Pasca-Inkubasi (Post-Incubation Bridge Fund) untuk menutup jurang pembiayaan setelah masa hibah habis, khususnya startup berbasis hardware. Kedua: Pisahkan Desain Kebijakan Startup dari Program UMKM Konvensional—startup butuh modal ekuitas dan perlindungan paten, bukan sekadar pelatihan buka lapak online. Ketiga: Bangun 'Diaspora Mentor Fellowship' menghubungkan founder sukses Aceh di Jakarta dengan inovator muda di kampus-kampus lokal untuk mengatasi defisit panutan.",
            "content": """
            <div class="grid-3col">
                <div class="card rec-card">
                    <div class="rec-num">01</div>
                    <h4>Post-Incubation Bridge Fund</h4>
                    <p class="rec-target">Sasaran: Pemda Aceh & Universitas</p>
                    <p class="rec-body">Mendirikan skema modal kerja lanjutan atau dana padanan (matching grant) bagi startup lulusan program yang telah mencapai validasi produk, mencegah kematian mendadak seperti kasus PST.</p>
                </div>
                <div class="card rec-card">
                    <div class="rec-num">02</div>
                    <h4>Redefinisi Program Startup vs UMKM</h4>
                    <p class="rec-target">Sasaran: Dinas Koperasi, BI, Diskominfo</p>
                    <p class="rec-body">Membedakan kurikulum pembinaan: UMKM difokuskan pada digital marketing lokal dan cashflow harian, sedangkan startup teknologi difasilitasi modal ventura, uji lab produk, dan rekayasa hak cipta/paten.</p>
                </div>
                <div class="card rec-card">
                    <div class="rec-num">03</div>
                    <h4>Diaspora Mentor Fellowship</h4>
                    <p class="rec-target">Sasaran: Komunitas Pengusaha & Kampus</p>
                    <p class="rec-body">Membangun jejaring mentoring formal terstruktur yang melibatkan diaspora tech leader dan founder asal Aceh di Jakarta/Bandung untuk mendampingi calon founder secara jarak jauh maupun residensi berkala.</p>
                </div>
            </div>
            """
        },

        # SLIDE 15: Kendala Riset & Mitigasi Teknis
        {
            "id": 15,
            "badge": "REFLEKSI METODOLOGIS",
            "title": "Kendala Lapangan & Solusi Teknis yang Diterapkan",
            "subtitle": "Transparansi tantangan eksekusi teknis selama sprint riset data",
            "speaker_notes": "Sesuai permintaan mentor, kami menjabarkan 4 kendala utama yang dihadapi selama pengerjaan sprint ini. Pertama: URL Google News yang terenkripsi dan portal berita lokal yang memblokir scraping otomatis—kami selesaikan dengan script 02_resolver.py dan fallback extractor. Kedua: Noise data yang masif—kami selesaikan dengan Ingestion Shield yang memfilter 7.192 paragraf non-relevan. Ketiga: Sampel primer yang kecil (12 founder dan 3 wawancara) karena sulitnya menemukan founder aktif di Aceh—kami posisikan sebagai studi kasus kualitatif dan ditriangulasi dengan data makro. Keempat: Ketimpangan volume data antara 6.648 berita dan 25 data survei—kami selesaikan dengan normalisasi persentase per baris, bukan digabung mentah.",
            "content": """
            <div class="grid-2col">
                <div class="card card-sm">
                    <div class="kendala-tag">KENDALA 1: RESOLUSI URL & ANTI-BOT SCRAPING</div>
                    <p class="text-sm"><b>Dampak:</b> 746 percobaan scraping gagal karena redirect terenkripsi Google News dan proteksi server media.</p>
                    <p class="text-sm text-success"><b>Solusi:</b> Membangun pipeline mandiri <code>02_resolver.py</code> dengan request header browser emulation & multi-extractor fallback, berhasil mengamankan 1.231 artikel dari 243 domain.</p>
                </div>
                <div class="card card-sm">
                    <div class="kendala-tag">KENDALA 2: NOISE DATA LUAR WILAYAH</div>
                    <p class="text-sm"><b>Dampak:</b> 7.192 paragraf berita nasional tidak sengaja terambil karena kata kunci umum (misal: 'BSI', 'PON', 'Kemenparekraf').</p>
                    <p class="text-sm text-success"><b>Solusi:</b> Mengembangkan <i>Ingestion Shield</i> dengan dictionary entitas lokal Aceh & filter skor relevansi domain (<code>rejected_dataset.csv</code>).</p>
                </div>
                <div class="card card-sm">
                    <div class="kendala-tag">KENDALA 3: SAMPEL PRIMER KECIL (n=12 SURVEI, n=3 WAWANCARA)</div>
                    <p class="text-sm"><b>Dampak:</b> Tidak memungkinkan pengujian signifikansi statistik parametrik secara terisolasi.</p>
                    <p class="text-sm text-success"><b>Solusi:</b> Memposisikan survei sebagai penguat kualitatif (deep probing) dan mentriangulasikannya secara konvergen dengan korpus teks 7.000+ unit.</p>
                </div>
                <div class="card card-sm">
                    <div class="kendala-tag">KENDALA 4: KETIMPANGAN VOLUME ANTAR SUMBER</div>
                    <p class="text-sm"><b>Dampak:</b> Penggabungan mentah akan menenggelamkan suara founder di bawah 6.648 paragraf berita.</p>
                    <p class="text-sm text-success"><b>Solusi:</b> Analisis dilakukan terisolasi per sumber terlebih dahulu, kemudian dinormalisasi dalam matriks persentase lintas sumber (C8 Heatmap).</p>
                </div>
            </div>
            """
        },

        # SLIDE 16: Limitasi & Riset Lanjutan
        {
            "id": 16,
            "badge": "LIMITASI RISET",
            "title": "Limitasi Metodologis & Arahan Riset Lanjutan",
            "subtitle": "Keterbatasan ilmiah yang perlu diperhatikan dalam membaca laporan ini",
            "speaker_notes": "Sebagai penutup sesi utama, kami mencatat limitasi riset ini secara transparan. Pertama: Analisis sentimen berita menggunakan lexicon-based dictionary bahasa Indonesia, yang memiliki keterbatasan mendeteksi eufemisme atau sindiran halus gaya bahasa jurnalistik. Kedua: Sampel luar Banda Aceh masih terbatas (hanya Lhokseumawe dan sebagian kecil wilayah lain), sehingga generalisasi tingkat provinsi harus dilakukan secara berhati-hati. Ketiga: Riset ini bersifat cross-sectional (potong lintang); kami menyarankan penelitian lanjutan melakukan tracking longitudinal terhadap kohort alumni program inkubasi selama 3-5 tahun untuk melihat tingkat kelangsungan hidup jangka panjang.",
            "content": """
            <div class="grid-2col">
                <div class="card">
                    <h4 class="mb-3 text-red">Limitasi Ilmiah Laporan</h4>
                    <ul class="clean-list">
                        <li><b>Sentimen Berita Jurnalistik:</b> Bahasa jurnalistik Indonesia yang formal menghasilkan dominasi kategori netral (81,2%), berpotensi menyamarkan kritik struktural implisit.</li>
                        <li><b>Representasi Spasial Luar Banda Aceh:</b> Responden survei mayoritas berbasis di ibu kota provinsi; dinamika ekosistem di pantai barat-selatan dan dataran tinggi Gayo belum terwakili secara mendalam.</li>
                        <li><b>Ketiadaan Data Finansial Terbuka:</b> Startup lokal belum berbadan hukum modal ventura terbuka sehingga data omzet dan valuasi bersandar pada self-reported interview.</li>
                    </ul>
                </div>
                <div class="card">
                    <h4 class="mb-3 text-blue">Rekomendasi Agenda Riset Lanjutan</h4>
                    <ul class="clean-list">
                        <li><b>Pelacakan Kohort Longitudinal:</b> Melakukan tracking 3 tahun terhadap alumni program inkubasi kampus di USK dan Unimal untuk memetakan tingkat kelangsungan hidup riil.</li>
                        <li><b>Studi Etnografi Diaspora Tech:</b> Riset mendalam terhadap motivasi dan hambatan para talenta teknologi Aceh di kota-kota besar untuk kembali membangun daerah.</li>
                        <li><b>Pengembangan Model NLP Lokal:</b> Fine-tuning model IndoBERT dengan korpus dialek lokal dan konteks regulasi perbankan syariah di Aceh.</li>
                    </ul>
                </div>
            </div>
            <div class="card text-center mt-3" style="background:#F1F5F9;">
                <b>Terima Kasih.</b> Sesi Presentasi Selesai — Membuka Sesi Diskusi & Tanya Jawab Penguji.
            </div>
            """
        },

        # SLIDE 17 (APPENDIX A1): Heatmap Topik
        {
            "id": 17,
            "badge": "LAMPIRAN [A1]",
            "title": "Disparitas Fokus Topik Lintas Sumber Data",
            "subtitle": "Matriks persentase dinormalisasi per baris sumber data (C8 Heatmap)",
            "speaker_notes": "Lampiran A1 menampilkan heatmap distribusi topik yang telah dinormalisasi per baris. Dari sini terlihat jelas bagaimana media sosial memberi porsi 13,5% pada isu infrastruktur—jauh lebih tinggi dari berita (2,4%). Media massa sangat condong ke digitalisasi (23%), sementara wawancara dan survei merata menyoroti masalah pendanaan, talenta, dan kelangsungan ekosistem.",
            "content": f"""
            <div class="text-center">
                <img src="{c8_b64}" class="slide-img" style="max-height:480px;" alt="Heatmap Normalisasi Topik">
            </div>
            """
        },

        # SLIDE 18 (APPENDIX A2): Profil 3 Narasumber
        {
            "id": 18,
            "badge": "LAMPIRAN [A2]",
            "title": "Profil 3 Studi Kasus Wawancara Mendalam",
            "subtitle": "Perbandingan model bisnis, rekam jejak pendanaan, dan tantangan operasional utama",
            "speaker_notes": "Lampiran A2 merangkum 3 studi kasus yang kami wawancarai. SuratPlus mewakili startup software (SaaS) murni dengan pengguna massal; PT Plastik Sago Teknologi mewakili startup hardware/bioplastik padat karya; dan Bepal mewakili inisiatif komunitas digital di luar Banda Aceh (Lhokseumawe). Perbedaan karakteristik ketiganya memperkaya triangulasi kualitatif kami.",
            "content": """
            <div class="grid-3col">
                <div class="card">
                    <h4>1. SuratPlus</h4>
                    <span class="badge blue mb-2">SaaS / Template Surat Digital</span>
                    <p class="text-sm"><b>Model:</b> Freemium dokumen & generator surat resmi.</p>
                    <p class="text-sm"><b>Traksi:</b> 200.000+ pengguna terdaftar & 1,8 juta kunjungan web di 250 kota (Banda Aceh peringkat ke-30).</p>
                    <p class="text-sm"><b>Status Modal:</b> 100% Bootstrap mandiri, modal awal Rp500 ribu.</p>
                    <p class="text-sm text-red"><b>Pain Point:</b> Pasar lokal Banda Aceh enggan bayar (pilih Canva gratis); sulit mencari mentor lokal karena yang sukses pindah ke Jakarta.</p>
                </div>
                <div class="card">
                    <h4>2. PT Plastik Sago Teknologi (PST)</h4>
                    <span class="badge green mb-2">Deep-Tech / Bioplastik Sagu</span>
                    <p class="text-sm"><b>Model:</b> Manufaktur mangkuk & wadah ramah lingkungan berbasis pati sagu.</p>
                    <p class="text-sm"><b>Traksi:</b> Penjualan melampaui target saat masa inkubasi Kemristekdikti.</p>
                    <p class="text-sm"><b>Status Modal:</b> Hibah riset pemerintah (berhenti kontrak 2021).</p>
                    <p class="text-sm text-red"><b>Pain Point:</b> Jurang pasca-kontrak: mesin sewaan di Jakarta rusak, modal mandiri tak cukup untuk beli mesin baru. Vakum sejak 2022.</p>
                </div>
                <div class="card">
                    <h4>3. Bepal (Lhokseumawe)</h4>
                    <span class="badge amber mb-2">Media & Komunitas Digital</span>
                    <p class="text-sm"><b>Model:</b> Agregator informasi & platform komunitas lokal.</p>
                    <p class="text-sm"><b>Traksi:</b> Komunitas aktif dengan skor antusiasme 8,5 / 10.</p>
                    <p class="text-sm"><b>Status Modal:</b> Mandiri disubsidi founder kerja sampingan.</p>
                    <p class="text-sm text-red"><b>Pain Point:</b> Daya beli rendah di kota lapis kedua; talenta IT lokal minim keahlian desain UI/UX.</p>
                </div>
            </div>
            """
        },

        # SLIDE 19 (APPENDIX A3): Detail Arsitektur Labeling
        {
            "id": 19,
            "badge": "LAMPIRAN [A3]",
            "title": "Arsitektur Labeling & Audit Kualitas Data",
            "subtitle": "Metrik otomasi pelabelan dan audit 815 baris data (label_stats.json)",
            "speaker_notes": "Lampiran A3 memperlihatkan audit kualitas labeling teks. Dari 13.840 baris data berita bersih, 94,1% berhasil dilabeli otomatis oleh sistem rule-based bertingkat kami (direct matching, artikel propagation, dan title propagation). Hanya 815 baris atau 5,9% yang masuk kategori needs_review dan diaudit secara manual, menjamin konsistensi labeling topik di seluruh korpus.",
            "content": """
            <div class="grid-2col">
                <div class="card">
                    <h4 class="mb-3">Statistik Otomasi Labeling (N=13.840)</h4>
                    <div class="stat-highlight-row">
                        <div class="stat-box">
                            <div class="val green">94,1%</div>
                            <div class="lbl">Tingkat Otomasi Labeling (13.025 Baris)</div>
                        </div>
                        <div class="stat-box">
                            <div class="val">5,9%</div>
                            <div class="lbl">Baris Masuk Needs Review (815 Baris)</div>
                        </div>
                    </div>
                    <ul class="clean-list mt-3">
                        <li><b>Direct Matching:</b> 9.008 baris dilabeli langsung via kata kunci unik.</li>
                        <li><b>Article Propagation:</b> 3.694 baris diturunkan dari konsensus topik artikel.</li>
                        <li><b>Title Propagation:</b> 323 baris diturunkan dari judul berita utama.</li>
                    </ul>
                </div>
                <div class="card">
                    <h4 class="mb-3">Distribusi Out-of-Domain Filter</h4>
                    <p class="text-sm">Sistem Ingestion Shield berhasil memilah 7.192 paragraf berita yang berada di luar domain ekonomi digital Aceh (misalnya liputan bencana alam, politik umum, atau olahraga tanpa kaitan bisnis).</p>
                    <div class="callout-box mt-3">
                        <b>Integritas Korpus:</b> Seluruh 6.648 paragraf berita yang masuk ke analisis akhir telah melalui verifikasi dua lapis relevansi domain.
                    </div>
                </div>
            </div>
            """
        },

        # SLIDE 20 (APPENDIX A4): Audit Klaim Lama vs Terverifikasi
        {
            "id": 20,
            "badge": "LAMPIRAN [A4]",
            "title": "Rekonsiliasi Audit Data: Klaim Lama vs Fakta Riil",
            "subtitle": "Koreksi menyeluruh terhadap inkonsistensi draf laporan sebelumnya",
            "speaker_notes": "Lampiran A4 adalah bukti audit integritas data kami. Kami menyandingkan klaim di draf awal dengan angka aktual terverifikasi. Kami mengoreksi klaim sentimen berita dari 86,5% menjadi 81,2%; klaim prioritas modal dari 58,3% menjadi 50%; membuang klaim fiktif 44 remote work dan 95% omzet SuratPlus; serta menghapus label sepihak 'SEMPURNA 4/4'. Riset ini kini berdiri di atas landasan angka yang 100% dapat dipertanggungjawabkan di depan siapa pun.",
            "content": """
            <div class="table-responsive">
                <table class="deck-table text-xs">
                    <thead>
                        <tr>
                            <th>Parameter Klaim</th>
                            <th>Klaim Awal Laporan</th>
                            <th>Fakta Aktual Terverifikasi</th>
                            <th>Tindakan Perbaikan</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Sentimen Berita Netral</td>
                            <td>86,5% Netral</td>
                            <td><b>81,21% Netral</b> (0,51% negatif, 18,28% positif)</td>
                            <td>Dikoreksi di semua slide & visualisasi</td>
                        </tr>
                        <tr>
                            <td>Akses Pendanaan #1</td>
                            <td>58,3% Responden</td>
                            <td><b>50,0% Responden</b> (6 dari 12 founder)</td>
                            <td>Angka diperbarui sesuai survey_structured.csv</td>
                        </tr>
                        <tr>
                            <td>Sebaran User SuratPlus</td>
                            <td>95%+ Omzet dari Jawa</td>
                            <td><b>200.000+ User (1,8 Juta Kunjungan) di 250 Kota; Banda Aceh urutan ke-30</b></td>
                            <td>Diganti dengan data riil yang lebih kuat</td>
                        </tr>
                        <tr>
                            <td>Unit Remote Work Sosmed</td>
                            <td>44 Percakapan Remote</td>
                            <td><b>Hanya 9 Unit</b> yang menyebut remote/wfa secara eksplisit</td>
                            <td>Narasi 'Remote Arbitrage' dibuang dari headline</td>
                        </tr>
                        <tr>
                            <td>Diskusi Modal Ventur Sosmed</td>
                            <td>Klaim bernilai Nol (0)</td>
                            <td><b>34 Unit Sosmed</b> menyebut investor / VC</td>
                            <td>Klaim ekstrem 'nol' dihapus</td>
                        </tr>
                        <tr>
                            <td>Status Validasi Hipotesis</td>
                            <td>TERVALIDASI SEMPURNA 4/4</td>
                            <td><b>Rubrik Kekuatan Bukti:</b> 2 Kuat, 4 Sedang, 1 Indikatif</td>
                            <td>Diterapkan standar kejujuran ilmiah</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """
        }
    ]

    total_slides = len(slides)

    # 3. HTML & CSS TEMPLATE
    css_content = """
    :root {
        --accent: #E4572E;
        --accent-light: #FBD8CE;
        --navy: #1F2A44;
        --navy-dark: #0F172A;
        --slate: #64748B;
        --gray-light: #F8FAFC;
        --border: #E2E8F0;
        --card-bg: #FFFFFF;
        --success: #2E7D32;
        --amber: #D97706;
    }
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    body {
        font-family: 'Inter', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
        background: #0B1120;
        color: var(--navy);
        overflow: hidden;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    /* Toolbar */
    .toolbar {
        background: #111827;
        color: #F9FAFB;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 24px;
        border-bottom: 1px solid #1F2937;
        z-index: 100;
        font-size: 14px;
    }
    .toolbar-left, .toolbar-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .brand-title {
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-tag {
        background: var(--accent);
        color: #FFF;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 800;
    }
    .btn {
        background: #1F2937;
        color: #E5E7EB;
        border: 1px solid #374151;
        padding: 6px 14px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .btn:hover {
        background: #374151;
        color: #FFF;
    }
    .btn.active {
        background: var(--accent);
        border-color: var(--accent);
        color: #FFF;
    }
    .slide-counter {
        font-weight: 600;
        color: #9CA3AF;
        min-width: 90px;
        text-align: center;
    }
    /* Deck Container */
    .deck-container {
        flex: 1;
        position: relative;
        overflow: hidden;
        background: #0F172A;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .slide {
        display: none;
        width: 100%;
        max-width: 1400px;
        height: 100%;
        max-height: 860px;
        background: #FFFFFF;
        border-radius: 14px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        padding: 36px 48px;
        flex-direction: column;
        justify-content: flex-start;
        position: relative;
        overflow-y: auto;
    }
    .slide.active {
        display: flex;
        animation: fadeIn 0.3s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.99); }
        to { opacity: 1; transform: scale(1); }
    }
    /* Slide Header */
    .slide-header {
        margin-bottom: 24px;
        border-bottom: 2px solid var(--border);
        padding-bottom: 14px;
    }
    .slide-badge {
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--accent);
        margin-bottom: 4px;
    }
    .slide-title {
        font-size: 26px;
        font-weight: 800;
        color: var(--navy);
        line-height: 1.25;
        margin-bottom: 4px;
    }
    .slide-subtitle {
        font-size: 14px;
        color: var(--slate);
        font-weight: 500;
    }
    .slide-body {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    /* Grid Helpers */
    .grid-2col {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
    }
    .grid-3col {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
    }
    /* Cards */
    .card {
        background: var(--gray-light);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
    }
    .card-sm {
        padding: 14px 18px;
    }
    .card-accent-left {
        border-left: 5px solid var(--slate);
    }
    .card-accent-left.active {
        border-left: 5px solid var(--accent);
        background: #FFF7F5;
    }
    .card-tag {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: var(--slate);
        margin-bottom: 8px;
    }
    .card-tag.highlight {
        color: var(--accent);
    }
    .big-metric {
        font-size: 38px;
        font-weight: 800;
        color: var(--navy);
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .big-metric.red {
        color: var(--accent);
    }
    .big-metric .unit {
        font-size: 14px;
        font-weight: 600;
        color: var(--slate);
    }
    .card-desc {
        font-size: 13.5px;
        color: var(--navy);
        line-height: 1.5;
        margin-bottom: 12px;
    }
    .metric-bullet {
        font-size: 13px;
        color: var(--navy);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
    }
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot.red { background: var(--accent); }
    .dot.green { background: var(--success); }
    /* Hero */
    .hero-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        padding: 20px 0;
    }
    .hero-stats-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 32px;
    }
    .stat-pill {
        background: var(--gray-light);
        border: 1px solid var(--border);
        border-radius: 30px;
        padding: 8px 18px;
        font-size: 13.5px;
        font-weight: 600;
        color: var(--navy);
    }
    .stat-pill .num {
        color: var(--accent);
        font-weight: 800;
    }
    .hero-quote {
        background: #F8FAFC;
        border-left: 6px solid var(--accent);
        padding: 28px 36px;
        font-size: 20px;
        font-weight: 600;
        line-height: 1.6;
        color: var(--navy);
        border-radius: 0 12px 12px 0;
        margin-bottom: 32px;
    }
    .meta-footer {
        display: flex;
        gap: 32px;
        font-size: 13px;
        color: var(--slate);
        border-top: 1px solid var(--border);
        padding-top: 18px;
    }
    /* Stat Boxes */
    .stat-highlight-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
    }
    .stat-box {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 16px;
    }
    .stat-box .val {
        font-size: 24px;
        font-weight: 800;
        color: var(--navy);
    }
    .stat-box .val.red { color: var(--accent); }
    .stat-box .val.green { color: var(--success); }
    .stat-box .lbl {
        font-size: 11.5px;
        font-weight: 600;
        color: var(--slate);
        margin-top: 4px;
        line-height: 1.3;
    }
    /* Quotes */
    .quote-box {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 6px;
        padding: 12px 16px;
    }
    .quote-text {
        font-size: 13px;
        font-style: italic;
        color: var(--navy);
        line-height: 1.45;
        margin-bottom: 4px;
    }
    .quote-author {
        font-size: 11.5px;
        font-weight: 700;
        color: var(--slate);
    }
    /* Hypothesis Cards */
    .hypo-card {
        background: var(--gray-light);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
    }
    .hypo-id {
        display: inline-block;
        background: var(--navy);
        color: #FFF;
        font-size: 11px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .hypo-card h4 {
        font-size: 14.5px;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 6px;
    }
    .hypo-card p {
        font-size: 12.5px;
        color: var(--slate);
        line-height: 1.4;
    }
    /* Badges */
    .badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .badge.green { background: #DCFCE7; color: #166534; }
    .badge.amber { background: #FEF3C7; color: #92400E; }
    .badge.blue { background: #DBEAFE; color: #1E40AF; }
    .badge.gray { background: #F1F5F9; color: #475569; }
    .evidence-tag {
        font-size: 12.5px;
        font-weight: 600;
        color: var(--navy);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    /* Tables */
    .deck-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
    }
    .deck-table th {
        background: #F1F5F9;
        color: var(--navy);
        font-weight: 700;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 2px solid var(--border);
    }
    .deck-table td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
        color: var(--navy);
        vertical-align: top;
    }
    /* Compare Table */
    .compare-table {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }
    .compare-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
        font-size: 12px;
        gap: 12px;
    }
    .compare-row:last-child { border-bottom: none; }
    .compare-row.header {
        background: #F1F5F9;
        font-weight: 700;
        color: var(--navy);
    }
    /* Timeline */
    .timeline-box {
        display: flex;
        flex-direction: column;
        gap: 16px;
        position: relative;
        padding-left: 20px;
    }
    .timeline-box::before {
        content: '';
        position: absolute;
        left: 6px;
        top: 8px;
        bottom: 8px;
        width: 2px;
        background: var(--border);
    }
    .tl-item {
        position: relative;
    }
    .tl-dot {
        position: absolute;
        left: -20px;
        top: 4px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid #FFF;
    }
    .tl-dot.green { background: var(--success); }
    .tl-dot.red { background: var(--accent); }
    .tl-content {
        font-size: 12.5px;
        line-height: 1.45;
        color: var(--navy);
    }
    /* Recommendations */
    .rec-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-top: 4px solid var(--accent);
        padding: 22px;
    }
    .rec-num {
        font-size: 28px;
        font-weight: 900;
        color: var(--accent);
        line-height: 1;
        margin-bottom: 10px;
    }
    .rec-card h4 {
        font-size: 16px;
        font-weight: 800;
        color: var(--navy);
        margin-bottom: 6px;
    }
    .rec-target {
        font-size: 11.5px;
        font-weight: 700;
        color: var(--slate);
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .rec-body {
        font-size: 13px;
        color: var(--navy);
        line-height: 1.5;
    }
    /* Workflow */
    .workflow-grid {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .wf-step {
        flex: 1;
        background: var(--gray-light);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .wf-step.highlight {
        background: #FFF7F5;
        border-color: var(--accent);
    }
    .wf-step .step-num {
        font-size: 10px;
        font-weight: 800;
        color: var(--slate);
        margin-bottom: 4px;
    }
    .wf-step h5 {
        font-size: 13px;
        font-weight: 800;
        color: var(--navy);
        margin-bottom: 4px;
    }
    .wf-step p {
        font-size: 11px;
        color: var(--slate);
    }
    .wf-arrow {
        color: var(--slate);
        font-weight: 800;
        font-size: 16px;
    }
    /* Speaker Notes Modal/Overlay */
    .speaker-notes-drawer {
        display: none;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #111827;
        color: #F3F4F6;
        border-top: 3px solid var(--accent);
        padding: 20px 32px;
        z-index: 200;
        max-height: 240px;
        overflow-y: auto;
        box-shadow: 0 -10px 25px rgba(0,0,0,0.5);
    }
    .speaker-notes-drawer.open {
        display: block;
    }
    .notes-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .notes-title {
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--accent);
    }
    .notes-body {
        font-size: 14px;
        line-height: 1.6;
        color: #E5E7EB;
    }
    /* Helpers */
    .clean-list {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 10px;
        font-size: 13px;
        color: var(--navy);
    }
    .clean-list li {
        position: relative;
        padding-left: 18px;
    }
    .clean-list li::before {
        content: '▪';
        color: var(--accent);
        position: absolute;
        left: 0;
        font-size: 16px;
        line-height: 1;
    }
    .callout-box {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
        padding: 10px 16px;
        font-size: 12.5px;
        color: #1E3A8A;
    }
    .slide-img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        border: 1px solid var(--border);
    }
    .mt-2 { margin-top: 8px; }
    .mt-3 { margin-top: 14px; }
    .mt-4 { margin-top: 20px; }
    .mb-2 { margin-bottom: 8px; }
    .mb-3 { margin-bottom: 14px; }
    .text-sm { font-size: 12.5px; }
    .text-xs { font-size: 11.5px; }
    .text-muted { color: var(--slate); }
    .text-red { color: var(--accent); }
    .text-blue { color: #2563EB; }
    .text-success { color: var(--success); }
    .text-center { text-align: center; }

    /* PRINT STYLES (PDF EXPORT OPTIMIZED) */
    @media print {
        body {
            background: #FFFFFF !important;
            overflow: visible !important;
            height: auto !important;
        }
        .toolbar, .speaker-notes-drawer {
            display: none !important;
        }
        .deck-container {
            padding: 0 !important;
            background: #FFF !important;
            display: block !important;
        }
        .slide {
            display: flex !important;
            page-break-after: always !important;
            break-after: page !important;
            width: 100% !important;
            max-width: 100% !important;
            height: 100vh !important;
            max-height: 100vh !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 30px 40px !important;
        }
        @page {
            size: landscape;
            margin: 0;
        }
    }
    """

    # Assemble HTML
    slides_html = ""
    for s in slides:
        active_cls = " active" if s["id"] == 1 else ""
        slides_html += f"""
        <div class="slide{active_cls}" id="slide-{s['id']}" data-slide-id="{s['id']}" data-notes="{s['speaker_notes']}">
            <div class="slide-header">
                <div class="slide-badge">{s['badge']}</div>
                <h2 class="slide-title">{s['title']}</h2>
                <div class="slide-subtitle">{s['subtitle']}</div>
            </div>
            <div class="slide-body">
                {s['content']}
            </div>
        </div>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slide Deck: Analisis Ekosistem Startup Aceh 2026</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        {css_content}
    </style>
</head>
<body>

    <!-- Executive Toolbar -->
    <div class="toolbar">
        <div class="toolbar-left">
            <div class="brand-title">
                GRAK RESEARCH <span class="brand-tag">MENTOR DECK</span>
            </div>
            <button class="btn" id="prevBtn" onclick="prevSlide()">◀ Sebelumnya</button>
            <div class="slide-counter" id="slideCounter">Slide 1 / {total_slides}</div>
            <button class="btn" id="nextBtn" onclick="nextSlide()">Selanjutnya ▶</button>
        </div>
        <div class="toolbar-right">
            <button class="btn" id="notesToggleBtn" onclick="toggleNotes()">📝 Speaker Notes (N)</button>
            <button class="btn" id="fullscreenBtn" onclick="toggleFullscreen()">⛶ Layar Penuh (F)</button>
            <button class="btn" onclick="window.print()">🖨️ Cetak / Simpan PDF</button>
        </div>
    </div>

    <!-- Main Deck Container -->
    <div class="deck-container">
        {slides_html}
    </div>

    <!-- Speaker Notes Overlay -->
    <div class="speaker-notes-drawer" id="notesDrawer">
        <div class="notes-header">
            <div class="notes-title">🎙️ Poin Presenter & Antisipasi Pertanyaan Penguji (Tekan 'N' untuk sembunyikan)</div>
            <button class="btn" style="padding:2px 8px;" onclick="toggleNotes()">✕</button>
        </div>
        <div class="notes-body" id="notesContent"></div>
    </div>

    <script>
        let currentSlide = 1;
        const totalSlides = {total_slides};

        function showSlide(index) {{
            if (index < 1) index = 1;
            if (index > totalSlides) index = totalSlides;
            currentSlide = index;

            document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
            const activeSlide = document.getElementById(`slide-${{currentSlide}}`);
            if (activeSlide) {{
                activeSlide.classList.add('active');
                // Trigger plotly redraw if any
                window.dispatchEvent(new Event('resize'));
            }}

            document.getElementById('slideCounter').textContent = `Slide ${{currentSlide}} / ${{totalSlides}}`;
            document.getElementById('prevBtn').disabled = (currentSlide === 1);
            document.getElementById('nextBtn').disabled = (currentSlide === totalSlides);

            // Update notes
            const notes = activeSlide ? activeSlide.getAttribute('data-notes') : '';
            document.getElementById('notesContent').textContent = notes;
        }}

        function nextSlide() {{
            if (currentSlide < totalSlides) {{
                showSlide(currentSlide + 1);
            }}
        }}

        function prevSlide() {{
            if (currentSlide > 1) {{
                showSlide(currentSlide - 1);
            }}
        }}

        function toggleNotes() {{
            const drawer = document.getElementById('notesDrawer');
            const btn = document.getElementById('notesToggleBtn');
            drawer.classList.toggle('open');
            btn.classList.toggle('active');
        }}

        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(err => alert(err.message));
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}

        // Keyboard Navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
                e.preventDefault();
                nextSlide();
            }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
                e.preventDefault();
                prevSlide();
            }} else if (e.key.toLowerCase() === 'n') {{
                toggleNotes();
            }} else if (e.key.toLowerCase() === 'f') {{
                toggleFullscreen();
            }} else if (e.key === 'Home') {{
                showSlide(1);
            }} else if (e.key === 'End') {{
                showSlide(totalSlides);
            }}
        }});

        // Init
        showSlide(1);
    </script>
</body>
</html>
"""

    deck_out_file = os.path.join(deck_dir, 'index.html')
    with open(deck_out_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Successfully built presentation deck at: {deck_out_file}")

if __name__ == '__main__':
    build_presentation_deck()
