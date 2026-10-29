"""
09_dashboard.py — Premium Interactive HTML Dashboard
GRAK 2026 · Sprint 3
"""

import os
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("⚠️ plotly belum terinstall. Install dengan: pip install plotly")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
DASHBOARD_DIR = os.path.join(PROCESSED_DIR, "dashboard")
INPUT_CSV = os.path.join(PROCESSED_DIR, "combined_text.csv")
TRIANGULATION_CSV = os.path.join(PROCESSED_DIR, "triangulation_matrix.csv")
OUTPUT_HTML = os.path.join(DASHBOARD_DIR, "index.html")

# Premium Color Palette
COLORS = {
    "primary": "#3b82f6",     # Blue
    "secondary": "#8b5cf6",   # Purple
    "success": "#10b981",     # Emerald
    "warning": "#f59e0b",     # Amber
    "danger": "#ef4444",      # Red
    "dark_bg": "rgba(0,0,0,0)",
    "text_main": "#f8fafc",
    "text_muted": "#94a3b8"
}

def style_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["dark_bg"],
        plot_bgcolor=COLORS["dark_bg"],
        font=dict(family="Inter, sans-serif", color=COLORS["text_muted"]),
        title_font=dict(family="Outfit, sans-serif", size=20, color=COLORS["text_main"]),
        margin=dict(t=60, b=40, l=40, r=40),
        hoverlabel=dict(bgcolor="#1e293b", font_size=14, font_family="Inter")
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#334155", zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#334155", zeroline=False)
    return fig

def create_sentiment_cross_chart(df: pd.DataFrame) -> go.Figure:
    if "data_source" not in df.columns: return None
    cross = pd.crosstab(df["data_source"], df["sentiment"], normalize='index') * 100
    fig = go.Figure()
    sent_colors = {"positive": COLORS["success"], "neutral": COLORS["primary"], "negative": COLORS["danger"]}
    for sentiment in ['positive', 'neutral', 'negative']:
        if sentiment in cross.columns:
            fig.add_trace(go.Bar(
                y=cross.index.str.title(),
                x=cross[sentiment],
                name=sentiment.capitalize(),
                orientation='h',
                marker_color=sent_colors.get(sentiment)
            ))
    fig.update_layout(
        title="Cross Analysis: Sentimen per Sumber Data",
        barmode='stack',
        xaxis_title="Persentase (%)",
        yaxis_title="Sumber",
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return style_fig(fig)

def create_topic_chart(df: pd.DataFrame) -> go.Figure:
    topic_counts = df["topic"].value_counts().sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=topic_counts.values,
        y=topic_counts.index,
        orientation="h",
        marker=dict(
            color=topic_counts.values,
            colorscale="Purp",
            line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
        ),
        text=[f"{v} ({v/len(df)*100:.1f}%)" for v in topic_counts.values],
        textposition="outside",
        textfont=dict(color=COLORS["text_main"])
    ))
    fig.update_layout(
        title="Distribusi Topik Dominan",
        xaxis_title="Jumlah Data Point",
        height=350,
        margin=dict(l=150, r=80)
    )
    return style_fig(fig)

def create_heatmap(df: pd.DataFrame) -> go.Figure:
    cross = pd.crosstab(df["topic"], df["sentiment"])
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
    fig = go.Figure(go.Heatmap(
        z=cross_pct.values,
        x=cross_pct.columns.str.capitalize(),
        y=cross_pct.index,
        colorscale="RdBu",
        text=cross.values,
        texttemplate="%{text}",
        textfont=dict(size=14, color="#ffffff"),
        hovertemplate="Topik: %{y}<br>Sentimen: %{x}<br>Jumlah: %{text}<br>Persentase: %{z:.1f}%<extra></extra>",
        showscale=False
    ))
    fig.update_layout(
        title="Heatmap: Topik vs Sentimen",
        height=350,
        margin=dict(l=150)
    )
    return style_fig(fig)

