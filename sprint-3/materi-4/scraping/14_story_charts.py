#!/usr/bin/env python3
"""
14_story_charts.py
------------------
Menghasilkan 9 chart visualisasi baru (C1–C9) berbasis data terverifikasi (verified_metrics.json).
Mengikuti design system tim data GRAK:
- Minimalis, bersih, profesional
- Abu-abu netral (#9AA5B1) untuk konteks, aksen (#E4572E) untuk data yang disorot
- Teks navy (#1F2A44), latar putih (#FFFFFF)
- Output format:
  1. 16:9 PNG (untuk slide deck & presentasi)
  2. 4:5 PNG (1080x1350 aspect ratio, untuk feed/carousel tim sosmed)
  3. CSV per chart di charts_data/ agar tim desainer bisa mereproduksi di Figma/Canva
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- DESIGN SYSTEM CONSTANTS ---
FONT_FAMILY = 'sans-serif'
COLOR_ACCENT = '#E4572E'      # Oranye-MerahGRAK
COLOR_ACCENT_LIGHT = '#FBD8CE'
COLOR_NAVY = '#1F2A44'        # Dark Navy
COLOR_GRAY = '#9AA5B1'        # Slate Neutral
COLOR_GRAY_LIGHT = '#E2E8F0'  # Background grid / cards
COLOR_WHITE = '#FFFFFF'
COLOR_SUCCESS = '#2E7D32'     # Green
COLOR_WARNING = '#D97706'     # Amber
COLOR_MUTED = '#64748B'

plt.rcParams['font.sans-serif'] = ['Inter', 'Plus Jakarta Sans', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = FONT_FAMILY
plt.rcParams['text.color'] = COLOR_NAVY
plt.rcParams['axes.labelcolor'] = COLOR_NAVY
plt.rcParams['xtick.color'] = COLOR_NAVY
plt.rcParams['ytick.color'] = COLOR_NAVY


def ensure_dirs(base_dir):
    story_dir = os.path.join(base_dir, 'data', 'processed', 'storytelling')
    png_dir = os.path.join(story_dir, 'charts_png')
    data_dir = os.path.join(story_dir, 'charts_data')
    os.makedirs(png_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    return story_dir, png_dir, data_dir


def load_metrics(story_dir):
    json_path = os.path.join(story_dir, 'verified_metrics.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ==========================================
# C1: FUNNEL PIPELINE METODOLOGI
# ==========================================
def build_c1_funnel(metrics, png_dir, data_dir):
    funnel = metrics['data_funnel']
    stages = [
        ("1. Discovery Artikel", funnel['discovery_articles'], "1.350 artikel ditemukan via Google News & RSS"),
        ("2. Resolusi URL", funnel['resolved_urls'], "1.347 URL aktif (746 percobaan gagal ditangani fallback)"),
        ("3. Ekstraksi Artikel", funnel['articles_extracted'], f"{funnel['articles_extracted']} artikel diekstrak dari {funnel['unique_portals']} media online"),
        ("4. Pembersihan & Dedup", funnel['cleaned_dedup_paragraphs'], "13.840 paragraf bersih setelah dedup teks & boilerplate"),
        ("5. Ingestion Shield", funnel['cleaned_dedup_paragraphs'] - funnel['out_of_domain_rejected'], f"{funnel['out_of_domain_rejected']} paragraf out-of-domain dibuang"),
        ("6. Relevan Domain", funnel['news_relevant_paragraphs'], "6.648 paragraf berita seputar ekosistem bisnis/startup"),
        ("7. Triangulasi 4 Sumber", funnel['total_analyzed_units'], "+311 sosmed, +113 wawancara, +25 survei = 7.097 unit")
    ]
    
    # Save CSV
    df_c1 = pd.DataFrame([{"tahap": s[0], "volume": s[1], "keterangan": s[2]} for s in stages])
    df_c1.to_csv(os.path.join(data_dir, 'c1_funnel_pipeline.csv'), index=False)

    # 16:9 and 4:5 plots
    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(stages))
        vals = [s[1] for s in stages]
        max_val = max(vals)
        
        # Bars
        colors = [COLOR_GRAY if i < 6 else COLOR_ACCENT for i in range(len(stages))]
        bars = ax.barh(y_pos, vals, color=colors, height=0.6, edgecolor='none')
        
        # Labels and values
        ax.set_yticks(y_pos)
        ax.set_yticklabels([s[0] for s in stages], fontsize=11, fontweight='bold', color=COLOR_NAVY)
        ax.invert_yaxis()
        ax.set_xlim(0, max_val * 1.35)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)
        
        for i, (bar, stage) in enumerate(zip(bars, stages)):
            w = bar.get_width()
            val_str = f"{w:,}"
            ax.text(w + (max_val * 0.02), bar.get_y() + bar.get_height()/2, 
                    f"{val_str}  —  {stage[2]}", 
                    va='center', ha='left', fontsize=9.5, color=COLOR_NAVY if i == 6 else COLOR_MUTED,
                    fontweight='bold' if i == 6 else 'normal')
            
        title = "Pipeline Data: Dari 1.350 Berita Mentah hingga 7.097 Unit Triangulasi Terverifikasi"
        subtitle = "Funnel pembersihan data end-to-end melalui Ingestion Shield, deduplikasi, dan integrasi multi-sumber"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 12, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)
        
        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c1_funnel_pipeline_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C2: KONTRAS SENTIMEN NEGATIF PER SUMBER
# ==========================================
def build_c2_sentiment_contrast(metrics, png_dir, data_dir):
    sents = metrics['sentiment_by_source']
    sources = [
        ("Berita Media (N=6.648)", sents['news']['pct']['negative'], sents['news']['counts']['negative'], sents['news']['total']),
        ("Media Sosial (N=311)", sents['social_media']['pct']['negative'], sents['social_media']['counts']['negative'], sents['social_media']['total']),
        ("Wawancara Pelaku (N=113)", sents['interview']['pct']['negative'], sents['interview']['counts']['negative'], sents['interview']['total']),
        ("Teks Survei Founder (N=25)", sents['survey']['pct']['negative'], sents['survey']['counts']['negative'], sents['survey']['total'])
    ]
    
    # Save CSV
    df_c2 = pd.DataFrame([{
        "sumber": s[0],
        "persentase_negatif": s[1],
        "unit_negatif": s[2],
        "total_unit": s[3]
    } for s in sources])
    df_c2.to_csv(os.path.join(data_dir, 'c2_sentiment_contrast.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(sources))
        pcts = [s[1] for s in sources]
        colors = [COLOR_GRAY, COLOR_GRAY, COLOR_ACCENT, COLOR_ACCENT]
        
        bars = ax.barh(y_pos, pcts, color=colors, height=0.55, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels([s[0] for s in sources], fontsize=12, fontweight='bold', color=COLOR_NAVY)
        ax.invert_yaxis()
        ax.set_xlim(0, 85)
        ax.set_xlabel("Persentase Sentimen Negatif / Kritis (%)", fontsize=11, fontweight='bold', color=COLOR_NAVY, labelpad=12)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)
        
        for bar, s in zip(bars, sources):
            w = bar.get_width()
            ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, 
                    f"{w:.1f}% ({s[2]}/{s[3]} unit)", 
                    va='center', ha='left', fontsize=11, fontweight='bold', color=COLOR_NAVY)
            
        title = "Ramai Positif di Media, Kritis di Lapangan: Sentimen Negatif Melonjak 125x Lipat"
        subtitle = "Berita online didominasi narasi netral/seremonial (hanya 0,5% negatif), sementara founder menyuarakan frustrasi nyata (64% negatif)"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 12, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)
        
        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c2_sentiment_contrast_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C3: DOT PLOT LIKERT SCORE FOUNDER
# ==========================================
def build_c3_likert_dotplot(metrics, png_dir, data_dir):
    likert = metrics['survey_metrics']['likert_metrics']
    # Sort by mean
    sorted_items = sorted(likert.items(), key=lambda x: x[1]['mean'])
    
    # Save CSV
    df_c3 = pd.DataFrame([{
        "metrik": v['label'],
        "mean_skor": v['mean'],
        "median_skor": v['median'],
        "std": v['std']
    } for k, v in sorted_items])
    df_c3.to_csv(os.path.join(data_dir, 'c3_likert_dotplot.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(sorted_items))
        means = [item[1]['mean'] for item in sorted_items]
        labels = [item[1]['label'] for item in sorted_items]
        
        # Color mapping: bottom red/accent, middle gray, top green
        colors = []
        for m in means:
            if m < 2.5:
                colors.append(COLOR_ACCENT)
            elif m < 3.5:
                colors.append(COLOR_GRAY)
            else:
                colors.append(COLOR_SUCCESS)
                
        # Neutral reference line at 3.0
        ax.axvline(3.0, color=COLOR_MUTED, linestyle='--', linewidth=1.2, alpha=0.7)
        ax.text(3.05, len(sorted_items)-0.5, 'Ambang Netral (3,0)', color=COLOR_MUTED, fontsize=9.5, style='italic')

        # Dot and line
        ax.hlines(y_pos, xmin=1.0, xmax=means, color=COLOR_GRAY_LIGHT, linewidth=2.5, zorder=1)
        ax.scatter(means, y_pos, color=colors, s=140, zorder=2, edgecolor=COLOR_WHITE, linewidth=1.5)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=11, fontweight='bold', color=COLOR_NAVY)
        ax.set_xlim(1.0, 5.0)
        ax.set_xlabel("Rata-rata Skor Likert (Skala 1 = Sangat Rendah/Sulit, 5 = Sangat Tinggi/Mudah)", 
                      fontsize=10.5, fontweight='bold', color=COLOR_NAVY, labelpad=10)
        ax.xaxis.grid(True, linestyle=':', alpha=0.4, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)

        for y, m in zip(y_pos, means):
            ax.text(m + 0.1, y, f"{m:.2f}", va='center', ha='left', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)

        title = "Founder Percaya pada Diri Sendiri (4,08), Bukan pada Ekosistem (2,58) atau Pendanaan (1,42)"
        subtitle = "Survei Founder Aceh (n=12): Persepsi pendanaan & dukungan pemerintah berada di zona kritis (<2,0)"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)
        
        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c3_likert_dotplot_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C4: RANKING TANTANGAN UTAMA FOUNDER
# ==========================================
def build_c4_challenges_ranking(metrics, png_dir, data_dir):
    challenges = metrics['survey_metrics']['challenges']['top3_overall']
    # Sort top 7
    top_items = sorted(challenges.items(), key=lambda x: x[1], reverse=True)[:7]
    
    # Save CSV
    df_c4 = pd.DataFrame([{"tantangan": k, "jumlah_sebutan_top3": v, "persentase": round(v/12*100, 1)} for k, v in top_items])
    df_c4.to_csv(os.path.join(data_dir, 'c4_challenges_ranking.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(top_items))
        counts = [item[1] for item in top_items]
        labels = [item[0] for item in top_items]
        colors = [COLOR_ACCENT if i == 0 else COLOR_GRAY for i in range(len(top_items))]
        
        bars = ax.barh(y_pos, counts, color=colors, height=0.55, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=11, fontweight='bold', color=COLOR_NAVY)
        ax.invert_yaxis()
        ax.set_xlim(0, 8.5)
        ax.set_xlabel("Frekuensi Disebut dalam Top-3 Tantangan (Total Responden n=12)", 
                      fontsize=10.5, fontweight='bold', color=COLOR_NAVY, labelpad=10)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)

        for bar, count in zip(bars, counts):
            w = bar.get_width()
            pct = round(count / 12 * 100, 1)
            ax.text(w + 0.15, bar.get_y() + bar.get_height()/2, 
                    f"{count} founder ({pct}%)", 
                    va='center', ha='left', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)

        title = "Akses Modal & Talenta Spesifik Mendominasi Titik Sakit Founder Aceh"
        subtitle = "Sebutan Top-3 Tantangan Terbesar: Akses Pendanaan nomor satu (50%), disusul Ketersediaan Talenta (42%)"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)
        
        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c4_challenges_ranking_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C5: WAFFLE / GRID STATUS PENDANAAN & REVENUE
# ==========================================
def build_c5_funding_waffle(metrics, png_dir, data_dir):
    # n=12 founder:
    # 10 Unfunded: 4 Sudah punya revenue, 2 Sudah scaling (total 6 revenue-generating), 3 MVP, 1 Ideation
    # 2 Funded: 1 Revenue, 1 Inactive
    grid_data = [
        {"id": 1, "fund": "Tidak Pernah Didanai", "status": "Sudah punya revenue", "label": "Bootstrap + Revenue"},
        {"id": 2, "fund": "Tidak Pernah Didanai", "status": "Sudah punya revenue", "label": "Bootstrap + Revenue"},
        {"id": 3, "fund": "Tidak Pernah Didanai", "status": "Sudah punya revenue", "label": "Bootstrap + Revenue"},
        {"id": 4, "fund": "Tidak Pernah Didanai", "status": "Sudah punya revenue", "label": "Bootstrap + Revenue"},
        {"id": 5, "fund": "Tidak Pernah Didanai", "status": "Sudah scaling", "label": "Bootstrap + Scaling"},
        {"id": 6, "fund": "Tidak Pernah Didanai", "status": "Sudah scaling", "label": "Bootstrap + Scaling"},
        {"id": 7, "fund": "Tidak Pernah Didanai", "status": "Sudah punya produk/MVP", "label": "Bootstrap + MVP"},
        {"id": 8, "fund": "Tidak Pernah Didanai", "status": "Sudah punya produk/MVP", "label": "Bootstrap + MVP"},
        {"id": 9, "fund": "Tidak Pernah Didanai", "status": "Sudah punya produk/MVP", "label": "Bootstrap + MVP"},
        {"id": 10, "fund": "Tidak Pernah Didanai", "status": "Masih ideation", "label": "Bootstrap + Ideation"},
        {"id": 11, "fund": "Pernah Didanai", "status": "Sudah punya revenue", "label": "Didanai + Revenue"},
        {"id": 12, "fund": "Pernah Didanai", "status": "Sudah tidak aktif", "label": "Didanai + Tidak Aktif"}
    ]
    df_c5 = pd.DataFrame(grid_data)
    df_c5.to_csv(os.path.join(data_dir, 'c5_funding_waffle.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        # Draw 3 rows x 4 cols
        cols = 4
        rows = 3
        
        for idx, item in enumerate(grid_data):
            r = idx // cols
            c = idx % cols
            x = c * 2.6 + 0.5
            y = (rows - 1 - r) * 2.0 + 0.5
            
            # Box color
            if item["fund"] == "Tidak Pernah Didanai":
                if "Revenue" in item["label"] or "Scaling" in item["label"]:
                    box_color = COLOR_ACCENT
                    text_color = COLOR_WHITE
                    badge = "MANDIRI (REVENUE)"
                else:
                    box_color = COLOR_ACCENT_LIGHT
                    text_color = COLOR_NAVY
                    badge = "MANDIRI (PRE-REV)"
            else:
                box_color = COLOR_GRAY_LIGHT
                text_color = COLOR_NAVY
                badge = "PERNAH DIDANAI"

            rect = patches.FancyBboxPatch((x, y), 2.2, 1.5, boxstyle="round,pad=0.15", 
                                          facecolor=box_color, edgecolor='none')
            ax.add_patch(rect)
            
            ax.text(x + 1.1, y + 1.1, f"Founder #{item['id']}", 
                    ha='center', va='center', fontsize=9.5, fontweight='bold', color=text_color)
            ax.text(x + 1.1, y + 0.7, item['status'], 
                    ha='center', va='center', fontsize=8, color=text_color)
            ax.text(x + 1.1, y + 0.35, f"[{badge}]", 
                    ha='center', va='center', fontsize=7.5, fontweight='bold', color=text_color)

        ax.set_xlim(0, 11.5)
        ax.set_ylim(0, 6.8)
        ax.axis('off')

        title = "83% Founder Aceh Bertahan Mandiri Tanpa Pendanaan; 6 di Antaranya Berhasil Cetak Revenue"
        subtitle = "Distribusi Permodalan vs Status Bisnis (n=12): Ketiadaan modal ekuitas tidak membunuh startup, namun memperlambat skala"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)

        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c5_funding_waffle_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C6: EVALUASI PASCA-PROGRAM INKUBASI
# ==========================================
def build_c6_incubation_followup(metrics, png_dir, data_dir):
    followup = metrics['survey_metrics']['incubation']['followup_distribution']
    items = [
        ("Tidak Ada Sama Sekali", followup.get("Tidak ada sama sekali", 4), COLOR_ACCENT),
        ("Ada, tapi Terbatas", followup.get("Ada, tapi terbatas", 1), COLOR_GRAY),
        ("Ada, Berkelanjutan", followup.get("Ada, berkelanjutan", 1), COLOR_SUCCESS)
    ]
    total_valid = sum(item[1] for item in items)
    
    df_c6 = pd.DataFrame([{"tindak_lanjut": item[0], "jumlah": item[1], "persentase": round(item[1]/total_valid*100, 1)} for item in items])
    df_c6.to_csv(os.path.join(data_dir, 'c6_incubation_followup.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(items))
        counts = [item[1] for item in items]
        labels = [item[0] for item in items]
        colors = [item[2] for item in items]
        
        bars = ax.barh(y_pos, counts, color=colors, height=0.5, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=12, fontweight='bold', color=COLOR_NAVY)
        ax.invert_yaxis()
        ax.set_xlim(0, 5.5)
        ax.set_xlabel(f"Jumlah Responden Peserta Program Inkubasi/Dukungan (n={total_valid})", 
                      fontsize=10.5, fontweight='bold', color=COLOR_NAVY, labelpad=10)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)

        for bar, count in zip(bars, counts):
            w = bar.get_width()
            pct = round(count / total_valid * 100, 1)
            ax.text(w + 0.1, bar.get_y() + bar.get_height()/2, 
                    f"{count} responden ({pct}%)", 
                    va='center', ha='left', fontsize=11, fontweight='bold', color=COLOR_NAVY)

        title = "Jurang Pasca-Program: 66,7% Peserta Mengalami Putus Pendampingan Pasca-Kontrak"
        subtitle = "Evaluasi Tindak Lanjut Program: Masalah utama bukan di tahap inkubasi, melainkan ketiadaan jembatan pasca-program"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)

        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c6_incubation_followup_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C7: TOPIK BERITA: UMKM VS R&D
# ==========================================
def build_c7_news_topic_framing(metrics, png_dir, data_dir):
    # From label_stats
    topics = [
        ("Digitalisasi UMKM / Bisnis Konvensional", 1526, 23.0, COLOR_ACCENT),
        ("Pendanaan (Didominasi KUR / Kredit Perbankan)", 1017, 15.3, COLOR_GRAY),
        ("Talenta (Pelatihan Literasi Dasar)", 988, 14.9, COLOR_GRAY),
        ("Regulasi & Kebijakan Pemerintah", 725, 10.9, COLOR_GRAY),
        ("Akses Pasar", 632, 9.5, COLOR_GRAY),
        ("Ekosistem & Komunitas", 432, 6.5, COLOR_GRAY),
        ("Success Story & Profil Bisnis", 354, 5.3, COLOR_GRAY),
        ("Infrastruktur Teknologi & R&D Produk", 159, 2.4, COLOR_ACCENT)
    ]
    df_c7 = pd.DataFrame([{"topik": t[0], "paragraf": t[1], "persentase": t[2]} for t in topics])
    df_c7.to_csv(os.path.join(data_dir, 'c7_news_topic_framing.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        y_pos = np.arange(len(topics))
        pcts = [t[2] for t in topics]
        labels = [t[0] for t in topics]
        colors = [t[3] for t in topics]
        
        bars = ax.barh(y_pos, pcts, color=colors, height=0.6, edgecolor='none')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
        ax.invert_yaxis()
        ax.set_xlim(0, 30)
        ax.set_xlabel("Persentase dari 6.648 Paragraf Berita Relevan (%)", 
                      fontsize=10.5, fontweight='bold', color=COLOR_NAVY, labelpad=10)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRAY)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_GRAY_LIGHT)
        ax.spines['bottom'].set_color(COLOR_GRAY_LIGHT)

        for bar, t in zip(bars, topics):
            w = bar.get_width()
            ax.text(w + 0.4, bar.get_y() + bar.get_height()/2, 
                    f"{w:.1f}% ({t[1]:,} paragraf)", 
                    va='center', ha='left', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)

        title = "Media Membingkai Startup sebagai UMKM: Topik Digitalisasi 10x Lipat Lebih Banyak dari R&D"
        subtitle = "Penyebutan kata UMKM muncul di 330 artikel vs Startup di 77 artikel (Rasio 4,3 : 1). Kebutuhan R&D hanya 2,4%"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)

        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c7_news_topic_framing_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C8: HEATMAP TOPIK X SUMBER NORMALIZED
# ==========================================
def build_c8_topic_heatmap(metrics, png_dir, data_dir):
    topic_dist = metrics['topic_distribution']['normalized_pct']
    # Convert to DataFrame
    df_raw = pd.DataFrame(topic_dist)
    
    # Rename index for display
    source_map = {
        'news': 'Berita Media',
        'social_media': 'Media Sosial',
        'interview': 'Wawancara Pelaku',
        'survey': 'Teks Survei Founder'
    }
    topic_map = {
        'digitalization': 'Digitalisasi',
        'funding': 'Pendanaan',
        'talent': 'Talenta',
        'regulation': 'Regulasi',
        'market_access': 'Akses Pasar',
        'ecosystem': 'Ekosistem',
        'success_story': 'Kisah Sukses',
        'infrastructure': 'Infrastruktur'
    }
    
    df_plot = df_raw.rename(index=source_map, columns=topic_map)
    cols_order = ['Digitalisasi', 'Pendanaan', 'Talenta', 'Regulasi', 'Akses Pasar', 'Ekosistem', 'Kisah Sukses', 'Infrastruktur']
    rows_order = ['Berita Media', 'Media Sosial', 'Wawancara Pelaku', 'Teks Survei Founder']
    df_plot = df_plot.reindex(index=rows_order, columns=cols_order).fillna(0)
    
    # Save CSV
    df_plot.to_csv(os.path.join(data_dir, 'c8_topic_heatmap_normalized.csv'))

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        
        data_matrix = df_plot.values
        im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=35)
        
        ax.set_xticks(np.arange(len(cols_order)))
        ax.set_yticks(np.arange(len(rows_order)))
        ax.set_xticklabels(cols_order, fontsize=10.5, fontweight='bold', color=COLOR_NAVY, rotation=25, ha='right')
        ax.set_yticklabels(rows_order, fontsize=11, fontweight='bold', color=COLOR_NAVY)
        
        # Loop over data dimensions and create text annotations.
        for i in range(len(rows_order)):
            for j in range(len(cols_order)):
                val = data_matrix[i, j]
                text_color = COLOR_WHITE if val > 20 else COLOR_NAVY
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color=text_color, fontweight='bold', fontsize=10)

        cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
        cbar.set_label('Persentase Per Baris Sumber (%)', fontsize=10, fontweight='bold', color=COLOR_NAVY)
        cbar.ax.tick_params(labelsize=9)

        title = "Disparitas Fokus Antar Sumber: Berita Dominan Digitalisasi, Sosmed Soroti Infrastruktur & Talenta"
        subtitle = "Distribusi Topik Dinormalisasi per Sumber (%): Menghilangkan bias dominasi volume berita mentah"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=25, loc='left', color=COLOR_NAVY)

        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c8_topic_heatmap_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


# ==========================================
# C9: MATRIKS KEKUATAN BUKTI 6 INSIGHT
# ==========================================
def build_c9_evidence_matrix(metrics, png_dir, data_dir):
    ev = metrics['evidence_matrix']
    rows = []
    for k, v in ev.items():
        rows.append({
            "insight": k,
            "status_kekuatan": v['strength'],
            "sumber_triangulasi": ", ".join(v['sources']),
            "bukti_kunci": v['key_metric']
        })
    df_c9 = pd.DataFrame(rows)
    df_c9.to_csv(os.path.join(data_dir, 'c9_evidence_matrix.csv'), index=False)

    for mode, (figsize, dpi) in [("16_9", ((12, 6.75), 150)), ("4_5", ((9, 11.25), 150))]:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=COLOR_WHITE)
        ax.set_facecolor(COLOR_WHITE)
        ax.axis('off')

        title = "Matriks Kekuatan Bukti: Landasan Riset Terverifikasi & Jujur Akademik"
        subtitle = "Klasifikasi Triangulasi Kuat / Sedang / Indikatif menggantikan klaim bombastis 'Sempurna 4/4'"
        ax.set_title(f"{title}\n{subtitle}", fontsize=13 if mode == '16_9' else 11.5, 
                     fontweight='bold', pad=20, loc='left', color=COLOR_NAVY)

        y_pos = np.linspace(0.85, 0.08, len(rows))
        
        for idx, (y, r) in enumerate(zip(y_pos, rows)):
            status = r['status_kekuatan']
            if "Kuat" in status:
                badge_bg = '#E8F5E9'
                badge_fg = '#2E7D32'
                border_color = '#A5D6A7'
            elif "Sedang" in status:
                badge_bg = '#FFF3E0'
                badge_fg = '#E65100'
                border_color = '#FFCC80'
            else:
                badge_bg = '#F1F5F9'
                badge_fg = '#64748B'
                border_color = '#CBD5E1'

            # Background card
            card = patches.FancyBboxPatch((0.01, y - 0.045), 0.98, 0.095, 
                                          boxstyle="round,pad=0.01", facecolor=COLOR_WHITE, 
                                          edgecolor=border_color, linewidth=1.2)
            ax.add_patch(card)

            # Badge
            badge_box = patches.FancyBboxPatch((0.03, y - 0.025), 0.16, 0.055,
                                               boxstyle="round,pad=0.008", facecolor=badge_bg,
                                               edgecolor='none')
            ax.add_patch(badge_box)
            ax.text(0.11, y + 0.002, status, ha='center', va='center', 
                    fontsize=8.5, fontweight='bold', color=badge_fg)

            # Insight Title & Evidence
            ax.text(0.21, y + 0.018, r['insight'], fontsize=9.5, fontweight='bold', color=COLOR_NAVY)
            ax.text(0.21, y - 0.022, f"Sumber: {r['sumber_triangulasi']}  |  Bukti: {r['bukti_kunci']}", 
                    fontsize=8, color=COLOR_MUTED)

        plt.tight_layout()
        plt.savefig(os.path.join(png_dir, f'c9_evidence_matrix_{mode}.png'), facecolor=COLOR_WHITE, bbox_inches='tight', pad_inches=0.2)
        plt.close()


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    story_dir, png_dir, data_dir = ensure_dirs(base_dir)
    print("Loading metrics from verified_metrics.json...")
    metrics = load_metrics(story_dir)
    
    print("Generating C1: Funnel Pipeline...")
    build_c1_funnel(metrics, png_dir, data_dir)

    print("Generating C2: Sentiment Contrast...")
    build_c2_sentiment_contrast(metrics, png_dir, data_dir)

    print("Generating C3: Likert Dot Plot...")
    build_c3_likert_dotplot(metrics, png_dir, data_dir)

    print("Generating C4: Challenges Ranking...")
    build_c4_challenges_ranking(metrics, png_dir, data_dir)

    print("Generating C5: Funding Waffle / Grid...")
    build_c5_funding_waffle(metrics, png_dir, data_dir)

    print("Generating C6: Incubation Followup...")
    build_c6_incubation_followup(metrics, png_dir, data_dir)

    print("Generating C7: News Topic Framing...")
    build_c7_news_topic_framing(metrics, png_dir, data_dir)

    print("Generating C8: Topic Heatmap (Normalized)...")
    build_c8_topic_heatmap(metrics, png_dir, data_dir)

    print("Generating C9: Evidence Matrix...")
    build_c9_evidence_matrix(metrics, png_dir, data_dir)

    print(f"All 9 charts generated in {png_dir} (16:9 & 4:5) and {data_dir} (CSV)!")


if __name__ == '__main__':
    main()
