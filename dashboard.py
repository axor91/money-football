"""
Streamlit-дашборд: рыночная стоимость топ-клубов, 2019—2026.

Запуск:
    streamlit run dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CSV_PATH = Path("data/clubs.csv")

CLUB_NORMALIZE = {
    "Atlético Madrid": "Atlético de Madrid",
}

CLUB_RU = {
    "FC Barcelona": "Барселона",
    "Manchester City": "Манчестер Сити",
    "Real Madrid": "Реал Мадрид",
    "Liverpool FC": "Ливерпуль",
    "Paris Saint-Germain": "ПСЖ",
    "Chelsea FC": "Челси",
    "Tottenham Hotspur": "Тоттенхэм",
    "Manchester United": "Манчестер Юнайтед",
    "Juventus FC": "Ювентус",
    "Bayern Munich": "Бавария",
    "Arsenal FC": "Арсенал",
    "SSC Napoli": "Наполи",
    "Inter Milan": "Интер",
    "AC Milan": "Милан",
    "Borussia Dortmund": "Боруссия Дортмунд",
    "Bayer 04 Leverkusen": "Байер Леверкузен",
    "RB Leipzig": "РБ Лейпциг",
    "Atlético de Madrid": "Атлетико Мадрид",
    "Aston Villa": "Астон Вилла",
    "Leicester City": "Лестер",
    "Everton FC": "Эвертон",
    "Atalanta BC": "Аталанта",
    "AS Roma": "Рома",
    "Newcastle United": "Ньюкасл",
    "Real Sociedad": "Реал Сосьедад",
    "Brighton & Hove Albion": "Брайтон",
    "Brentford FC": "Брентфорд",
    "West Ham United": "Вест Хэм",
    "Nottingham Forest": "Ноттингем Форест",
    "Ajax Amsterdam": "Аякс",
    "Olympique Lyon": "Лион",
    "Wolverhampton Wanderers": "Вулверхэмптон",
    "Valencia CF": "Валенсия",
    "Sporting CP": "Спортинг",
    "Crystal Palace": "Кристал Пэлас",
    "Sevilla FC": "Севилья",
    "SL Benfica": "Бенфика",
    "AS Monaco": "Монако",
    "Villarreal CF": "Вильярреал",
    "SS Lazio": "Лацио",
    "Southampton FC": "Саутгемптон",
    "AFC Bournemouth": "Борнмут",
}

COUNTRY_RU = {
    "Spain": "Испания",
    "England": "Англия",
    "Italy": "Италия",
    "Germany": "Германия",
    "France": "Франция",
    "Netherlands": "Нидерланды",
    "Portugal": "Португалия",
}

# AS Monaco на TM числится со страной Monaco, но играет во французской Ligue 1.
# Лига > место расположения, поэтому переопределяем.
CLUB_COUNTRY_OVERRIDE = {
    "AS Monaco": "France",
}

LEAGUE_COLORS = {
    "Англия": "#DC2626",
    "Испания": "#F59E0B",
    "Германия": "#0891B2",
    "Италия": "#16A34A",
    "Франция": "#7C3AED",
    "Нидерланды": "#EC4899",
    "Португалия": "#0EA5E9",
}

PALETTE = [
    "#DC2626", "#2563EB", "#059669", "#7C3AED", "#EA580C",
    "#0891B2", "#DB2777", "#65A30D", "#CA8A04", "#0EA5E9",
    "#9D174D", "#B45309", "#1E40AF", "#15803D", "#9333EA",
]
GREY_LINE = "#D1D5DB"
GREY_INK = "#6B7280"
INK = "#0F172A"
NAVY = "#1E3A8A"
ACCENT = "#DC2626"


def ru(club: str) -> str:
    return CLUB_RU.get(club, club)


st.set_page_config(
    page_title="Стоимость футбольных клубов · 2019—2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:wght@600;700&display=swap');

html, body, [class*="st-"], .stMarkdown, button, input, select, textarea {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1680px !important;
}

h1, h2, h3, h4 {
    font-family: 'Source Serif 4', 'Inter', serif !important;
    letter-spacing: -0.015em;
    color: #0F172A;
}
h1 { font-weight: 700; font-size: 2.8rem; line-height: 1.05; margin-bottom: 0.6rem; }
h2 { font-weight: 700; font-size: 1.6rem; margin-top: 3rem !important; margin-bottom: 1rem !important; }
h3 { font-weight: 600; font-size: 1.1rem; margin-top: 2rem !important; }

.eyebrow {
    color: #DC2626; font-size: 0.78rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.4rem;
}
.dek {
    color: #374151; font-size: 1.08rem; line-height: 1.55;
    max-width: 820px; margin-bottom: 0.5rem;
}

.kpi-row {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
    border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;
    margin: 1.75rem 0 0.5rem 0;
}
.kpi { padding: 1.1rem 1.75rem; border-right: 1px solid #F3F4F6; }
.kpi:first-child { padding-left: 0; }
.kpi:last-child { border-right: none; padding-right: 0; }
.kpi .lbl {
    color: #6B7280; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 600; margin-bottom: 0.4rem;
}
.kpi .val {
    color: #0F172A; font-size: 1.85rem; font-weight: 700;
    line-height: 1.1; font-family: 'Source Serif 4', serif;
}
.kpi .sub { color: #6B7280; font-size: 0.82rem; margin-top: 0.4rem; line-height: 1.4; }
.kpi .delta-up { color: #059669; font-weight: 600; }
.kpi .delta-dn { color: #DC2626; font-weight: 600; }

.insight-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
    margin-top: 0.75rem; margin-bottom: 0.5rem;
}
.insight {
    border-left: 3px solid #DC2626; padding: 0.4rem 0.9rem;
    background: #FAFAFA; border-radius: 0 6px 6px 0;
}
.insight .title {
    font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #DC2626; margin-bottom: 0.25rem;
}
.insight .body { color: #1F2937; font-size: 0.93rem; line-height: 1.45; }

.footer {
    color: #9CA3AF; font-size: 0.83rem; padding-top: 1.5rem;
    border-top: 1px solid #E5E7EB; margin-top: 3rem; line-height: 1.6;
}
.footer b { color: #4B5563; }

[data-testid="stSidebar"] {
    background: #FAFAF9; border-right: 1px solid #E5E7EB; padding-top: 1rem;
}
[data-testid="stSidebar"] h3 {
    font-family: 'Inter', sans-serif !important; font-size: 0.78rem !important;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #6B7280 !important; font-weight: 600 !important; margin-top: 1.4rem !important;
}
.stMultiSelect [data-baseweb="tag"] { background: #0F172A !important; border-radius: 4px !important; }
.stMultiSelect [data-baseweb="tag"] span { color: white !important; font-size: 0.78rem !important; }
[data-testid="stDataFrame"] { border: 1px solid #E5E7EB; border-radius: 6px; }

@media (max-width: 1024px) {
    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    h1 { font-size: 2.2rem; }
    h2 { font-size: 1.35rem; }
    .kpi .val { font-size: 1.5rem; }
    .insight-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.5rem !important;
    }
    h1 { font-size: 1.8rem; line-height: 1.15; }
    h2 { font-size: 1.2rem; margin-top: 2rem !important; }
    .dek { font-size: 0.96rem; }
    .kpi-row { grid-template-columns: 1fr 1fr; }
    .kpi { padding: 1rem 0.9rem; border-right: none; border-bottom: 1px solid #F3F4F6; }
    .kpi:first-child, .kpi:nth-child(3) { padding-left: 0; }
    .kpi:nth-child(2), .kpi:last-child { padding-right: 0; }
    .kpi:nth-child(3), .kpi:last-child { border-bottom: none; padding-bottom: 0; }
    .kpi .val { font-size: 1.25rem; }
    .insight-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
    .kpi-row { grid-template-columns: 1fr; }
    .kpi { border-bottom: 1px solid #F3F4F6 !important; padding: 0.85rem 0 !important; }
    .kpi:last-child { border-bottom: none !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(path: str, mtime: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df["club"] = df["club"].replace(CLUB_NORMALIZE)
    df = df.dropna(subset=["club", "value_eur_m"])
    df["country"] = df.apply(
        lambda r: CLUB_COUNTRY_OVERRIDE.get(r["club"], r["country"]),
        axis=1,
    )
    df["country_ru"] = df["country"].map(COUNTRY_RU).fillna(df["country"])
    df["club_ru"] = df["club"].map(CLUB_RU).fillna(df["club"])
    return df


def fmt_eur(v: float) -> str:
    if v >= 1000:
        return f"€{v / 1000:.2f} млрд"
    return f"€{v:.0f} млн"


_MONTHS_RU = {
    1: ("Январь", "янв"), 2: ("Февраль", "фев"), 3: ("Март", "мар"),
    4: ("Апрель", "апр"), 5: ("Май", "май"), 6: ("Июнь", "июн"),
    7: ("Июль", "июл"), 8: ("Август", "авг"), 9: ("Сентябрь", "сен"),
    10: ("Октябрь", "окт"), 11: ("Ноябрь", "ноя"), 12: ("Декабрь", "дек"),
}


def fmt_month(dt, short: bool = False) -> str:
    m = _MONTHS_RU[dt.month][1 if short else 0]
    return f"{m} {dt.year}"


PLOTLY_CONFIG_BASE = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "lasso2d", "select2d", "autoScale2d", "zoomIn2d", "zoomOut2d",
    ],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


def plotly_config(filename: str) -> dict:
    cfg = {**PLOTLY_CONFIG_BASE}
    cfg["toImageButtonOptions"] = {**cfg["toImageButtonOptions"], "filename": filename}
    return cfg


if not CSV_PATH.exists():
    st.error(f"Нет файла `{CSV_PATH}`. Сначала запусти `python collect.py`.")
    st.stop()

df = load_data(str(CSV_PATH), CSV_PATH.stat().st_mtime)
first_snap = df["snapshot_date"].min()
last_snap = df["snapshot_date"].max()
latest = df[df["snapshot_date"] == last_snap].sort_values("rank").reset_index(drop=True)
first = df[df["snapshot_date"] == first_snap].sort_values("rank").reset_index(drop=True)

# ───────── Hero ──────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow">Экономика футбола · 2019—2026</div>', unsafe_allow_html=True)
st.markdown("# Большие деньги в большом футболе")
st.markdown(
    f'<p class="dek">Совокупная рыночная стоимость составов '
    f'<b>топ-25 клубов мира</b> с {fmt_month(first_snap)} по {fmt_month(last_snap)}. '
    f'По данным Transfermarkt.</p>',
    unsafe_allow_html=True,
)

# ───────── KPI ───────────────────────────────────────────────────────────────
total_now = latest["value_eur_m"].sum()
total_then = first["value_eur_m"].sum()
growth_pct = (total_now - total_then) / total_then * 100

pair = (
    df[df["snapshot_date"].isin([first_snap, last_snap])]
    .pivot_table(index="club", columns="snapshot_date", values="value_eur_m")
    .dropna()
)
pair.columns = ["v_first", "v_last"]
pair["delta_abs"] = pair["v_last"] - pair["v_first"]
pair["delta_pct"] = (pair["v_last"] - pair["v_first"]) / pair["v_first"] * 100
biggest_riser = pair.sort_values("delta_abs", ascending=False).iloc[0]
top_pct_row = pair.sort_values("delta_pct", ascending=False).iloc[0]
top_faller = pair.sort_values("delta_abs").iloc[0]

leader_then = first.iloc[0]
leader_now = latest.iloc[0]

kpi_html = f"""
<div class="kpi-row">
  <div class="kpi">
    <div class="lbl">Суммарная стоимость · {fmt_month(last_snap, short=True)}</div>
    <div class="val">€{total_now/1000:.2f} млрд</div>
    <div class="sub"><span class="delta-up">▲ {growth_pct:+.0f}%</span> к {fmt_month(first_snap, short=True)}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Лидер · {fmt_month(last_snap, short=True)}</div>
    <div class="val">{ru(leader_now['club'])}</div>
    <div class="sub">{fmt_eur(leader_now['value_eur_m'])} · {leader_now['country_ru'] or '—'}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Лидер · {fmt_month(first_snap, short=True)}</div>
    <div class="val">{ru(leader_then['club'])}</div>
    <div class="sub">{fmt_eur(leader_then['value_eur_m'])} · {leader_then['country_ru'] or '—'}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Главный взлёт за период</div>
    <div class="val">{ru(biggest_riser.name)}</div>
    <div class="sub"><span class="delta-up">▲ +{fmt_eur(biggest_riser['delta_abs'])}</span> ({biggest_riser['delta_pct']:+.0f}%)</div>
  </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)


