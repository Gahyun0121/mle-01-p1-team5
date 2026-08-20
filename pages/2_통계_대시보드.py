# =========================================================
# 라이브러리 및 프로젝트 경로 설정
# =========================================================

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# 현재 파일(pages/2_통계_대시보드.py)을 기준으로
# 한 단계 위의 프로젝트 루트(mle-01-p1-team5)를 가져옴
ROOT_DIR = Path(__file__).resolve().parents[1]

# pages 폴더에서 Streamlit을 직접 실행해도
# 프로젝트 루트의 src 모듈을 import할 수 있도록 경로 추가
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# 여행경보 지도 생성에 필요한 함수 import
from src.viz_map import load_alarm, make_alarm_map


# =========================================================
# 페이지 제목
# =========================================================

st.title("🌏 통계 대시보드")

st.markdown(
    """
    여행경보와 안전정보 현황을 한눈에 확인하세요.
    """
)

# =========================================================
# 데이터 불러오기
# =========================================================

# 여행경보 지도 데이터
# Streamlit이 재실행될 때마다 CSV를 다시 읽지 않도록 캐싱
@st.cache_data
def load():
    alarm_path = ROOT_DIR / "data" / "alarm_clean.csv"
    return load_alarm(alarm_path)


# 연도별 국가 안전정보 TOP10 데이터
@st.cache_data
def load_safety_stats():
    safety_stats_path = ROOT_DIR / "data" / "safety_stats.csv"
    return pd.read_csv(safety_stats_path)


# 데이터 로드
df = load()
safety_info_stats = load_safety_stats()

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

    # 작성일을 날짜형으로 변환
    notice_df["안전공지_작성일"] = pd.to_datetime(
        notice_df["안전공지_작성일"],
        errors="coerce"
    )

    # 연도 / 월 생성
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


# 데이터 로드
notice_df = load_safety_notice()


# 월별 · 대륙별 안전공지 건수 집계
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
# TAB 1. 국가별 여행경보 지도
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

    # =========================================================
# TAB 2. 연도별 국가 안전정보 TOP 10
# =========================================================

with tab2:

    st.subheader("연도별 국가 안전정보 TOP 10")

    # -------------------------
    # 연도 선택 슬라이더
    # -------------------------

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

    # -------------------------
    # 선택 연도 데이터
    # -------------------------

    year_data = safety_info_stats[
        safety_info_stats["year"] == selected_year
    ]

    total_count = year_data["count"].sum()

    # TOP 10
    top10 = (
        year_data
        .nlargest(10, "count")
        .sort_values("count", ascending=True)
    )

    top10_count = top10["count"].sum()

    # -------------------------
    # 막대그래프
    # -------------------------

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

    # -------------------------
    # 연도 / 대륙 선택
    # -------------------------

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

    # -------------------------
    # 선택 조건 적용
    # -------------------------

    chart_df = monthly_continent.copy()

    if selected_notice_year != "전체":
        chart_df = chart_df[
            chart_df["연도"] == selected_notice_year
        ]

    if selected_continent != "전체":
        chart_df = chart_df[
            chart_df["대륙명"] == selected_continent
        ]

    # 연월 표시
    chart_df["연월표시"] = chart_df.apply(
        lambda x: (
            f"{str(int(x['연도']))[2:]}년 "
            f"{int(x['월'])}월"
        ),
        axis=1
    )

    # -------------------------
    # 선 그래프
    # -------------------------

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