def generate_matrix_table(csv_path: str) -> str:
    if not os.path.exists(csv_path): return "<p>Matrix tidak ditemukan.</p>"
    df_matrix = pd.read_csv(csv_path)
    
    html = '<table class="styled-table">\n'
    html += '<thead><tr><th>ID</th><th>Hipotesis</th><th>Macro (Berita)</th><th>Micro (Survei)</th><th>Wawancara</th><th>Grassroots (Sosmed)</th><th>Konvergensi</th></tr></thead>\n<tbody>\n'
    
    for _, row in df_matrix.iterrows():
        status = row.get("convergence", "")
        badge_class = "status-green" if "SUPPORTED" in status.upper() else "status-red"
        html += f"""
        <tr>
            <td class="id-col">{row.get('hypothesis', '')}</td>
            <td class="hyp-col">
                <strong>{row.get('hypothesis_title', '')}</strong><br>
                <span class="muted">{row.get('hypothesis_claim', '')}</span>
            </td>
            <td>{row.get('scraping_evidence', '')}</td>
            <td>{row.get('survey_evidence', '')}</td>
            <td>{row.get('interview_evidence', '')}</td>
            <td>{row.get('social_media_evidence', '')}</td>
            <td class="status-col"><span class="badge {badge_class}">{status}</span><br><span class="muted">{row.get('strength', '')}</span></td>
        </tr>
        """
    html += "</tbody></table>"
    return html

def map_zone(loc):
    if pd.isna(loc): return None
    loc = str(loc).lower()
    if any(x in loc for x in ['banda aceh', 'aceh besar', 'sabang', 'pidie']):
        return "Zone 1"
    elif any(x in loc for x in ['lhokseumawe', 'aceh utara', 'bireuen']):
        return "Zone 2"
    elif any(x in loc for x in ['meulaboh', 'barat', 'selatan', 'nagan', 'jaya', 'simeulue', 'singkil', 'subulussalam']):
        return "Zone 3"
    elif any(x in loc for x in ['tengah', 'gayo', 'bener meriah', 'timur', 'tamiang', 'langsa']):
        return "Zone 4"
    return None

def generate_regional_html(df: pd.DataFrame) -> str:
    df['zone'] = df['location'].apply(map_zone)
    mapped_df = df.dropna(subset=['zone'])
    total_mapped = len(mapped_df)
    if total_mapped == 0: total_mapped = 1
        
    zones_info = {
        "Zone 1": {"title": "Zone 1: Banda Aceh & Aceh Besar", "desc": "<strong>Episentrum & Hub Kebijakan:</strong> Terkonsentrasi pada ekosistem kampus USK/UIN dan pendanaan hibah. Menjadi pusat komunitas IT dan inisiatif inkubasi pemerintah."},
        "Zone 2": {"title": "Zone 2: Lhokseumawe, Aceh Utara, Bireuen", "desc": "<strong>Anchor Politeknik & Talenta:</strong> Dipimpin oleh Politeknik Negeri Lhokseumawe (PNL) dan Unimal. Fokus diskursus pada ketersediaan talent engineering dan pasar industri."},
        "Zone 3": {"title": "Zone 3: Barat-Selatan (Barsela)", "desc": "<strong>Krisis Utilitas & Blank Spot:</strong> Rasio sentimen negatif infrastruktur tinggi. Pemadaman listrik berkala dan jaringan serat optik putus melumpuhkan aktivitas freelance dan server lokal."},
        "Zone 4": {"title": "Zone 4: Dataran Gayo & Timur-Tenggara", "desc": "<strong>Kluster Komoditas & Agritech:</strong> Topik pasar mendominasi. Kebutuhan digitalisasi berpusat pada keterlacakan rantai pasok (<i>supply chain traceability</i>) komoditas Kopi Arabika Gayo dan Nilam."}
    }
    
    html = ""
    for z in ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]:
        z_df = mapped_df[mapped_df['zone'] == z]
        pct = (len(z_df) / total_mapped) * 100
        
        pos = len(z_df[z_df['sentiment'] == 'positive'])
        neu = len(z_df[z_df['sentiment'] == 'neutral'])
        neg = len(z_df[z_df['sentiment'] == 'negative'])
        
        neg_class = "danger" if neg > pos else ""
        
        html += f'''
        <div class="region-card">
            <div class="region-card-header">
                <div class="region-title">{zones_info[z]["title"]}</div>
                <div class="region-pct">{pct:.1f}% Korpus</div>
            </div>
            <div class="region-stats">
                <span>Positif: {pos}</span> &middot; <span>Netral: {neu}</span> &middot; <span class="{neg_class}">Negatif: {neg}</span>
            </div>
            <div class="region-desc">
                {zones_info[z]["desc"]}
            </div>
        </div>
        '''
    return html