# ───────── URL params: восстановление состояния ──────────────────────────────
qp = st.query_params
qp_clubs = [c for c in qp.get("clubs", "").split(",") if c]
qp_countries = [c for c in qp.get("countries", "").split(",") if c]


# ───────── Сайдбар ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Страны")
    countries = sorted(df["country"].dropna().unique())
    countries_default = [c for c in countries if c in qp_countries]
    selected_countries = st.multiselect(
        "страны",
        countries,
        default=countries_default,
        format_func=lambda x: COUNTRY_RU.get(x, x),
        label_visibility="collapsed",
        placeholder="Все страны",
    )

    if selected_countries:
        country_pool_df = df[df["country"].isin(selected_countries)]
    else:
        country_pool_df = df

    pool = sorted(country_pool_df["club"].unique())
    last_in_pool = (
        country_pool_df[country_pool_df["snapshot_date"] == last_snap]
        .sort_values("rank")
    )
    pool_set = set(pool)
    qp_clubs_in_pool = [c for c in qp_clubs if c in pool_set]
    if qp_clubs_in_pool:
        clubs_default = qp_clubs_in_pool
    else:
        clubs_default = last_in_pool.head(5)["club"].tolist()

    st.markdown("### Клубы для выделения")
    selected = st.multiselect(
        "клубы",
        pool,
        default=clubs_default,
        format_func=lambda x: ru(x),
        label_visibility="collapsed",
        placeholder="Выбери клубы",
    )

    st.markdown("### Опции")
    smooth = st.checkbox("Сглаживать линии", value=True)
    log_scale = st.checkbox("Логарифмическая шкала", value=False)

    st.markdown("### Поделиться")
    st.caption("Текущий выбор сохраняется в URL — скопируй адресную строку, чтобы поделиться.")

