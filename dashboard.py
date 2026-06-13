# =============================================================================
# DASHBOARD KUALITAS UDARA JAKARTA (ISPU) - 5 DASHBOARD BISNIS INTELIJEN
# =============================================================================
# Cara menjalankan:
#   1. pip install streamlit plotly pandas numpy
#   2. streamlit run ispu_jakarta_dashboard.py
#   3. Pastikan file CSV ada di path yang sama, atau ubah DATA_PATH di bawah.
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# KONFIGURASI GLOBAL
# ──────────────────────────────────────────────────────────────────────────────
DATA_PATH = "ispu_jakarta_cleaned_final.csv"   # sesuaikan jika perlu

CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_COLORS = {
    "BAIK":               "#2ECC71",
    "SEDANG":             "#F1C40F",
    "TIDAK SEHAT":        "#E67E22",
    "SANGAT TIDAK SEHAT": "#E74C3C",
    "BERBAHAYA":          "#8E44AD",
}
POLLUTANT_COLORS = {
    "PM10":  "#E74C3C",
    "PM2.5": "#E67E22",
    "O3":    "#3498DB",
    "CO":    "#95A5A6",
    "SO2":   "#F39C12",
    "NO2":   "#9B59B6",
}
STATION_COLORS = {
    "DKI1 Bunderan HI":   "#1ABC9C",
    "DKI2 Kelapa Gading": "#E74C3C",
    "DKI3 Jagakarsa":     "#3498DB",
    "DKI4 Lubang Buaya":  "#E67E22",
    "DKI5 Kebon Jeruk":   "#9B59B6",
}
MONTH_ID = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
            7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}

