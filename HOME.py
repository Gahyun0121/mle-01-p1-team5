import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from src.sidebar import render_sidebar

st.set_page_config(page_title="트립가드", layout="wide")
render_sidebar()

ROOT = Path(__file__).resolve().parent

st.markdown("""
<style>
/* 페이지 전체 배경을 아주 옅은 슬레이트로 (완전 흰색 방지) */
[data-testid="stAppViewContainer"]{background:#FFFFFF;}
[data-testid="stHeader"]{background:transparent;}

.hero{text-align:center;padding-bottom:32px;border-bottom:1px solid #E2E8F0;margin-bottom:12px;}
.hero-title{font-size:38px;font-weight:700;color:#0F172A;}
.hero-sub{font-size:15px;color:#64748B;margin-top:12px;line-height:1.7;}

/* 숫자 카드 - 항목별 색상 지정 */
.stat{border-radius:12px;padding:24px;text-align:center;border:1px solid;}
.stat-label{font-size:15px;font-weight:600;}
.stat-value{font-size:30px;font-weight:700;margin-top:8px;}

.stat-blue{background:#EFF6FF;border-color:#BFDBFE;}
.stat-blue .stat-label{color:#3B82F6;}
.stat-blue .stat-value{color:#1D4ED8;}

.stat-amber{background:#FFFBEB;border-color:#FDE68A;}
.stat-amber .stat-label{color:#D97706;}
.stat-amber .stat-value{color:#B45309;}

.stat-teal{background:#F0FDFA;border-color:#99F6E4;}
.stat-teal .stat-label{color:#0D9488;}
.stat-teal .stat-value{color:#0F766E;}

.section-title{
    font-size:15px;font-weight:600;color:#0F172A;
    margin:40px 0 16px 0;padding-left:9px;
    border-left:3px solid #2563EB;
}

/* 카드 전체가 링크. a 태그라 어디를 눌러도 페이지 이동됨 */
.feat{
    display:block;
    background:#fff;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:22px;
    height:130px;
    box-sizing:border-box;
    text-decoration:none;
    transition:border-color .15s, transform .15s;
}
.feat:hover{
    border-color:#93C5FD;
    transform:translateY(-2px);
}
/* a 안에서는 div가 쪼개지므로 span에 display:block을 줘서 줄바꿈시킴 */
.feat-icon{display:block;font-size:20px;}
.feat-title{display:block;font-size:16px;font-weight:600;color:#0F172A;margin-top:10px;text-decoration:none;}
.feat-desc{display:block;font-size:13px;color:#64748B;line-height:1.6;margin-top:6px;text-decoration:none;}

.footer{
    margin-top:40px;padding-top:18px;border-top:1px solid #E2E8F0;
    font-size:12px;color:#94A3B8;text-align:center;
}

/* 지구본 위 커서를 손 모양으로 (기본 십자는 드래그 가능해 보이지 않음) */
.js-plotly-plot .draglayer .nsewdrag{cursor:grab !important;}
.js-plotly-plot .draglayer .nsewdrag:active{cursor:grabbing !important;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_alarm():
    df = pd.read_csv(ROOT / "data" / "alarm_clean.csv")
    rep = df.groupby(["iso3", "국가명"], as_index=False)["경보단계"].max()
    return rep


st.markdown("""
<div class="hero">
    <div class="hero-title">🌐 트립가드</div>
    <div class="hero-sub">
        외교부가 발표하는 국가별 여행경보와 안전공지, 현지에서 실제로 발생한 사건사고 정보를<br>
        여행지 추천 데이터와 함께 모아 어디로 갈지부터 무엇을 조심할지까지 한 곳에서 확인합니다.
    </div>
</div>
""", unsafe_allow_html=True)

alarm = load_alarm()

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
stats = [
    ("여행경보", f"{alarm['iso3'].nunique()}개국", "stat-amber"),
    ("안전공지", "5,957건", "stat-blue"),
    ("여행지 추천", "43개국", "stat-teal"),
]
for col, (label, value, cls) in zip([s1, s2, s3], stats):
    with col:
        st.markdown(
            f'<div class="stat {cls}"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div></div>',
            unsafe_allow_html=True
        )

st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

LEVEL_COLOR = {1: "#60A5FA", 2: "#FBBF24", 3: "#F97316", 4: "#DC2626"}
LEVEL_NAME = {1: "여행유의", 2: "여행자제", 3: "출국권고", 4: "여행금지"}

fig = go.Figure()

for level in sorted(alarm["경보단계"].dropna().unique()):
    sub = alarm[alarm["경보단계"] == level]
    fig.add_trace(go.Choropleth(
        locations=sub["iso3"],
        z=[level] * len(sub),
        text=sub["국가명"],
        colorscale=[[0, LEVEL_COLOR[int(level)]], [1, LEVEL_COLOR[int(level)]]],
        showscale=False,
        name=f"{int(level)}단계 · {LEVEL_NAME[int(level)]}",
        showlegend=True,
        marker_line_color="#FFFFFF",
        marker_line_width=0.3,
        hovertemplate="<b>%{text}</b><br>" + f"{int(level)}단계 · {LEVEL_NAME[int(level)]}" + "<extra></extra>",
    ))

fig.update_geos(
    projection_type="orthographic",
    projection_rotation=dict(lon=127, lat=20),
    showocean=True, oceancolor="#DCE9F2",
    showland=True, landcolor="#F4F1EA",
    showlakes=True, lakecolor="#DCE9F2",
    showcountries=True, countrycolor="#FFFFFF",
    showcoastlines=True, coastlinecolor="#A8C0D0", coastlinewidth=0.5,
    framecolor="#D9E2EA", showframe=True,
    bgcolor="rgba(0,0,0,0)",
)

fig.update_layout(
    height=460,
    margin=dict(l=0, r=0, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=0, x=0, font=dict(size=12)),
    dragmode="orbit",
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displaylogo": False, "scrollZoom": False},
)
st.caption("지구본을 드래그하면 회전합니다 · 국가에 마우스를 올리면 경보단계가 표시됩니다")

# 지구본과 탭 섹션 사이 구분선 (위아래 여백 포함)
st.markdown(
    '<hr style="margin:36px 0 8px 0;border:none;border-top:1px solid #E2E8F0;">',
    unsafe_allow_html=True
)

st.markdown('<div class="section-title">이렇게 사용하세요</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
feats = [
    (f1, "/통계_대시보드", "📊", "통계 대시보드", "세계지도와 차트로 전체 경보 현황을 한눈에"),
    (f2, "/국가_상세", "📋", "국가 정보", "국가별 경보·사건사고·추천 여행지 상세"),
    (f3, "/안전_QnA", "💬", "안전 Q&A", "궁금한 점을 물어보면 근거와 함께 답변"),
]
for col, href, icon, title, desc in feats:
    with col:
        st.markdown(
            f'<a class="feat" href="{href}" target="_self">'
            f'<span class="feat-icon">{icon}</span>'
            f'<span class="feat-title">{title}</span>'
            f'<span class="feat-desc">{desc}</span></a>',
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="footer">데이터 출처 · 외교부 해외안전여행 (0404.go.kr)</div>',
    unsafe_allow_html=True
)