# Записываем выбор в URL
new_qp = {}
if selected:
    new_qp["clubs"] = ",".join(selected)
if selected_countries:
    new_qp["countries"] = ",".join(selected_countries)
if dict(qp) != new_qp:
    qp.clear()
    for k, v in new_qp.items():
        qp[k] = v

scope = country_pool_df


def base_layout(height: int = 520, right_margin: int = 200) -> dict:
    return dict(
        height=height,
        template="simple_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color=INK),
        margin=dict(l=10, r=right_margin, t=15, b=40),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="white", bordercolor="#E5E7EB",
            font=dict(family="Inter", size=12, color=INK),
        ),
        xaxis=dict(
            showgrid=False, showline=True, linecolor="#E5E7EB",
            tickfont=dict(size=11, color=GREY_INK),
            tickformat="%Y", dtick="M12",
            ticks="outside", ticklen=4, tickcolor="#E5E7EB",
        ),
        yaxis=dict(
            gridcolor="#F3F4F6", zeroline=False, showline=False,
            tickfont=dict(size=11, color=GREY_INK),
        ),
        showlegend=False,
    )


# ───────── График 1: динамика стоимости ──────────────────────────────────────
st.markdown("## Динамика рыночной стоимости")

LABEL_LIMIT = 12
BUMP_LIMIT = 10
TOP_M, BOT_M = 15, 40
MIN_GAP_PX = 28

