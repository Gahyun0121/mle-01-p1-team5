# =========================================================
# 라이브러리 및 프로젝트 경로 설정
# =========================================================

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from src.sidebar import render_sidebar


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.viz_map import load_alarm, make_alarm_map
from src.alarm_stats import render_alarm_distribution   # 추가: import는 상단에 모음


# =========================================================
# 페이지 제목
# =========================================================

st.title("🌏 통계 대시보드")

st.markdown(
    """
    여행경보와 안전정보 현황을 한눈에 확인하세요.
    """
)
render_sidebar()

# =========================================================
# 데이터 불러오기
# =========================================================

@st.cache_data
def load():
    alarm_path = ROOT_DIR / "data" / "alarm_clean.csv"
    return load_alarm(alarm_path)


@st.cache_data
def load_safety_stats():
    safety_stats_path = ROOT_DIR / "data" / "safety_stats.csv"
    return pd.read_csv(safety_stats_path)


df = load()
safety_info_stats = load_safety_stats()

# 삭제: 여기 있던 st.divider() / render_alarm_distribution() 3줄 제거
#       탭 생성 전이라 화면 맨 위에 그려졌음. tab1 안으로 이동함


# =========================================================
# 월별 안전공지 데이터 불러오기
# =========================================================

@st.cache_data
def load_safety_notice():

    safety_notice_path = (
        ROOT_DIR / "data" / "safety_notice_processed.csv"
    )

    notice_df = pd.read_csv(
        safety_notice_path,
        encoding="utf-8-sig"
    )

    notice_df["안전공지_작성일"] = pd.to_datetime(
        notice_df["안전공지_작성일"],
        errors="coerce"
    )

    notice_df["연도"] = (
        notice_df["안전공지_작성일"]
        .dt.year
        .astype("Int64")
    )

    notice_df["월"] = (
        notice_df["안전공지_작성일"]
        .dt.month
        .astype("Int64")
    )

    return notice_df


notice_df = load_safety_notice()


monthly_continent = (
    notice_df
    .dropna(subset=["대륙명", "연도", "월"])
    .groupby(["연도", "월", "대륙명"])
    .size()
    .reset_index(name="공지건수")
)

# =========================================================
# 대시보드 탭
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "🌍 국가별 여행경보",
    "📊 국가 안전정보 TOP 10",
    "📈 월별 안전공지 추이"
])

# =========================================================
# TAB 1. 국가별 여행경보 지도 + 분포 분석
# =========================================================

with tab1:

    st.subheader("국가별 여행경보 지도")

    st.plotly_chart(
        make_alarm_map(df),
        use_container_width=True
    )

    st.caption(
        "시각적 참고용, 자세한 정보는 "
        "챗봇이나 검색 서비스를 이용해주세요."
    )

    # 추가: 지도 바로 아래에 분포 분석. tab1 안이라 다른 탭에서는 안 보임
    render_alarm_distribution()

# =========================================================
# TAB 2. 연도별 국가 안전정보 TOP 10
# =========================================================

with tab2:

    st.subheader("연도별 국가 안전정보 TOP 10")

    min_year = int(
        safety_info_stats.loc[
            safety_info_stats["year"] >= 2011,
            "year"
        ].min()
    )

    max_year = int(
        safety_info_stats.loc[
            safety_info_stats["year"] >= 2011,
            "year"
        ].max()
    )

    selected_year = st.slider(
        "연도",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        step=1,
        key="top10_year"
    )

    year_data = safety_info_stats[
        safety_info_stats["year"] == selected_year
    ]

    total_count = year_data["count"].sum()

    top10 = (
        year_data
        .nlargest(10, "count")
        .sort_values("count", ascending=True)
    )

    top10_count = top10["count"].sum()

    fig_top10 = px.bar(
        top10,
        x="count",
        y="country_kr",
        orientation="h",
        text="count",
        title=(
            f"{selected_year}년 | "
            f"전체 {total_count}건 · "
            f"TOP10 {top10_count}건"
        )
    )

    fig_top10.update_layout(
        xaxis_title="안전정보 등록 건수",
        yaxis_title="국가",
        showlegend=False,
        height=600
    )

    fig_top10.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_top10,
        use_container_width=True
    )

# =========================================================
# TAB 3. 대륙별 월간 안전공지 추이
# =========================================================

with tab3:

    st.subheader("대륙별 월간 안전공지 추이")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        year_options = (
            ["전체"]
            + sorted(
                monthly_continent["연도"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )
        )

        selected_notice_year = st.selectbox(
            "연도 선택",
            year_options,
            key="notice_year"
        )

    with filter_col2:

        continent_options = (
            ["전체"]
            + sorted(
                monthly_continent["대륙명"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        selected_continent = st.selectbox(
            "대륙 선택",
            continent_options,
            key="notice_continent"
        )

    chart_df = monthly_continent.copy()

    if selected_notice_year != "전체":
        chart_df = chart_df[
            chart_df["연도"] == selected_notice_year
        ]

    if selected_continent != "전체":
        chart_df = chart_df[
            chart_df["대륙명"] == selected_continent
        ]

    chart_df["연월표시"] = chart_df.apply(
        lambda x: (
            f"{str(int(x['연도']))[2:]}년 "
            f"{int(x['월'])}월"
        ),
        axis=1
    )

    fig_notice = px.line(
        chart_df,
        x="연월표시",
        y="공지건수",
        color="대륙명",
        markers=True,
        title="월별 대륙별 안전공지 추이"
    )

    fig_notice.update_layout(
        xaxis_title="연월",
        yaxis_title="안전공지 건수",
        legend_title="대륙",
        hovermode="x unified",
        height=600
    )

    st.plotly_chart(
        fig_notice,
        use_container_width=True
    )