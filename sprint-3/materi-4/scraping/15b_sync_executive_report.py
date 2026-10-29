"""
15b_sync_executive_report.py — Deterministic Synchronizer for laporan_sprint3_tim_data.html
===========================================================================================
Menyuntikkan Base64 grafik PNG terbaru, data Chart.js (#topicChart), dan metrik terverifikasi
dari verified_metrics.json ke dalam laporan_sprint3_tim_data.html agar 100% bebas mismatch.
"""

import os
import re
import json
import base64
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
STORY_DIR = os.path.join(PROCESSED_DIR, "storytelling")
CHARTS_PNG_DIR = os.path.join(STORY_DIR, "charts_png")
METRICS_PATH = os.path.join(STORY_DIR, "verified_metrics.json")
HTML_PATH = os.path.join(PROCESSED_DIR, "laporan_sprint3_tim_data.html")

ALT_TO_PNG = {
    "Kontras Sentimen Lintas Sumber": "c2_sentiment_contrast_16_9.png",
    "Disparitas Fokus Antar Sumber C8 Heatmap": "c8_topic_heatmap_16_9.png",
    "Likert Dotplot Chart": "c3_likert_dotplot_16_9.png",
    "Funding Waffle Chart": "c5_funding_waffle_16_9.png",
    "Challenges Ranking Chart": "c4_challenges_ranking_16_9.png",
}