shape = "spline" if smooth else "linear"
use_inline_labels = 0 < len(selected) <= LABEL_LIMIT

fig = go.Figure()

for club in scope["club"].unique():
    if club in selected:
        continue
    sub = scope[scope["club"] == club].sort_values("snapshot_date")
    fig.add_trace(go.Scatter(
        x=sub["snapshot_date"], y=sub["value_eur_m"],
        mode="lines",
        line=dict(width=1, color=GREY_LINE, shape=shape),
        opacity=0.7,
        name=ru(club), hoverinfo="skip", showlegend=False,
    ))

selected_endpoints = []
for i, club in enumerate(selected):
    sub = scope[scope["club"] == club].sort_values("snapshot_date")
    if sub.empty:
        continue
    color = PALETTE[i % len(PALETTE)]
    name_ru = ru(club)
    fig.add_trace(go.Scatter(
        x=sub["snapshot_date"], y=sub["value_eur_m"],
        mode="lines+markers",
        line=dict(width=2.6, color=color, shape=shape),
        marker=dict(size=5, color=color, line=dict(width=1.5, color="white")),
        name=name_ru,
        hovertemplate=f"<b>{name_ru}</b><br>%{{x|%b %Y}}<br>€%{{y:.0f}} млн<extra></extra>",
        showlegend=not use_inline_labels,
    ))
    last = sub.iloc[-1]
    selected_endpoints.append((name_ru, last["snapshot_date"], float(last["value_eur_m"]), color))