# ──────────────────────────────────────────────────────────────────────────────
# LOAD & CLEAN DATA
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["tanggal"]  = pd.to_datetime(df["tanggal"])
    df["critical"] = df["critical"].replace("PM25", "PM2.5")
    df["year"]     = df["tanggal"].dt.year
    df["month"]    = df["tanggal"].dt.month
    df["month_name"] = df["month"].map(MONTH_ID)
    df["dayofweek"]  = df["tanggal"].dt.dayofweek
    df["day_type"]   = df["dayofweek"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    df["quarter"]    = df["tanggal"].dt.quarter
    df["is_unhealthy"] = df["categori"].isin(
        ["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
    )
    # stasiun singkat
    df["stasiun_short"] = df["stasiun"].str.extract(r"(DKI\d)")
    return df

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def metric_card(label, value, delta=None, delta_label="", color="#1ABC9C"):
    delta_html = ""
    if delta is not None:
        sign  = "▲" if delta >= 0 else "▼"
        dcolor = "#E74C3C" if delta >= 0 else "#2ECC71"
        delta_html = f'<div style="font-size:12px;color:{dcolor};">{sign} {abs(delta):.1f} {delta_label}</div>'
    return f"""
    <div style="background:#1E1E2E;border-left:4px solid {color};border-radius:8px;
                padding:14px 18px;margin:4px;">
        <div style="font-size:12px;color:#aaa;text-transform:uppercase;letter-spacing:1px;">{label}</div>
        <div style="font-size:28px;font-weight:700;color:#fff;margin:4px 0;">{value}</div>
        {delta_html}
    </div>"""

def section_header(title, subtitle=""):
    sub = f'<div style="color:#aaa;font-size:13px;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="border-bottom:2px solid #3498DB;margin:20px 0 12px 0;padding-bottom:6px;">
        <span style="font-size:18px;font-weight:700;color:#ECF0F1;">{title}</span>
        {sub}
    </div>""", unsafe_allow_html=True)

def insight_box(text, icon="💡", color="#2C3E50"):
    st.markdown(f"""
    <div style="background:{color};border-left:4px solid #3498DB;border-radius:6px;
                padding:14px 18px;margin:10px 0;font-size:13.5px;line-height:1.7;color:#ECF0F1;">
        <b>{icon} Analisis & Insight</b><br>{text}
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Kualitas Udara Jakarta",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0F0F1A; }
    [data-testid="stSidebar"]          { background-color: #13131F; }
    h1,h2,h3,h4,h5,h6,p,div,span,label { color: #ECF0F1 !important; }
    .stSelectbox>div>div, .stMultiSelect>div>div { background:#1E1E2E !important; color:#ECF0F1 !important; }
    .stSlider>div { color:#ECF0F1 !important; }
    .block-container { padding-top:1rem; padding-bottom:1rem; }
    div[data-testid="metric-container"] {
        background:#1E1E2E; border-radius:8px; padding:10px; border-left:3px solid #3498DB;
    }
    .stTabs [data-baseweb="tab"] { color:#ECF0F1 !important; background:#1E1E2E !important; }
    .stTabs [aria-selected="true"] { border-bottom:2px solid #3498DB !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    df = load_data()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGASI
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:10px 0 20px;'>
    <div style='font-size:32px;'>🌫️</div>
    <div style='font-size:16px;font-weight:700;color:#3498DB;'>Dashboard ISPU Jakarta</div>
    <div style='font-size:11px;color:#888;'>Indeks Standar Pencemar Udara<br>2010 – 2023</div>
</div>
""", unsafe_allow_html=True)

dashboard = st.sidebar.radio(
    "Pilih Dashboard",
    [
        "📊 Dashboard 1: Overview Kualitas Udara",
        "📈 Dashboard 2: Tren Temporal",
        "🗺️ Dashboard 3: Perbandingan Antar Stasiun",
        "🔬 Dashboard 4: Analisis Pencemar Kritis",
        "🌡️ Dashboard 5: Pola Musiman",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='font-size:11px;color:#888;'>
    📅 Periode: Jan 2010 – Nov 2023<br>
    📍 Stasiun: 5 SPKU DKI Jakarta<br>
    📋 Total data: {len(df):,} observasi
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DASHBOARD 1: OVERVIEW KUALITAS UDARA JAKARTA
# ==============================================================================
if "Dashboard 1" in dashboard:
    st.markdown("""
    <h1 style='margin-bottom:4px;'>📊 Overview Kualitas Udara Jakarta</h1>
    <p style='color:#888;font-size:13px;'>Gambaran menyeluruh kualitas udara Jakarta berdasarkan data ISPU 2010–2023</p>
    """, unsafe_allow_html=True)

    # ── FILTER ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Filter Dashboard 1")
        year_range = st.slider(
            "Rentang Tahun", 2010, 2023, (2010, 2023), key="d1_yr"
        )
        stations_d1 = st.multiselect(
            "Pilih Stasiun", df["stasiun"].unique().tolist(),
            default=df["stasiun"].unique().tolist(), key="d1_st"
        )

    d1 = df[
        (df["year"].between(year_range[0], year_range[1])) &
        (df["stasiun"].isin(stations_d1))
    ]

    # ── KPI CARDS ────────────────────────────────────────────────────────────
    section_header("🔑 Key Performance Indicators")

    avg_ispu       = d1["max"].mean()
    pct_unhealthy  = d1["is_unhealthy"].mean() * 100
    dominant_poll  = d1["critical"].value_counts().idxmax()
    total_days     = len(d1)
    pct_good       = (d1["categori"] == "BAIK").mean() * 100

    cols = st.columns(5)
    kpis = [
        ("Rata-rata ISPU",     f"{avg_ispu:.1f}",       "#3498DB"),
        ("% Hari Tidak Sehat", f"{pct_unhealthy:.1f}%", "#E74C3C"),
        ("Pencemar Dominan",   dominant_poll,            "#E67E22"),
        ("Total Observasi",    f"{total_days:,}",        "#9B59B6"),
        ("% Hari Baik",        f"{pct_good:.1f}%",      "#2ECC71"),
    ]
    for col, (lbl, val, col_code) in zip(cols, kpis):
        with col:
            st.markdown(metric_card(lbl, val, color=col_code), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DISTRIBUSI KATEGORI ──────────────────────────────────────────────────
    section_header("📊 Distribusi Kategori ISPU", "Komposisi hari berdasarkan kategori kualitas udara")
    col1, col2 = st.columns([1, 1])

    with col1:
        cat_counts = (
            d1["categori"]
            .value_counts()
            .reindex(CATEGORY_ORDER)
            .dropna()
            .reset_index()
        )
        cat_counts.columns = ["Kategori", "Jumlah"]
        cat_counts["Persen"] = (cat_counts["Jumlah"] / cat_counts["Jumlah"].sum() * 100).round(1)

        fig_pie = px.pie(
            cat_counts, names="Kategori", values="Jumlah",
            color="Kategori",
            color_discrete_map=CATEGORY_COLORS,
            hole=0.45,
            title="Proporsi Kategori Kualitas Udara",
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar_cat = px.bar(
            cat_counts, x="Kategori", y="Persen",
            color="Kategori", color_discrete_map=CATEGORY_COLORS,
            text="Persen",
            title="Persentase Hari per Kategori",
            labels={"Persen": "Persentase (%)"},
        )
        fig_bar_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=False,
            xaxis=dict(categoryorder="array", categoryarray=CATEGORY_ORDER)
        )
        st.plotly_chart(fig_bar_cat, use_container_width=True)

    # ── PENCEMAR DOMINAN ─────────────────────────────────────────────────────
    section_header("🏭 Pencemar Paling Dominan", "Frekuensi kemunculan setiap polutan sebagai pencemar kritis")
    col3, col4 = st.columns([1, 1])

    with col3:
        poll_counts = d1["critical"].value_counts().reset_index()
        poll_counts.columns = ["Polutan", "Frekuensi"]
        poll_counts["Persen"] = (poll_counts["Frekuensi"] / poll_counts["Frekuensi"].sum() * 100).round(1)

        fig_poll = px.bar(
            poll_counts, x="Frekuensi", y="Polutan", orientation="h",
            color="Polutan", color_discrete_map=POLLUTANT_COLORS,
            text="Persen",
            title="Frekuensi Pencemar Kritis",
        )
        fig_poll.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_poll.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=False,
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig_poll, use_container_width=True)

    with col4:
        # Weekday vs Weekend
        wkd = d1.groupby("day_type")["max"].agg(["mean", "median", "std"]).reset_index()
        wkd.columns = ["Tipe Hari", "Rata-rata", "Median", "Std Dev"]
        fig_wkd = go.Figure()
        colors_wkd = {"Weekday": "#3498DB", "Weekend": "#E67E22"}
        for _, row in wkd.iterrows():
            fig_wkd.add_trace(go.Bar(
                name=row["Tipe Hari"],
                x=[row["Tipe Hari"]],
                y=[row["Rata-rata"]],
                error_y=dict(type="data", array=[row["Std Dev"]], visible=True),
                marker_color=colors_wkd[row["Tipe Hari"]],
                text=f"{row['Rata-rata']:.1f}",
                textposition="outside",
            ))
        fig_wkd.update_layout(
            title="Perbandingan ISPU: Weekday vs Weekend",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=True, barmode="group",
            yaxis_title="Rata-rata ISPU (max)",
        )
        st.plotly_chart(fig_wkd, use_container_width=True)

    # ── RINGKASAN PER STASIUN ─────────────────────────────────────────────────
    section_header("📍 Kondisi Terkini per Stasiun SPKU")
    station_summary = d1.groupby("stasiun").agg(
        avg_ispu=("max", "mean"),
        median_ispu=("max", "median"),
        pct_unhealthy=("is_unhealthy", lambda x: x.mean() * 100),
        dominant=("critical", lambda x: x.value_counts().idxmax()),
    ).reset_index().round(1)
    station_summary.columns = ["Stasiun", "Rata-rata ISPU", "Median ISPU",
                                "% Tidak Sehat", "Pencemar Dominan"]

    fig_station = px.bar(
        station_summary, x="Stasiun", y="Rata-rata ISPU",
        color="Stasiun", color_discrete_map=STATION_COLORS,
        text="Rata-rata ISPU",
        title="Rata-rata ISPU per Stasiun",
        hover_data=["Median ISPU", "% Tidak Sehat", "Pencemar Dominan"],
    )
    fig_station.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_station.add_hline(y=50, line_dash="dash", line_color="#F1C40F",
                          annotation_text="Batas Sedang (50)")
    fig_station.add_hline(y=100, line_dash="dash", line_color="#E74C3C",
                          annotation_text="Batas Tidak Sehat (100)")
    fig_station.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1", showlegend=False,
    )
    st.plotly_chart(fig_station, use_container_width=True)

    with st.expander("📋 Tabel Ringkasan per Stasiun"):
        st.dataframe(station_summary.set_index("Stasiun"), use_container_width=True)

    # ── INSIGHT ───────────────────────────────────────────────────────────────
    insight_box(
        f"""
        <b>Kondisi Umum:</b> Rata-rata ISPU Jakarta sebesar <b>{avg_ispu:.1f}</b> berada di kategori
        <b>SEDANG</b>, namun <b>{pct_unhealthy:.1f}%</b> hari tercatat dalam kategori Tidak Sehat atau lebih buruk —
        setara dengan ±{int(pct_unhealthy/100 * total_days):,} hari dari {total_days:,} observasi.
        Hanya <b>{pct_good:.1f}%</b> hari yang memiliki kualitas BAIK.<br><br>
        <b>Pencemar Utama:</b> <b>{dominant_poll}</b> mendominasi sebagai pencemar kritis, yang erat kaitannya
        dengan emisi kendaraan bermotor dan aktivitas industri di Jakarta.<br><br>
        <b>Weekday vs Weekend:</b> Perbedaan ISPU antara hari kerja ({d1[d1['day_type']=='Weekday']['max'].mean():.1f})
        dan akhir pekan ({d1[d1['day_type']=='Weekend']['max'].mean():.1f}) relatif kecil, mengindikasikan bahwa
        sumber pencemar bukan hanya berasal dari aktivitas kerja/bisnis, tetapi juga transportasi dan industri
        yang beroperasi sepanjang minggu.<br><br>
        <b>Implikasi Kebijakan:</b> Fokus pengendalian emisi perlu diarahkan pada sumber <b>{dominant_poll}</b>
        — terutama pembatasan kendaraan berbahan bakar kotor dan peningkatan standar emisi industri.
        Stasiun <b>DKI4 Lubang Buaya</b> dan <b>DKI2 Kelapa Gading</b> memerlukan perhatian prioritas.
        """,
        icon="🏙️"
    )


# ==============================================================================
# DASHBOARD 2: TREN TEMPORAL KUALITAS UDARA
# ==============================================================================
elif "Dashboard 2" in dashboard:
    st.markdown("""
    <h1 style='margin-bottom:4px;'>📈 Tren Temporal Kualitas Udara</h1>
    <p style='color:#888;font-size:13px;'>Analisis tren nilai ISPU dari waktu ke waktu dengan berbagai granularitas</p>
    """, unsafe_allow_html=True)

    # ── FILTER ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Filter Dashboard 2")
        granularity = st.selectbox(
            "Granularitas Waktu",
            ["Harian", "Bulanan", "Tahunan"],
            key="d2_gran",
        )
        stations_d2 = st.multiselect(
            "Pilih Stasiun",
            df["stasiun"].unique().tolist(),
            default=df["stasiun"].unique().tolist(),
            key="d2_st",
        )
        year_range2 = st.slider(
            "Rentang Tahun", 2010, 2023, (2010, 2023), key="d2_yr"
        )

    d2 = df[
        (df["year"].between(year_range2[0], year_range2[1])) &
        (df["stasiun"].isin(stations_d2))
    ]

    # ── TREN UTAMA ────────────────────────────────────────────────────────────
    section_header("📊 Tren ISPU Berdasarkan Waktu", f"Granularitas: {granularity}")

    if granularity == "Harian":
        trend_df = d2.groupby(["tanggal", "stasiun"])["max"].mean().reset_index()
        x_col = "tanggal"
        title_suffix = "Harian"
        # rolling mean 30 hari
        overall_daily = d2.groupby("tanggal")["max"].mean().reset_index()
        overall_daily["rolling30"] = overall_daily["max"].rolling(30, min_periods=1).mean()

    elif granularity == "Bulanan":
        d2["yearmonth"] = d2["tanggal"].dt.to_period("M").dt.to_timestamp()
        trend_df = d2.groupby(["yearmonth", "stasiun"])["max"].mean().reset_index()
        x_col = "yearmonth"
        overall_daily = d2.groupby("yearmonth")["max"].mean().reset_index()
        overall_daily.columns = ["tanggal", "max"]
        overall_daily["rolling30"] = overall_daily["max"].rolling(3, min_periods=1).mean()
        title_suffix = "Bulanan"

    else:  # Tahunan
        trend_df = d2.groupby(["year", "stasiun"])["max"].mean().reset_index()
        x_col = "year"
        overall_daily = d2.groupby("year")["max"].mean().reset_index()
        overall_daily.columns = ["tanggal", "max"]
        overall_daily["rolling30"] = overall_daily["max"]
        title_suffix = "Tahunan"

    fig_trend = go.Figure()
    for station in stations_d2:
        s_df = trend_df[trend_df["stasiun"] == station]
        fig_trend.add_trace(go.Scatter(
            x=s_df[x_col], y=s_df["max"],
            mode="lines",
            name=station,
            line=dict(color=STATION_COLORS.get(station, "#aaa"), width=1.5),
            opacity=0.75,
        ))

    # overall average
    fig_trend.add_trace(go.Scatter(
        x=overall_daily["tanggal"], y=overall_daily["rolling30"],
        mode="lines",
        name="Rata-rata Semua Stasiun",
        line=dict(color="white", width=2.5, dash="dot"),
    ))

    # threshold lines
    fig_trend.add_hline(y=100, line_dash="dash", line_color="#E74C3C",
                        annotation_text="Tidak Sehat (100)")
    fig_trend.add_hline(y=50, line_dash="dash", line_color="#F1C40F",
                        annotation_text="Sedang (50)", annotation_position="bottom right")

    fig_trend.update_layout(
        title=f"Tren ISPU {title_suffix} per Stasiun",
        xaxis_title="Waktu", yaxis_title="Nilai ISPU (max)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="#333"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # ── PERBANDINGAN ANTAR PERIODE ────────────────────────────────────────────
    section_header("📅 Perbandingan Antar Periode")
    col1, col2 = st.columns(2)

    with col1:
        yearly_avg = d2.groupby("year")["max"].mean().reset_index()
        yearly_avg.columns = ["Tahun", "Rata-rata ISPU"]
        yearly_avg["Warna"] = yearly_avg["Rata-rata ISPU"].apply(
            lambda v: "#E74C3C" if v >= 100 else ("#E67E22" if v >= 50 else "#2ECC71")
        )

        fig_yr = go.Figure(go.Bar(
            x=yearly_avg["Tahun"], y=yearly_avg["Rata-rata ISPU"],
            marker_color=yearly_avg["Warna"],
            text=yearly_avg["Rata-rata ISPU"].round(1),
            textposition="outside",
        ))
        fig_yr.add_hline(y=yearly_avg["Rata-rata ISPU"].mean(), line_dash="dot",
                         line_color="white", annotation_text="Rata-rata keseluruhan")
        fig_yr.update_layout(
            title="Rata-rata ISPU per Tahun",
            xaxis_title="Tahun", yaxis_title="Rata-rata ISPU",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1",
        )
        st.plotly_chart(fig_yr, use_container_width=True)

    with col2:
        # Dekade / periode perbandingan
        d2["periode"] = pd.cut(
            d2["year"],
            bins=[2009, 2013, 2017, 2020, 2023],
            labels=["2010–2013", "2014–2017", "2018–2020", "2021–2023"],
        )
        prd = d2.groupby(["periode", "categori"]).size().reset_index(name="count")
        prd_total = d2.groupby("periode").size().reset_index(name="total")
        prd = prd.merge(prd_total, on="periode")
        prd["pct"] = prd["count"] / prd["total"] * 100

        fig_prd = px.bar(
            prd, x="periode", y="pct", color="categori",
            color_discrete_map=CATEGORY_COLORS,
            barmode="stack",
            title="Komposisi Kategori per Periode",
            labels={"pct": "Persentase (%)", "periode": "Periode", "categori": "Kategori"},
            category_orders={"categori": CATEGORY_ORDER},
        )
        fig_prd.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1",
            legend=dict(bgcolor="rgba(0,0,0,0.3)"),
        )
        st.plotly_chart(fig_prd, use_container_width=True)

    # ── TREN KATEGORI DARI WAKTU KE WAKTU ──────────────────────────────────
    section_header("🔄 Persentase Hari Tidak Sehat per Tahun")
    unhealthy_yr = d2.groupby("year")["is_unhealthy"].mean().reset_index()
    unhealthy_yr.columns = ["Tahun", "Pct Tidak Sehat"]
    unhealthy_yr["Pct Tidak Sehat"] *= 100

    fig_uh = go.Figure()
    fig_uh.add_trace(go.Scatter(
        x=unhealthy_yr["Tahun"], y=unhealthy_yr["Pct Tidak Sehat"],
        mode="lines+markers",
        fill="tozeroy",
        line=dict(color="#E74C3C", width=2),
        fillcolor="rgba(231,76,60,0.15)",
        name="% Tidak Sehat",
    ))
    # trend line
    z = np.polyfit(unhealthy_yr["Tahun"], unhealthy_yr["Pct Tidak Sehat"], 1)
    p = np.poly1d(z)
    fig_uh.add_trace(go.Scatter(
        x=unhealthy_yr["Tahun"], y=p(unhealthy_yr["Tahun"]),
        mode="lines", line=dict(color="yellow", dash="dash", width=1.5),
        name="Tren Linear",
    ))
    fig_uh.update_layout(
        title="Tren Persentase Hari Tidak Sehat",
        xaxis_title="Tahun", yaxis_title="% Hari Tidak Sehat",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
    )
    st.plotly_chart(fig_uh, use_container_width=True)

    # ── INSIGHT ───────────────────────────────────────────────────────────────
    yr_max   = d2.groupby("year")["max"].mean().idxmax()
    yr_min   = d2.groupby("year")["max"].mean().idxmin()
    yr_max_v = d2.groupby("year")["max"].mean().max()
    yr_min_v = d2.groupby("year")["max"].mean().min()

    insight_box(
        f"""
        <b>Tren Jangka Panjang (2010–2023):</b> Kualitas udara Jakarta menunjukkan pola <b>fluktuatif</b>
        tanpa tren penurunan yang konsisten. Tahun <b>{yr_max}</b> mencatat rata-rata ISPU tertinggi
        ({yr_max_v:.1f}), sedangkan <b>{yr_min}</b> menjadi tahun terbersih ({yr_min_v:.1f}).<br><br>
        <b>Periode Kritis:</b> Tahun 2011–2013 dan 2018–2019 merupakan dua episode memburuknya kualitas udara
        secara signifikan — keduanya melampaui ambang batas ISPU 100 (Tidak Sehat). Perlu investigasi lebih lanjut
        terhadap faktor penyebab seperti kebakaran hutan, emisi industri, atau kondisi meteorologi.<br><br>
        <b>Dampak COVID-19 (2020):</b> Terlihat penurunan rata-rata ISPU pada tahun 2020,
        yang diduga berkaitan dengan berkurangnya aktivitas transportasi dan industri selama pandemi.
        Ini menegaskan bahwa emisi kendaraan merupakan kontributor polusi utama Jakarta.<br><br>
        <b>Rekomendasi:</b> Diperlukan kebijakan yang konsisten dan berkelanjutan — bukan hanya reaktif —
        untuk memastikan kualitas udara tidak kembali memburuk setelah normalisasi aktivitas ekonomi.
        """,
        icon="📈"
    )


# ==============================================================================
# DASHBOARD 3: PERBANDINGAN ANTAR STASIUN
# ==============================================================================
elif "Dashboard 3" in dashboard:
    st.markdown("""
    <h1 style='margin-bottom:4px;'>🗺️ Perbandingan Kualitas Udara Antar Stasiun</h1>
    <p style='color:#888;font-size:13px;'>Analisis komprehensif 5 stasiun SPKU DKI Jakarta</p>
    """, unsafe_allow_html=True)

    # ── FILTER ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Filter Dashboard 3")
        year_range3 = st.slider(
            "Rentang Tahun", 2010, 2023, (2010, 2023), key="d3_yr"
        )
        metric_d3 = st.selectbox(
            "Metrik Utama",
            ["Rata-rata ISPU", "Median ISPU", "Persentase Tidak Sehat (%)"],
            key="d3_met",
        )

    d3 = df[df["year"].between(year_range3[0], year_range3[1])]

    # ── KPI PER STASIUN ───────────────────────────────────────────────────────
    section_header("📊 KPI per Stasiun")
    station_kpi = d3.groupby("stasiun").agg(
        avg_ispu=("max", "mean"),
        median_ispu=("max", "median"),
        max_ispu=("max", "max"),
        pct_unhealthy=("is_unhealthy", lambda x: x.mean() * 100),
        total_obs=("max", "count"),
        dominant=("critical", lambda x: x.value_counts().idxmax()),
    ).reset_index().round(1)

    cols = st.columns(5)
    for i, (_, row) in enumerate(station_kpi.iterrows()):
        with cols[i]:
            color = "#E74C3C" if row["pct_unhealthy"] > 20 else (
                "#E67E22" if row["pct_unhealthy"] > 10 else "#2ECC71"
            )
            st.markdown(metric_card(
                row["stasiun"].replace(" ", "\n"),
                f"{row['avg_ispu']:.1f}",
                delta=None, color=color,
            ), unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align:center;font-size:11px;color:#aaa;">'
                f'🚫 {row["pct_unhealthy"]:.1f}% Tdk Sehat<br>'
                f'🏭 {row["dominant"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PERBANDINGAN VISUAL ───────────────────────────────────────────────────
    section_header("📊 Perbandingan Visual Antar Stasiun")
    col1, col2 = st.columns([1.2, 1])

    with col1:
        # Box plot
        fig_box = px.box(
            d3, x="stasiun", y="max",
            color="stasiun", color_discrete_map=STATION_COLORS,
            title="Distribusi ISPU per Stasiun (Box Plot)",
            labels={"max": "Nilai ISPU", "stasiun": "Stasiun"},
            points="outliers",
        )
        fig_box.add_hline(y=50,  line_dash="dash", line_color="#F1C40F",
                          annotation_text="Sedang")
        fig_box.add_hline(y=100, line_dash="dash", line_color="#E74C3C",
                          annotation_text="Tidak Sehat")
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=False,
            xaxis_tickangle=-20,
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        # Radar chart
        params_radar = ["pm10", "pm25", "so2", "co", "o3", "no2"]
        param_labels = ["PM10", "PM2.5", "SO2", "CO", "O3", "NO2"]
        radar_df = d3.groupby("stasiun")[params_radar].mean()

        # normalize per parameter
        radar_norm = (radar_df - radar_df.min()) / (radar_df.max() - radar_df.min() + 1e-9)

        fig_radar = go.Figure()
        for station in radar_norm.index:
            vals = radar_norm.loc[station].tolist()
            vals += [vals[0]]  # close polygon
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=param_labels + [param_labels[0]],
                name=station,
                line_color=STATION_COLORS.get(station, "#aaa"),
                fill="toself",
                opacity=0.35,
            ))
        fig_radar.update_layout(
            polar=dict(bgcolor="rgba(0,0,0,0)"),
            title="Profil Polutan per Stasiun (Normalized)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1",
            legend=dict(bgcolor="rgba(0,0,0,0.3)"),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── DISTRIBUSI KATEGORI PER STASIUN ──────────────────────────────────────
    section_header("🎯 Distribusi Kategori ISPU per Stasiun")
    cat_station = d3.groupby(["stasiun", "categori"]).size().reset_index(name="count")
    cat_total   = d3.groupby("stasiun").size().reset_index(name="total")
    cat_station = cat_station.merge(cat_total, on="stasiun")
    cat_station["pct"] = cat_station["count"] / cat_station["total"] * 100

    fig_cat_st = px.bar(
        cat_station, x="stasiun", y="pct", color="categori",
        color_discrete_map=CATEGORY_COLORS,
        barmode="stack",
        title="Komposisi Kategori ISPU per Stasiun (%)",
        labels={"pct": "Persentase (%)", "stasiun": "Stasiun", "categori": "Kategori"},
        category_orders={"categori": CATEGORY_ORDER},
        text="pct",
    )
    fig_cat_st.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
    fig_cat_st.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
        xaxis_tickangle=-15,
    )
    st.plotly_chart(fig_cat_st, use_container_width=True)

    # ── TREN TAHUNAN PER STASIUN ──────────────────────────────────────────────
    section_header("📅 Tren Tahunan ISPU per Stasiun")
    yearly_station = d3.groupby(["year", "stasiun"])["max"].mean().reset_index()
    fig_yr_st = px.line(
        yearly_station, x="year", y="max",
        color="stasiun", color_discrete_map=STATION_COLORS,
        markers=True,
        title="Tren Rata-rata ISPU Tahunan per Stasiun",
        labels={"max": "Rata-rata ISPU", "year": "Tahun"},
    )
    fig_yr_st.add_hline(y=100, line_dash="dash", line_color="#E74C3C",
                        annotation_text="Tidak Sehat (100)")
    fig_yr_st.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
    )
    st.plotly_chart(fig_yr_st, use_container_width=True)

    # ── INSIGHT ───────────────────────────────────────────────────────────────
    worst_st   = station_kpi.sort_values("avg_ispu", ascending=False).iloc[0]["stasiun"]
    best_st    = station_kpi.sort_values("avg_ispu").iloc[0]["stasiun"]
    worst_pct  = station_kpi.sort_values("pct_unhealthy", ascending=False).iloc[0]["pct_unhealthy"]

    insight_box(
        f"""
        <b>Stasiun Terburuk:</b> <b>{worst_st}</b> secara konsisten mencatat kualitas udara terburuk dengan
        persentase hari Tidak Sehat tertinggi ({worst_pct:.1f}%). Kawasan ini memiliki kepadatan lalu
        lintas tinggi dan berada dekat zona industri, sehingga terpapar emisi kendaraan dan aktivitas industri
        secara bersamaan.<br><br>
        <b>Stasiun Terbersih:</b> <b>{best_st}</b> secara konsisten menunjukkan kualitas udara terbaik.
        Lokasinya yang relatif lebih dekat dengan area hijau dan karakteristik tata kota yang berbeda
        kemungkinan berkontribusi pada kualitas udara yang lebih baik.<br><br>
        <b>Profil Polutan:</b> Masing-masing stasiun memiliki profil polutan yang berbeda — DKI1 Bunderan HI
        dan DKI4 Lubang Buaya lebih didominasi PM10/PM2.5 (partikel dari kendaraan & konstruksi),
        sedangkan DKI2, DKI3, DKI5 lebih didominasi O3 (ozon troposfer dari reaksi fotokimia).<br><br>
        <b>Implikasi Kebijakan:</b> Intervensi harus bersifat <i>site-specific</i>:
        stasiun berbasis PM perlu pembatasan kendaraan berbahan bakar diesel &amp; laju konstruksi;
        stasiun berbasis O3 memerlukan pengendalian VOC dan NOx dari kendaraan serta industri.
        """,
        icon="📍"
    )


# ==============================================================================
# DASHBOARD 4: ANALISIS PARAMETER PENCEMAR KRITIS
# ==============================================================================
elif "Dashboard 4" in dashboard:
    st.markdown("""
    <h1 style='margin-bottom:4px;'>🔬 Analisis Parameter Pencemar Kritis</h1>
    <p style='color:#888;font-size:13px;'>Distribusi dan tren kemunculan setiap parameter sebagai pencemar kritis</p>
    """, unsafe_allow_html=True)

    # ── FILTER ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Filter Dashboard 4")
        year_range4 = st.slider(
            "Rentang Tahun", 2010, 2023, (2010, 2023), key="d4_yr"
        )
        stations_d4 = st.multiselect(
            "Pilih Stasiun",
            df["stasiun"].unique().tolist(),
            default=df["stasiun"].unique().tolist(),
            key="d4_st",
        )
        pollutants_d4 = st.multiselect(
            "Pilih Polutan",
            ["PM10", "PM2.5", "O3", "CO", "SO2", "NO2"],
            default=["PM10", "PM2.5", "O3", "CO", "SO2", "NO2"],
            key="d4_pol",
        )

    d4 = df[
        (df["year"].between(year_range4[0], year_range4[1])) &
        (df["stasiun"].isin(stations_d4)) &
        (df["critical"].isin(pollutants_d4))
    ]

    # ── KPI POLUTAN ───────────────────────────────────────────────────────────
    section_header("🏭 Distribusi Pencemar Kritis")
    col1, col2 = st.columns([1, 1])

    with col1:
        poll_freq = d4["critical"].value_counts().reset_index()
        poll_freq.columns = ["Polutan", "Frekuensi"]
        poll_freq["Persen"] = poll_freq["Frekuensi"] / poll_freq["Frekuensi"].sum() * 100

        fig_donut = px.pie(
            poll_freq, names="Polutan", values="Frekuensi",
            color="Polutan", color_discrete_map=POLLUTANT_COLORS,
            hole=0.5,
            title="Proporsi Pencemar Kritis Keseluruhan",
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#ECF0F1",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        # Heatmap pencemar × stasiun
        heat_df = d4.groupby(["stasiun", "critical"]).size().unstack(fill_value=0)
        # normalize by row
        heat_norm = heat_df.div(heat_df.sum(axis=1), axis=0) * 100

        fig_heat = px.imshow(
            heat_norm.round(1),
            color_continuous_scale="RdYlGn_r",
            aspect="auto",
            title="Distribusi Pencemar per Stasiun (%)",
            labels={"color": "% Kejadian", "x": "Polutan", "y": "Stasiun"},
            text_auto=True,
        )
        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#ECF0F1",
            coloraxis_colorbar=dict(tickfont_color="#ECF0F1"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── TREN POLUTAN DARI WAKTU KE WAKTU ──────────────────────────────────────
    section_header("📈 Tren Kemunculan Pencemar Kritis per Tahun")
    poll_year = d4.groupby(["year", "critical"]).size().reset_index(name="count")
    poll_year_total = d4.groupby("year").size().reset_index(name="total")
    poll_year = poll_year.merge(poll_year_total, on="year")
    poll_year["pct"] = poll_year["count"] / poll_year["total"] * 100

    fig_poll_yr = px.area(
        poll_year, x="year", y="pct",
        color="critical", color_discrete_map=POLLUTANT_COLORS,
        title="Tren Persentase Pencemar Kritis per Tahun",
        labels={"pct": "% Kejadian", "year": "Tahun", "critical": "Polutan"},
        groupnorm="percent",
    )
    fig_poll_yr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
    )
    st.plotly_chart(fig_poll_yr, use_container_width=True)

    # ── NILAI RATA-RATA SETIAP POLUTAN ──────────────────────────────────────
    section_header("📊 Nilai Rata-rata Konsentrasi Polutan per Stasiun")
    params_vals = {
        "PM10": "pm10", "PM2.5": "pm25",
        "SO2":  "so2",  "CO":    "co",
        "O3":   "o3",   "NO2":   "no2",
    }
    pollutant_sel = st.selectbox(
        "Pilih Polutan untuk Detail", list(params_vals.keys()), key="d4_psel"
    )
    p_col = params_vals[pollutant_sel]

    d4_full = df[
        (df["year"].between(year_range4[0], year_range4[1])) &
        (df["stasiun"].isin(stations_d4))
    ]

    col3, col4 = st.columns(2)
    with col3:
        p_yr = d4_full.groupby("year")[p_col].mean().reset_index()
        p_yr.columns = ["Tahun", "Nilai"]
        fig_p_yr = go.Figure(go.Scatter(
            x=p_yr["Tahun"], y=p_yr["Nilai"],
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color=POLLUTANT_COLORS.get(pollutant_sel, "#aaa"), width=2),
            fillcolor=f"rgba(52,152,219,0.15)",
            name=pollutant_sel,
        ))
        fig_p_yr.update_layout(
            title=f"Tren Tahunan Konsentrasi {pollutant_sel}",
            xaxis_title="Tahun", yaxis_title=f"Nilai {pollutant_sel}",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1",
        )
        st.plotly_chart(fig_p_yr, use_container_width=True)

    with col4:
        p_st = d4_full.groupby("stasiun")[p_col].mean().reset_index()
        p_st.columns = ["Stasiun", "Nilai"]
        fig_p_st = px.bar(
            p_st, x="Stasiun", y="Nilai",
            color="Stasiun", color_discrete_map=STATION_COLORS,
            text="Nilai",
            title=f"Rata-rata {pollutant_sel} per Stasiun",
        )
        fig_p_st.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_p_st.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=False, xaxis_tickangle=-15,
        )
        st.plotly_chart(fig_p_st, use_container_width=True)

    # ── PERUBAHAN DOMINANSI POLUTAN ANTAR PERIODE ─────────────────────────────
    section_header("🔄 Pergeseran Dominansi Polutan Antar Periode")
    d4_full["periode"] = pd.cut(
        d4_full["year"],
        bins=[2009, 2013, 2017, 2020, 2023],
        labels=["2010–2013", "2014–2017", "2018–2020", "2021–2023"],
    )
    p_prd = d4_full.groupby(["periode", "critical"]).size().reset_index(name="count")
    p_prd_total = d4_full.groupby("periode").size().reset_index(name="total")
    p_prd = p_prd.merge(p_prd_total, on="periode")
    p_prd["pct"] = p_prd["count"] / p_prd["total"] * 100

    fig_p_prd = px.bar(
        p_prd, x="periode", y="pct",
        color="critical", color_discrete_map=POLLUTANT_COLORS,
        barmode="stack",
        title="Pergeseran Komposisi Pencemar Kritis per Periode",
        labels={"pct": "Persentase (%)", "periode": "Periode", "critical": "Polutan"},
    )
    fig_p_prd.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
    )
    st.plotly_chart(fig_p_prd, use_container_width=True)

    # ── INSIGHT ───────────────────────────────────────────────────────────────
    top_poll = d4["critical"].value_counts().index[0]
    top_poll_pct = d4["critical"].value_counts(normalize=True).iloc[0] * 100

    insight_box(
        f"""
        <b>Polutan Paling Dominan:</b> <b>{top_poll}</b> mendominasi sebagai pencemar kritis
        ({top_poll_pct:.1f}% dari total kejadian). Ozon (O3) terbentuk dari reaksi fotokimia antara
        NOx dan VOC di bawah sinar ultraviolet, sehingga lebih tinggi saat musim kemarau (terik matahari).<br><br>
        <b>Partikulat (PM10 &amp; PM2.5):</b> Gabungan kejadian PM10 + PM2.5 menyumbang kontribusi signifikan
        kedua, terutama di stasiun DKI1 dan DKI4. Sumber utama adalah emisi kendaraan berbahan bakar
        diesel, debu konstruksi, dan pembakaran sampah terbuka.<br><br>
        <b>Perbedaan antar Stasiun:</b>
        DKI3 (Jagakarsa) dan DKI2 (Kelapa Gading) lebih sering mengalami O3 tinggi — indikasi kawasan
        dengan paparan matahari kuat dan akumulasi NOx dari lalu lintas. DKI4 (Lubang Buaya)
        lebih banyak terpapar partikulat, terkait kepadatan kendaraan berat di wilayah timur Jakarta.<br><br>
        <b>Implikasi Pengurangan Emisi:</b>
        <br>• Program <i>low-emission zone</i> di koridor bisnis untuk mengurangi NOx (prekursor O3)
        <br>• Percepatan elektrifikasi kendaraan untuk mengurangi PM &amp; NOx secara bersamaan
        <br>• Pengetatan standar Bahan Bakar Minyak Euro 4/5 untuk kendaraan diesel (PM10/PM2.5)
        <br>• Pengendalian debu konstruksi di proyek besar dekat stasiun DKI4
        """,
        icon="🔬"
    )


# ==============================================================================
# DASHBOARD 5: POLA MUSIMAN KUALITAS UDARA
# ==============================================================================
elif "Dashboard 5" in dashboard:
    st.markdown("""
    <h1 style='margin-bottom:4px;'>🌡️ Pola Musiman Kualitas Udara</h1>
    <p style='color:#888;font-size:13px;'>Analisis pola bulanan dan keterkaitan dengan siklus musim di Jakarta</p>
    """, unsafe_allow_html=True)

    # ── FILTER ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔧 Filter Dashboard 5")
        stations_d5 = st.multiselect(
            "Pilih Stasiun",
            df["stasiun"].unique().tolist(),
            default=df["stasiun"].unique().tolist(),
            key="d5_st",
        )
        year_range5 = st.slider(
            "Rentang Tahun", 2010, 2023, (2010, 2023), key="d5_yr"
        )

    d5 = df[
        (df["year"].between(year_range5[0], year_range5[1])) &
        (df["stasiun"].isin(stations_d5))
    ]

    # ── HEATMAP BULANAN × TAHUN ────────────────────────────────────────────
    section_header("🗓️ Heatmap ISPU Bulanan × Tahunan")
    heatmap_data = d5.groupby(["year", "month"])["max"].mean().unstack()
    heatmap_data.columns = [MONTH_ID[m] for m in heatmap_data.columns]

    fig_hm = px.imshow(
        heatmap_data.round(1),
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        title="Heatmap Rata-rata ISPU per Bulan dan Tahun",
        labels={"color": "Rata-rata ISPU", "x": "Bulan", "y": "Tahun"},
        text_auto=True,
        zmin=40, zmax=140,
    )
    fig_hm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#ECF0F1",
        coloraxis_colorbar=dict(tickfont_color="#ECF0F1"),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    # ── RATA-RATA BULANAN ─────────────────────────────────────────────────
    section_header("📊 Rata-rata ISPU per Bulan (Pola Musiman)", "Agregat seluruh tahun terpilih")
    monthly_avg = d5.groupby("month").agg(
        avg_ispu=("max", "mean"),
        std_ispu=("max", "std"),
        pct_unhealthy=("is_unhealthy", "mean"),
    ).reset_index()
    monthly_avg["month_name"] = monthly_avg["month"].map(MONTH_ID)
    monthly_avg["pct_unhealthy"] *= 100

    col1, col2 = st.columns([1.3, 1])
    with col1:
        fig_monthly = go.Figure()

        # Bar utama
        bar_colors = [
            CATEGORY_COLORS["TIDAK SEHAT"] if v >= 100
            else CATEGORY_COLORS["SEDANG"] if v >= 50
            else CATEGORY_COLORS["BAIK"]
            for v in monthly_avg["avg_ispu"]
        ]
        fig_monthly.add_trace(go.Bar(
            x=monthly_avg["month_name"], y=monthly_avg["avg_ispu"],
            name="Rata-rata ISPU",
            marker_color=bar_colors,
            error_y=dict(type="data", array=monthly_avg["std_ispu"], visible=True,
                         color="rgba(255,255,255,0.4)"),
            text=monthly_avg["avg_ispu"].round(1),
            textposition="outside",
        ))
        fig_monthly.add_hline(y=50,  line_dash="dash", line_color="#F1C40F",
                               annotation_text="Sedang")
        fig_monthly.add_hline(y=100, line_dash="dash", line_color="#E74C3C",
                               annotation_text="Tidak Sehat")

        # Musim annotations
        fig_monthly.add_vrect(x0=-0.5, x1=1.5, fillcolor="#3498DB", opacity=0.07,
                               annotation_text="Hujan", annotation_position="top left")
        fig_monthly.add_vrect(x0=1.5,  x1=3.5, fillcolor="#F39C12", opacity=0.07,
                               annotation_text="Pancaroba", annotation_position="top left")
        fig_monthly.add_vrect(x0=3.5,  x1=8.5, fillcolor="#E74C3C", opacity=0.07,
                               annotation_text="Kemarau", annotation_position="top left")
        fig_monthly.add_vrect(x0=8.5,  x1=10.5, fillcolor="#F39C12", opacity=0.07,
                               annotation_text="Pancaroba", annotation_position="top left")
        fig_monthly.add_vrect(x0=10.5, x1=11.5, fillcolor="#3498DB", opacity=0.07,
                               annotation_text="Hujan", annotation_position="top left")

        fig_monthly.update_layout(
            title="Rata-rata ISPU per Bulan beserta Musim",
            xaxis_title="Bulan", yaxis_title="Rata-rata ISPU",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1", showlegend=False,
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col2:
        # Polar / radial chart musiman
        monthly_avg_sorted = monthly_avg.sort_values("month")
        fig_polar = go.Figure(go.Barpolar(
            r=monthly_avg_sorted["avg_ispu"],
            theta=monthly_avg_sorted["month_name"],
            name="Rata-rata ISPU",
            marker_color=monthly_avg_sorted["avg_ispu"],
            marker_colorscale="RdYlGn_r",
            marker_cmin=50, marker_cmax=100,
        ))
        fig_polar.update_layout(
            title="Pola Musiman ISPU (Radial)",
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 110]),
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(tickfont_color="#ECF0F1"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ECF0F1",
        )
        st.plotly_chart(fig_polar, use_container_width=True)

    # ── POLA BULANAN PER STASIUN ──────────────────────────────────────────────
    section_header("📍 Pola Musiman per Stasiun")
    monthly_station = d5.groupby(["month", "stasiun"])["max"].mean().reset_index()
    monthly_station["month_name"] = monthly_station["month"].map(MONTH_ID)

    fig_ms = px.line(
        monthly_station, x="month", y="max",
        color="stasiun", color_discrete_map=STATION_COLORS,
        markers=True,
        title="Rata-rata ISPU Bulanan per Stasiun",
        labels={"max": "Rata-rata ISPU", "month": "Bulan (1=Jan)"},
        hover_data=["month_name"],
    )
    fig_ms.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=[MONTH_ID[m] for m in range(1, 13)],
    )
    fig_ms.add_hline(y=100, line_dash="dash", line_color="#E74C3C")
    fig_ms.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
    )
    st.plotly_chart(fig_ms, use_container_width=True)

    # ── KATEGORI PER BULAN ──────────────────────────────────────────────────
    section_header("🎨 Komposisi Kategori per Bulan")
    cat_month = d5.groupby(["month", "categori"]).size().reset_index(name="count")
    cat_month_total = d5.groupby("month").size().reset_index(name="total")
    cat_month = cat_month.merge(cat_month_total, on="month")
    cat_month["pct"] = cat_month["count"] / cat_month["total"] * 100
    cat_month["month_name"] = cat_month["month"].map(MONTH_ID)

    fig_cat_m = px.bar(
        cat_month, x="month_name", y="pct",
        color="categori", color_discrete_map=CATEGORY_COLORS,
        barmode="stack",
        title="Komposisi Kategori ISPU per Bulan (%)",
        labels={"pct": "Persentase (%)", "month_name": "Bulan", "categori": "Kategori"},
        category_orders={
            "month_name": [MONTH_ID[m] for m in range(1, 13)],
            "categori": CATEGORY_ORDER,
        },
    )
    fig_cat_m.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ECF0F1",
        legend=dict(bgcolor="rgba(0,0,0,0.3)"),
    )
    st.plotly_chart(fig_cat_m, use_container_width=True)

    # ── INSIGHT ───────────────────────────────────────────────────────────────
    worst_month  = monthly_avg.sort_values("avg_ispu", ascending=False).iloc[0]
    best_month   = monthly_avg.sort_values("avg_ispu").iloc[0]
    kemarau_avg  = monthly_avg[monthly_avg["month"].isin([5,6,7,8,9,10])]["avg_ispu"].mean()
    hujan_avg    = monthly_avg[monthly_avg["month"].isin([11,12,1,2,3,4])]["avg_ispu"].mean()

    insight_box(
        f"""
        <b>Bulan Terburuk:</b> <b>{worst_month['month_name']}</b> secara konsisten menjadi bulan
        dengan kualitas udara terburuk (rata-rata ISPU: {worst_month['avg_ispu']:.1f}).
        Bulan September berada di puncak musim kemarau panjang Jakarta, dengan curah hujan sangat rendah
        sehingga tidak ada efek <i>wet deposition</i> yang membersihkan polutan dari udara.<br><br>
        <b>Bulan Terbaik:</b> <b>{best_month['month_name']}</b> mencatat kualitas udara terbaik
        (rata-rata ISPU: {best_month['avg_ispu']:.1f}) — bersamaan dengan puncak musim hujan
        yang efektif mencuci polutan dari atmosfer.<br><br>
        <b>Pola Musim Hujan vs Kemarau:</b><br>
        • Musim Kemarau (Mei–Oktober): rata-rata ISPU <b>{kemarau_avg:.1f}</b> — lebih tinggi karena
        angin dari Australia membawa udara kering, sinar UV kuat (pembentukan O3), dan tidak ada hujan pembersih.<br>
        • Musim Hujan (Nov–April): rata-rata ISPU <b>{hujan_avg:.1f}</b> — lebih rendah karena
        curah hujan tinggi membantu deposisi basah partikulat dan polutan lainnya.<br><br>
        <b>Rekomendasi Operasional:</b><br>
        ✅ Tingkatkan <i>inspeksi emisi kendaraan</i> intensif mulai Maret–April sebelum kemarau<br>
        ✅ Aktifkan <i>sistem peringatan dini kualitas udara</i> publik selama Agustus–Oktober<br>
        ✅ Batasi kegiatan konstruksi luar ruang pada Agustus–September (puncak kemarau)<br>
        ✅ Tambah ruang terbuka hijau sebagai penyerap polutan alami, terutama di wilayah DKI2 dan DKI4<br>
        ✅ Koordinasikan dengan BMKG untuk prakiraan kualitas udara berbasis cuaca musiman
        """,
        icon="🌡️"
    )

    # ── TABEL RINGKASAN BULANAN ───────────────────────────────────────────────
    with st.expander("📋 Tabel Statistik Bulanan Lengkap"):
        monthly_table = monthly_avg[["month_name", "avg_ispu", "std_ispu", "pct_unhealthy"]].copy()
        monthly_table.columns = ["Bulan", "Rata-rata ISPU", "Std Dev", "% Tidak Sehat"]
        monthly_table["Musim"] = monthly_table["Bulan"].map({
            "Jan": "🌧️ Hujan", "Feb": "🌧️ Hujan", "Mar": "🌧️ Hujan",
            "Apr": "🌧️ Hujan", "Mei": "☀️ Kemarau", "Jun": "☀️ Kemarau",
            "Jul": "☀️ Kemarau", "Agu": "☀️ Kemarau", "Sep": "☀️ Kemarau",
            "Okt": "☀️ Kemarau", "Nov": "🌧️ Hujan", "Des": "🌧️ Hujan",
        })
        st.dataframe(monthly_table.round(1), use_container_width=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<hr style='border:1px solid #333;margin:30px 0 10px;'>
<div style='text-align:center;font-size:11px;color:#666;'>
    Dashboard Kualitas Udara Jakarta • Data ISPU SPKU DKI Jakarta 2010–2023 •
    Dibuat dengan Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