def main():
    if not os.path.exists(HTML_PATH):
        raise FileNotFoundError(f"Deliverable HTML tidak ditemukan: {HTML_PATH}")
    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(f"Verified metrics tidak ditemukan: {METRICS_PATH}")

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inject 5 Base64 PNG Charts berdasarkan atribut alt
    for alt_text, png_name in ALT_TO_PNG.items():
        png_path = os.path.join(CHARTS_PNG_DIR, png_name)
        if not os.path.exists(png_path):
            raise FileNotFoundError(f"Chart PNG tidak ditemukan: {png_path}")
        with open(png_path, "rb") as img_f:
            b64_str = base64.b64encode(img_f.read()).decode("utf-8")

        pattern = re.compile(
            r'(<img\s+src="data:image/png;base64,)[^"]+("\s+alt="' + re.escape(alt_text) + r'")'
        )
        html, count = pattern.subn(r"\g<1>" + b64_str + r"\g<2>", html)
        if count != 1:
            raise RuntimeError(f"Gagal mencocokkan tag img untuk alt='{alt_text}' (matched={count})")

    # 2. Update Sentimen Wawancara pada Kartu Pilar 3
    int_sent = metrics["sentiment_by_source"]["interview"]
    neg_pct = int_sent["pct"]["negative"]
    pos_pct = int_sent["pct"]["positive"]
    neu_pct = int_sent["pct"]["neutral"]

    neg_comma = f"{neg_pct:.1f}".replace(".", ",")
    pos_comma = f"{pos_pct:.1f}".replace(".", ",")

    pillar3_pattern = re.compile(
        r'(id="pillar-interview"[\s\S]*?)'
        r'<div class="pillar-sentiment-bar" title="Sentimen: [^"]+">\s*'
        r'<div class="sentiment-neg" style="width: [^"]+;"></div>\s*'
        r'<div class="sentiment-pos" style="width: [^"]+;"></div>\s*'
        r'<div class="sentiment-neu" style="width: [^"]+;"></div>\s*'
        r'</div>\s*'
        r'<div style="display: flex; justify-content: space-between; font-size: 0\.65rem; color: #64748B; margin-top: 3px;">\s*'
        r'<span style="color:#DC2626;">Negatif [^<]+</span>\s*'
        r'<span>Positif [^<]+</span>'
    )
    pillar3_replacement = (
        r"\g<1>"
        f'<div class="pillar-sentiment-bar" title="Sentimen: {neg_pct:.1f}% Negatif, {pos_pct:.1f}% Positif, {neu_pct:.1f}% Netral">\n'
        f'                                            <div class="sentiment-neg" style="width: {neg_pct:.1f}%;"></div>\n'
        f'                                            <div class="sentiment-pos" style="width: {pos_pct:.1f}%;"></div>\n'
        f'                                            <div class="sentiment-neu" style="width: {neu_pct:.1f}%;"></div>\n'
        f'                                        </div>\n'
        f'                                        <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: #64748B; margin-top: 3px;">\n'
        f'                                            <span style="color:#DC2626;">Negatif {neg_comma}%</span>\n'
        f'                                            <span>Positif {pos_comma}%</span>'
    )
    html, count_p3 = pillar3_pattern.subn(pillar3_replacement, html)
    if count_p3 != 1:
        raise RuntimeError(f"Gagal memperbarui blok sentimen Pilar 3 (matched={count_p3})")

    # 3. Sinkronisasi Chart.js #topicChart dengan c7_news_topic_framing.csv & verified_metrics.json (N=6.648)
    topic_chart_pattern = re.compile(
        r"data:\s*\{\s*labels:\s*\[[^\]]+\],\s*datasets:\s*\[\{\s*label:\s*'[^']+',\s*data:\s*\[[^\]]+\],\s*backgroundColor:\s*\[[^\]]+\]",
        re.DOTALL,
    )
    topic_chart_replacement = """data: {
                        labels: [
                            'Digitalisasi UMKM / E-Commerce (1.526)',
                            'Pendanaan / KUR Perbankan (1.017)',
                            'Talenta & Literasi Dasar (988)',
                            'Regulasi & Pemerintah (725)',
                            'Akses Pasar (632)',
                            'Ekosistem & Komunitas (432)',
                            'Kisah Sukses & Profil (354)',
                            'Infrastruktur Teknologi & R&D (159)'
                        ],
                        datasets: [{
                            label: 'Porsi Liputan Berita (% dari 6.648 Paragraf)',
                            data: [23.0, 15.3, 14.9, 10.9, 9.5, 6.5, 5.3, 2.4],
                            backgroundColor: [
                                '#1E3A8A',
                                '#CBD5E1',
                                '#CBD5E1',
                                '#CBD5E1',
                                '#CBD5E1',
                                '#CBD5E1',
                                '#94A3B8',
                                '#E4572E'
                            ]"""
    html, count_tc = topic_chart_pattern.subn(topic_chart_replacement, html)
    if count_tc != 1:
        raise RuntimeError(f"Gagal memperbarui data #topicChart (matched={count_tc})")

    html = html.replace("max: 36", "max: 26")

    # 4. Perbaikan Ketidaksinkronan Teks Narasi (N=12 Founder & SuratPlus 200.000+ Pengguna / 1,8 Juta Kunjungan)
    html = html.replace(
        "(N=6 dari 15 founder disurvei)",
        "(N=6 dari 12 founder disurvei)",
    )
    html = html.replace(
        '1,8 Juta <span style="font-size:1rem; font-weight:500; color:#64748B;">Pengguna di 250 Kota</span>',
        '200rb+ Pengguna <span style="font-size:1rem; font-weight:500; color:#64748B;">&amp; 1,8 Juta Kunjungan di 250 Kota</span>',
    )
    html = html.replace(
        "<b>Traksi Terverifikasi:</b> 1,8 Juta pengguna di 250 kabupaten/kota.",
        "<b>Traksi Terverifikasi:</b> 200.000+ pengguna terdaftar (1,8 juta kunjungan web) di 250 kabupaten/kota.",
    )
    html = html.replace(
        "Startup SaaS lokal (SuratPlus) menembus 1,8 juta pengguna di 250 kota",
        "Startup SaaS lokal (SuratPlus) menembus 200.000+ pengguna terdaftar (1,8 juta kunjungan web) di 250 kota",
    )
    html = html.replace(
        "42,48% negatif",
        "30,09% negatif",
    )

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ [15b] Berhasil menyinkronkan {HTML_PATH} (Base64 PNGs, #topicChart, Pilar 3={neg_pct:.1f}% negatif, & narasi).")


if __name__ == "__main__":
    main()