y_max_data = float(scope["value_eur_m"].max())
y_min_data = max(0.0, float(scope["value_eur_m"].min()))
y_range = y_max_data - y_min_data
y_axis_min = max(0.0, y_min_data - y_range * 0.06)
y_axis_max = y_max_data + y_range * 0.10

CHART_H = 660
PLOT_H_PX = CHART_H - TOP_M - BOT_M
axis_range = y_axis_max - y_axis_min


def _data_to_pix(y: float) -> float:
    return (y_axis_max - y) / axis_range * PLOT_H_PX


def _pix_to_data(p: float) -> float:
    return y_axis_max - p / PLOT_H_PX * axis_range


if use_inline_labels and selected_endpoints:
    selected_endpoints.sort(key=lambda r: -r[2])
    prev_pix = float("-inf")
    laid_pix = []
    for name, x, y, color in selected_endpoints:
        natural_pix = _data_to_pix(y)
        target_pix = max(natural_pix, prev_pix + MIN_GAP_PX)
        laid_pix.append((name, x, y, natural_pix, target_pix, color))
        prev_pix = target_pix

    bottom_pix = laid_pix[-1][4]
    floor_pix = PLOT_H_PX - 6
    if bottom_pix > floor_pix:
        excess = bottom_pix - floor_pix
        lift = min(excess, laid_pix[0][4] - 6)
        laid_pix = [(n, x, y, np_, tp - lift, col) for n, x, y, np_, tp, col in laid_pix]

    for name, x, y_actual, natural_pix, target_pix, color in laid_pix:
        y_label = _pix_to_data(target_pix)
        offset_pix = abs(target_pix - natural_pix)
        fig.add_annotation(
            x=x, y=y_label, xref="x", yref="y",
            ax=x, ay=y_actual, axref="x", ayref="y",
            text=f"  {name}",
            showarrow=offset_pix > 6,
            arrowhead=0, arrowwidth=0.6, arrowcolor=color,
            standoff=2, xanchor="left", yanchor="middle",
            font=dict(family="Inter", size=10, color=color),
        )