def generate_premium_html(df: pd.DataFrame) -> str:
    charts = [
        ("cross", create_sentiment_cross_chart(df)),
        ("topic", create_topic_chart(df)),
        ("heatmap", create_heatmap(df))
    ]
    
    chart_divs = ""
    for i, (name, fig) in enumerate(charts):
        if fig:
            div_id = f"chart_{name}"
            chart_html = fig.to_html(full_html=False, include_plotlyjs=(i==0), div_id=div_id, config={'displayModeBar': False})
            chart_divs += f'<div class="glass-panel chart-box">{chart_html}</div>\n'

    total_rows = f"{len(df):,}"
    matrix_html = generate_matrix_table(TRIANGULATION_CSV)
    regional_html = generate_regional_html(df)
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRAK 2026 | Ecosystem Intelligence Portal</title>
    <!-- Premium Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-color: #0B0F19;
            --panel-bg: rgba(26, 34, 53, 0.6);
            --panel-border: rgba(255, 255, 255, 0.08);
            --accent-1: #3b82f6;
            --accent-2: #8b5cf6;
            --accent-green: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif; background-color: var(--bg-color);
            background-image: radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                              radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            background-attachment: fixed; color: var(--text-main); line-height: 1.6; min-height: 100vh;
        }}
        .container {{ max-width: 1440px; margin: 0 auto; padding: 40px 24px; }}
        h1, h2, h3 {{ font-family: 'Outfit', sans-serif; }}
        .header {{ text-align: center; margin-bottom: 60px; animation: fadeInDown 0.8s ease-out; }}
        .header h1 {{
            font-size: 3.5rem; font-weight: 800;
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2), #ec4899);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 16px; letter-spacing: -1px;
        }}
        .header p {{ font-size: 1.2rem; color: var(--text-muted); max-width: 600px; margin: 0 auto; }}
        
        .glass-panel {{
            background: var(--panel-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--panel-border); border-radius: 20px; padding: 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        /* Stats */
        .stats-row {{ display: flex; justify-content: center; gap: 24px; margin-bottom: 40px; flex-wrap: wrap; }}
        .stat-badge {{
            background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 12px 24px; border-radius: 50px; display: flex; align-items: center; gap: 12px;
            color: var(--accent-1); font-weight: 600; font-family: 'Outfit', sans-serif; font-size: 1.1rem;
        }}
        .stat-badge span {{ color: #fff; }}
        
        /* Dashboard Layout */
        .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 40px; }}
        .chart-box {{ padding: 20px; }}
        .chart-box:hover {{ transform: translateY(-5px); border-color: rgba(255,255,255,0.2); }}
        
        /* Matrix Section */
        .matrix-section {{ margin-top: 60px; margin-bottom: 60px; }}
        .section-title {{ font-size: 2rem; margin-bottom: 30px; display: flex; align-items: center; gap: 12px; }}
        .section-title::before {{ content: ''; width: 8px; height: 32px; background: linear-gradient(to bottom, var(--accent-1), var(--accent-2)); border-radius: 4px; }}
        
        .styled-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        .styled-table th, .styled-table td {{ padding: 16px; text-align: left; border-bottom: 1px solid var(--panel-border); }}
        .styled-table th {{ font-family: 'Outfit', sans-serif; font-weight: 600; color: #fff; background: rgba(0,0,0,0.2); }}
        .styled-table tr:hover {{ background: rgba(255,255,255,0.02); }}
        .styled-table .id-col {{ font-weight: bold; color: var(--accent-1); font-size: 1.1rem; text-align: center; }}
        .styled-table .hyp-col {{ min-width: 200px; }}
        .styled-table .muted {{ color: var(--text-muted); font-size: 0.85em; display: block; margin-top: 4px; }}
        .styled-table .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; display: inline-block; }}
        .status-green {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.4); }}
        .status-red {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .styled-table td {{ vertical-align: top; }}
        
        /* Insight Section (5-Layer) */
        .insight-grid {{ display: grid; grid-template-columns: 1fr; gap: 24px; }}
        .insight-card {{ position: relative; overflow: hidden; }}
        .insight-card::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, var(--accent-1), var(--accent-2)); opacity: 0; transition: opacity 0.3s ease;
        }}
        .insight-card:hover::before {{ opacity: 1; }}
        .insight-number {{
            font-family: 'Outfit', sans-serif; font-size: 4rem; font-weight: 800;
            color: rgba(255,255,255,0.03); position: absolute; top: -10px; right: 10px; line-height: 1;
        }}
        .insight-card h3 {{ font-size: 1.4rem; color: #fff; margin-bottom: 16px; padding-right: 40px; }}
        
        .layer {{ margin-bottom: 12px; }}
        .layer-title {{ display: inline-block; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--accent-1); margin-right: 8px; width: 120px; }}
        .layer-content {{ font-size: 0.95rem; color: var(--text-muted); display: inline; }}
        
        .layer-insight {{ 
            margin-top: 16px; background: rgba(255,255,255,0.03); padding: 16px; border-left: 3px solid var(--accent-2); border-radius: 4px;
        }}
        .layer-insight .layer-title {{ color: var(--accent-2); display: block; margin-bottom: 8px; width: auto; }}
        .layer-insight .layer-content {{ color: #e2e8f0; font-weight: 500; font-size: 1.05rem; display: block; }}
        
        /* Regional Section */
        .regional-header {{ margin-bottom: 24px; }}
        .regional-badges {{ display: flex; gap: 12px; margin-bottom: 16px; }}
        .regional-badge {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; color: var(--accent-1); text-transform: uppercase; letter-spacing: 1px; }}
        .regional-badge.green {{ color: var(--accent-green); }}
        .regional-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 60px; }}
        .region-card {{ background: #11141D; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 24px; transition: transform 0.2s ease; }}
        .region-card:hover {{ transform: translateY(-2px); border-color: rgba(255,255,255,0.1); }}
        .region-card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        .region-title {{ font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 600; color: #fff; }}
        .region-pct {{ font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 600; color: var(--accent-green); }}
        .region-stats {{ display: flex; gap: 16px; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px; font-weight: 500; }}
        .region-stats span.danger {{ color: #ef4444; }}
        .region-desc {{ font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; }}
        .region-desc strong {{ color: #e2e8f0; }}
        
        @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .fade-in {{ animation: fadeIn 1s ease-out forwards; }}
        @media (max-width: 1024px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Ecosystem Intelligence</h1>
            <p>GRAK 2026 Sprint 3 • Triangulation Results & Core Insights</p>
        </header>
        
        <div class="stats-row fade-in">
            <div class="stat-badge">Data Analyzed <span>{total_rows} rows</span></div>
            <div class="stat-badge" style="color: var(--accent-2); border-color: rgba(139, 92, 246, 0.2); background: rgba(139, 92, 246, 0.1);">
                Sources <span>4 (Triangulated)</span>
            </div>
            <div class="stat-badge" style="color: var(--accent-green); border-color: rgba(16, 185, 129, 0.2); background: rgba(16, 185, 129, 0.1);">
                Confidence <span>Extremely High (Supported)</span>
            </div>
        </div>
        
        <div class="dashboard-grid fade-in" style="animation-delay: 0.2s;">
            {chart_divs}
        </div>
        
        <div class="matrix-section fade-in" style="animation-delay: 0.3s;">
            <h2 class="section-title">Matriks Triangulasi 4-Pilar</h2>
            <div class="glass-panel" style="padding: 0; overflow-x: auto;">
                {matrix_html}
            </div>
        </div>
        
        <div class="regional-section fade-in" style="animation-delay: 0.35s;">
            <div class="regional-header">
                <div class="regional-badges">
                    <span class="regional-badge">Regional Intelligence</span>
                    <span class="regional-badge green">4 Geographic Zones</span>
                </div>
                <h2 style="font-size: 2.2rem; margin-bottom: 8px;">Pemetaan Lintas Wilayah (Cross-Regional Analysis)</h2>
                <p style="color: var(--text-muted); margin-bottom: 30px;">Eksplorasi disparitas spasial ekosistem teknologi di seluruh penjuru Provinsi Aceh.</p>
            </div>
            
            <div class="regional-grid">
                {regional_html}
            </div>
        </div>
        
        <div class="insights-section fade-in" style="animation-delay: 0.4s;">
            <h2 class="section-title">6 Grand Insights (5-Layer Format)</h2>
            <div class="insight-grid">
                
                <div class="glass-panel insight-card">
                    <div class="insight-number">01</div>
                    <h3>Euforia Seremonial vs Realitas Lapangan</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">Sentimen berita publik didominasi narasi netral-optimis (86,5%), sementara data pelaku menunjukkan realitas sebaliknya (64,0% negatif di survei, 42,5% negatif di wawancara).</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Ada kontradiksi tajam; narasi media berfokus pada perayaan acara pembukaan/inkubasi startup, sementara suara akar rumput dipenuhi keluhan tentang eksekusi operasional di lapangan.</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Dukungan ekosistem sejauh ini (event, program pemerintah/kampus) berhasil menciptakan <i>hype</i> di media, namun gagal menyentuh masalah mendasar karena program seringkali selesai setelah foto bersama, tanpa pendampingan nyata.</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Dukungan ekosistem di Aceh masih terjebak pada "euforia seremonial" dan belum bertransisi menjadi pendampingan bisnis (follow-up) berkelanjutan yang memecahkan masalah riil startup.</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Silang sentimen Makro (Berita) vs Mikro (Survei/Wawancara) + Matriks Triangulasi H4.</div></div>
                </div>

                <div class="glass-panel insight-card">
                    <div class="insight-number">02</div>
                    <h3>Paradoks SDM dan "Remote Arbitrage"</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">41,7% responden survei memilih talent sebagai kendala utama, didukung oleh 44 unit percakapan di sosmed (Grassroots) tentang bekerja remote ke luar daerah.</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Startup lokal kesulitan mencari Software Engineer, bukan karena kampus gagal mencetak lulusan IT, tapi karena lulusan terbaik tersedot keluar daerah (Brain Drain).</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Startup lokal yang ber-budget minim tidak mampu bersaing secara gaji dengan perusahaan Jakarta/Global yang merekrut talenta Aceh secara WFA (Work From Anywhere).</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Krisis talenta digital di Aceh bukanlah masalah kekurangan produksi lulusan, melainkan ketidakmampuan startup lokal menahan (retain) mereka dari godaan gaji remote work nasional.</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Wawancara SuratPlus/Bepal + Analisis Grassroots Media Sosial + Survei Primer (H2).</div></div>
                </div>
                
                <div class="glass-panel insight-card">
                    <div class="insight-number">03</div>
                    <h3>Ketergantungan Absolut di Luar Ibu Kota</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">100% founder luar Banda Aceh di survei lahir dari program kampus. Pemberitaan dari Lhokseumawe/Langsa terpusat pada event perguruan tinggi (Unimal/PNL).</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Di luar Banda Aceh, ketiadaan fasilitas pendukung mandiri (Coworking Space) dan investor swasta menjadikan kampus sebagai satu-satunya pilar penopang.</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Kehidupan startup di wilayah kabupaten sangat rapuh karena bergantung sepenuhnya pada alokasi anggaran dan siklus birokrasi riset dosen/kampus.</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Ekosistem startup di luar Banda Aceh belum memiliki kemandirian pasar; hidup-matinya sebuah startup masih disetir secara absolut oleh agenda perguruan tinggi lokal.</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Wawancara PST (Lhokseumawe) + Klasterisasi Topik Berita Luar Banda Aceh (H3).</div></div>
                </div>

                <div class="glass-panel insight-card">
                    <div class="insight-number">04</div>
                    <h3>Jebakan "Pemburu Hadiah Lomba"</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">50% responden survei memberi skor sangat rendah untuk ketersediaan dana (mean 1.42 dari 5). Percakapan sosmed (45 unit) mengeluhkan ketiadaan Angel Investor atau VC lokal.</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Ketiadaan investor swasta lokal (smart money) membuat founder pemula di Aceh hanya bisa mengandalkan satu pintu pendanaan: Hibah kompetisi pemerintah atau kampus.</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Tanpa akses ke modal swasta untuk melakukan scale-up, founder terpaksa terus-menerus merombak ide (pitching) hanya untuk memenangkan hadiah uang tunai kompetisi berikutnya demi bertahan hidup.</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Absennya Venture Capital lokal menjebak startup pemula dalam siklus "Grant-Seeking" (pemburu hadiah lomba), yang mematikan fokus mereka pada pengembangan produk jangka panjang.</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Topik Makro (Berita) + Survei + Percakapan Twitter/Grassroots (H1).</div></div>
                </div>

                <div class="glass-panel insight-card">
                    <div class="insight-number">05</div>
                    <h3>Limitasi B2C dan Ilusi Pasar Lokal</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">34 unit ide dari Wawancara mengeluhkan pasar lokal yang "inginnya serba gratis/murah". Sebaliknya, kemudahan akses ke pasar luar Aceh dinilai cukup tinggi (3.75) di survei.</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Pasar konsumen (B2C) di Aceh sangat terbatas secara demografi daya beli (terkonsentrasi pada ASN) dan masih butuh diedukasi tentang layanan digital berbayar.</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Startup yang bersikeras melayani pasar retail lokal akan cepat kehabisan uang (burn rate). Mereka harus mengubah target ke segmen korporasi/pemerintah atau membidik luar wilayah.</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Sempitnya daya beli B2C lokal memaksa startup Aceh untuk segera memilih: beralih menjadi vendor B2B (pemerintah/kampus) atau langsung melakukan ekspansi pasar nasional agar bisa sustain.</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Wawancara SuratPlus/PST + Tren Sentimen Pasar di Sosmed (H5).</div></div>
                </div>

                <div class="glass-panel insight-card">
                    <div class="insight-number">06</div>
                    <h3>Ketimpangan "Seller vs Builder"</h3>
                    <div class="layer"><span class="layer-title">DATA:</span><div class="layer-content">Analisis berita didominasi klaster "Digitalisasi UMKM" (22.3%). Survei mencatat 0% responden menerima dukungan berupa fasilitas prototyping/R&D teknologi mendalam.</div></div>
                    <div class="layer"><span class="layer-title">PATTERN:</span><div class="layer-content">Kebijakan pemerintah dan inkubator sangat berat sebelah; berfokus pada "bagaimana cara berjualan online" (Marketing/Canva), tapi mengabaikan "bagaimana merakit teknologinya" (Engineering).</div></div>
                    <div class="layer"><span class="layer-title">INTERPRETATION:</span><div class="layer-content">Terjadi kesenjangan besar. Ekosistem secara keliru memperlakukan startup tech seolah-olah sama dengan UMKM kuliner/kriya, sehingga inovasi yang berbasis teknologi mendalam (deep-tech) mati kehabisan oksigen.</div></div>
                    <div class="layer layer-insight"><span class="layer-title">INSIGHT:</span><div class="layer-content">Dukungan ekosistem yang menyamaratakan Startup dengan UMKM konvensional telah menciptakan surplus pelatih Digital Marketing, namun mewariskan defisit kritis pada dukungan Rekayasa Produk (R&D).</div></div>
                    <div class="layer" style="margin-top: 16px;"><span class="layer-title">EVIDENCE:</span><div class="layer-content">Analisis Topik Scraping Berita (Makro) + Survei Profil Dukungan + Wawancara (H6).</div></div>
                </div>
                
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    if not HAS_PLOTLY: return
    df = pd.read_csv(INPUT_CSV)
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(generate_premium_html(df))
        
if __name__ == "__main__":
    main()