layout = base_layout(height=CHART_H, right_margin=220 if use_inline_labels else 30)
layout["yaxis"]["range"] = [y_axis_min, y_axis_max]
layout["yaxis"]["title"] = dict(text="млн €", font=dict(size=11, color=GREY_INK), standoff=8)
if log_scale:
    layout["yaxis"]["type"] = "log"

if not use_inline_labels and selected:
    layout["showlegend"] = True
    layout["legend"] = dict(
        orientation="h", yanchor="bottom", y=-0.22, xanchor="left", x=0,
        font=dict(family="Inter", size=11, color=INK),
        bgcolor="rgba(255,255,255,0)", borderwidth=0,
    )
    layout["margin"]["b"] = 100

fig.update_layout(**layout)

# ─── Аннотации ключевых событий ────
EVENTS = [
    ("2020-04-01", "COVID-19", "Переоценка TM"),
    ("2021-10-07", "Ньюкасл", "Покупка PIF"),
    ("2022-05-30", "Челси", "Продажа Boehly"),
]
for date_str, ev_title, ev_sub in EVENTS:
    fig.add_vline(x=date_str, line_width=1, line_dash="dot", line_color="#9CA3AF")
    fig.add_annotation(
        x=date_str, y=1, yref="paper",
        text=f"<b>{ev_title}</b><br><span style='color:#9CA3AF'>{ev_sub}</span>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter", size=10, color="#4B5563"),
        xshift=4, yshift=-4,
        align="left",
    )

st.plotly_chart(fig, width="stretch", config=plotly_config("football-clubs-dynamics"))


# ───────── Insights ──────────────────────────────────────────────────────────
insight_html = f"""
<div class="insight-grid">
  <div class="insight">
    <div class="title">№1 в абсолюте</div>
    <div class="body"><b>{ru(biggest_riser.name)}</b> прибавил <b>{fmt_eur(biggest_riser['delta_abs'])}</b>
    с {first_snap:%Y} ({biggest_riser['delta_pct']:+.0f}%).</div>
  </div>
  <div class="insight">
    <div class="title">Лидер по %</div>
    <div class="body"><b>{ru(top_pct_row.name)}</b> вырос на <b>{top_pct_row['delta_pct']:+.0f}%</b>
    — с {fmt_eur(top_pct_row['v_first'])} до {fmt_eur(top_pct_row['v_last'])}.</div>
  </div>
  <div class="insight">
    <div class="title">Просел сильнее всех</div>
    <div class="body"><b>{ru(top_faller.name)}</b>:
    <b>{fmt_eur(abs(top_faller['delta_abs']))}</b> вниз
    ({top_faller['delta_pct']:+.0f}%) с {first_snap:%Y} года.</div>
  </div>
</div>
"""
st.markdown(insight_html, unsafe_allow_html=True)


# ───────── Секция "По лигам" ─────────────────────────────────────────────────
st.markdown("## Соотношение лиг")
st.markdown(
    '<p class="footer" style="border:none;padding:0;margin:0 0 0.8rem 0;color:#6B7280;'
    'font-size:0.95rem;max-width:760px;">Сумма стоимости клубов из топ-25 в каждой лиге, '
    'по полугодиям. Чем шире полоса — тем больше «вес» лиги.</p>',
    unsafe_allow_html=True,
)

country_totals = (
    df.groupby(["snapshot_date", "country_ru"])["value_eur_m"]
    .sum().reset_index()
)
country_order = (
    df.groupby("country_ru")["value_eur_m"].sum()
    .sort_values(ascending=False).index.tolist()
)

fig_l = go.Figure()
for country in country_order:
    sub = country_totals[country_totals["country_ru"] == country].sort_values("snapshot_date")
    color = LEAGUE_COLORS.get(country, "#94A3B8")
    fig_l.add_trace(go.Scatter(
        x=sub["snapshot_date"], y=sub["value_eur_m"],
        mode="lines",
        stackgroup="one",
        line=dict(width=0.5, color=color),
        fillcolor=color,
        name=country,
        hovertemplate=f"<b>{country}</b><br>%{{x|%b %Y}}<br>€%{{y:.0f}} млн<extra></extra>",
    ))

layout_l = dict(
    height=460,
    template="simple_white",
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Inter, system-ui, sans-serif", size=12, color=INK),
    margin=dict(l=10, r=20, t=15, b=70),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="white", bordercolor="#E5E7EB",
                    font=dict(family="Inter", size=12, color=INK)),
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.22, xanchor="left", x=0,
        font=dict(family="Inter", size=11, color=INK),
        bgcolor="rgba(255,255,255,0)", borderwidth=0,
    ),
    xaxis=dict(
        showgrid=False, showline=True, linecolor="#E5E7EB",
        tickformat="%Y", dtick="M12",
        tickfont=dict(size=11, color=GREY_INK),
        ticks="outside", ticklen=4, tickcolor="#E5E7EB",
    ),
    yaxis=dict(
        gridcolor="#F3F4F6", zeroline=False, showline=False,
        title=dict(text="млн €", font=dict(size=11, color=GREY_INK), standoff=8),
        tickfont=dict(size=11, color=GREY_INK),
    ),
)
fig_l.update_layout(**layout_l)
st.plotly_chart(fig_l, width="stretch", config=plotly_config("football-clubs-leagues"))


# ───────── График 2: bump chart ──────────────────────────────────────────────
st.markdown("## Гонка за лидерство")

if selected:
    if len(selected) > BUMP_LIMIT:
        bump_clubs = (
            scope[(scope["club"].isin(selected)) & (scope["snapshot_date"] == last_snap)]
            .sort_values("rank").head(BUMP_LIMIT)["club"].tolist()
        )
        st.caption(
            f"Показаны топ-{BUMP_LIMIT} клубов из {len(selected)} выбранных по последнему рейтингу — "
            f"иначе линии сливаются. Сузь выбор, чтобы увидеть других."
        )
    else:
        bump_clubs = list(selected)

    bump_endpoints = []
    fig2 = go.Figure()
    for i, club in enumerate(bump_clubs):
        sub = scope[scope["club"] == club].sort_values("snapshot_date")
        if sub.empty:
            continue
        color = PALETTE[selected.index(club) % len(PALETTE)] if club in selected else PALETTE[i % len(PALETTE)]
        name_ru = ru(club)
        fig2.add_trace(go.Scatter(
            x=sub["snapshot_date"], y=sub["rank"],
            mode="lines+markers",
            line=dict(width=3, color=color, shape="spline", smoothing=0.6),
            marker=dict(size=10, color=color, line=dict(width=2, color="white")),
            name=name_ru,
            hovertemplate=f"<b>{name_ru}</b><br>%{{x|%b %Y}}<br>Ранг %{{y}}<extra></extra>",
            showlegend=False,
        ))
        last_p = sub.iloc[-1]
        bump_endpoints.append((name_ru, last_p["snapshot_date"], int(last_p["rank"]), color))

    bump_h = max(420, 42 * len(bump_clubs) + 220)
    bump_plot_h = bump_h - TOP_M - BOT_M
    bump_axis_range = 26

    def _rank_to_pix(r: float) -> float:
        return r / bump_axis_range * bump_plot_h

    def _pix_to_rank(p: float) -> float:
        return p / bump_plot_h * bump_axis_range

    bump_endpoints.sort(key=lambda r: r[2])
    prev_pix_b = float("-inf")
    laid_b_pix = []
    for name, x, r, color in bump_endpoints:
        natural_pix = _rank_to_pix(r)
        target_pix = max(natural_pix, prev_pix_b + MIN_GAP_PX)
        laid_b_pix.append((name, x, r, natural_pix, target_pix, color))
        prev_pix_b = target_pix

    bottom_pix_b = laid_b_pix[-1][4]
    if bottom_pix_b > bump_plot_h - 6:
        lift = bottom_pix_b - (bump_plot_h - 6)
        lift = min(lift, laid_b_pix[0][4] - 6)
        laid_b_pix = [(n, x, r, np_, tp - lift, col) for n, x, r, np_, tp, col in laid_b_pix]

    for name, x, r_actual, natural_pix, target_pix, color in laid_b_pix:
        r_label = _pix_to_rank(target_pix)
        offset_pix = abs(target_pix - natural_pix)
        fig2.add_annotation(
            x=x, y=r_label, xref="x", yref="y",
            ax=x, ay=r_actual, axref="x", ayref="y",
            text=f"  {name}",
            showarrow=offset_pix > 6,
            arrowhead=0, arrowwidth=0.6, arrowcolor=color,
            standoff=2, xanchor="left", yanchor="middle",
            font=dict(family="Inter", size=10, color=color),
        )

    layout2 = base_layout(height=bump_h, right_margin=220)
    layout2["yaxis"].update(
        autorange="reversed", dtick=5, range=[26, 0],
        title=dict(text="ранг", font=dict(size=11, color=GREY_INK), standoff=8),
    )
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, width="stretch", config=plotly_config("football-clubs-bump"))
else:
    st.info("Выбери клубы в боковой панели, чтобы увидеть гонку.")


# ───────── График 3: топ-15 на сегодня ───────────────────────────────────────
latest_in_scope = scope[scope["snapshot_date"] == last_snap].sort_values("rank")
top15 = latest_in_scope.head(15)
top15_rev = top15.iloc[::-1]

st.markdown(f"## Рейтинг · {fmt_month(last_snap)}")

bar_colors = [ACCENT if r == top15["rank"].min() else NAVY for r in top15_rev["rank"]]
bar_text = [fmt_eur(v) for v in top15_rev["value_eur_m"]]
bar_labels_ru = [ru(c) for c in top15_rev["club"]]

fig3 = go.Figure(go.Bar(
    x=top15_rev["value_eur_m"],
    y=bar_labels_ru,
    orientation="h",
    marker=dict(color=bar_colors, line=dict(width=0)),
    text=bar_text,
    textposition="outside",
    textfont=dict(family="Inter", size=11, color=INK),
    cliponaxis=False,
    hovertemplate="<b>%{y}</b><br>€%{x:.0f} млн<extra></extra>",
))
fig3.update_layout(
    height=520,
    template="simple_white", plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Inter, system-ui, sans-serif", size=12, color=INK),
    margin=dict(l=10, r=140, t=10, b=20),
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, showline=False,
               range=[0, top15_rev["value_eur_m"].max() * 1.18]),
    yaxis=dict(showgrid=False, tickfont=dict(size=12, color=INK), automargin=True),
    bargap=0.4,
)
st.plotly_chart(fig3, width="stretch", config=plotly_config("football-clubs-ranking"))

st.markdown("### Полный рейтинг")
st.dataframe(
    latest_in_scope.assign(club_ru=latest_in_scope["club"].map(ru))
        [["rank", "club_ru", "country_ru", "value_eur_m"]].rename(columns={
            "rank": "#",
            "club_ru": "Клуб",
            "country_ru": "Страна",
            "value_eur_m": "Стоимость, млн €",
        }),
    width="stretch",
    hide_index=True,
)


# ───────── Footer ────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="footer">'
    f'<b>Методология.</b> Совокупная рыночная стоимость состава по версии Transfermarkt, '
    f'в млн евро. Исторические значения восстановлены по архивным снапшотам Wayback Machine — '
    f'один срез на каждый квартал, отклонение от целевой даты ≤ 60 дней. '
    f'Каждый снапшот = первая страница рейтинга (топ-25 клубов).<br>'
    f'<b>Период:</b> {fmt_month(first_snap, short=True)} → {fmt_month(last_snap, short=True)} · '
    f'<b>Срезов:</b> {df["snapshot_date"].nunique()} · '
    f'<b>Клубов в выборке:</b> {df["club"].nunique()}.'
    f'</div>',
    unsafe_allow_html=True,
)
