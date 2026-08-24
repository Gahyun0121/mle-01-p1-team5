"""
경보단계 분포 분석 (전체 국가 vs 서비스 대상 43개국)
"""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]          # 변경: 상대경로 → 루트 기준 절대경로
ALARM_PATH = ROOT_DIR / "data" / "raw" / "alarm.json"
MASTER_PATH = ROOT_DIR / "data" / "country_master.csv"

STAGE_LABEL = {1: "1단계\n여행유의", 2: "2단계\n여행자제", 3: "3단계\n출국권고", 4: "4단계\n여행금지"}


@st.cache_data
def load_alarm_stats():
    """여행경보 + 국가매칭표를 읽어 국가 단위로 정리"""
    # json.load 사용: pd.read_json은 'NA'(나미비아)를 NaN으로 바꿔버림
    with open(ALARM_PATH, encoding="utf-8") as f:
        alarm = pd.DataFrame(json.load(f))

    alarm.columns = [c.strip() for c in alarm.columns]   # 컬럼명에 공백 섞여 있음
    alarm = alarm.rename(columns={"ISO 코드": "iso2", "한글 대륙명": "continent"})

    alarm["iso2"] = alarm["iso2"].astype(str).str.strip()
    alarm["경보단계"] = pd.to_numeric(alarm["경보단계"], errors="coerce")
    alarm = alarm[alarm["경보단계"].between(1, 4)]

    # 국가별 여러 행(태국 3행 등) → 대표값은 최댓값. 지도와 동일 규칙
    country = (
        alarm.groupby(["iso2", "국가명"], as_index=False)
        .agg(경보단계=("경보단계", "max"), continent=("continent", "first"))
    )

    # keep_default_na=False: 'NA'(나미비아 iso2)가 NaN 되는 것 방지
    # encoding='utf-8-sig': 첫 컬럼에 BOM 있음
    master = pd.read_csv(MASTER_PATH, keep_default_na=False, encoding="utf-8-sig")
    master["iso2"] = master["iso2"].str.strip()

    country["대상"] = country["iso2"].isin(set(master["iso2"]))

    # 추가: 경보가 아예 없는 대상국 = 미지정. 외교부는 경보 걸린 나라만 목록에 올림
    matched = set(country.loc[country["대상"], "iso2"])
    unlisted = master[~master["iso2"].isin(matched)]

    return country, master, unlisted


def render_alarm_distribution():
    country, master, unlisted = load_alarm_stats()
    target = country[country["대상"]]
    n_target = len(master)

    st.markdown("---")
    st.subheader("추천 국가 안전도 한눈에 보기")

    with st.expander("여행지 추천이 가능한 국가 보기"):
        st.caption(" · ".join(sorted(master["country_kr"])))


    # ── 1. 경보단계별 스택 막대 ────────────────────────────────
    # 변경: 그룹 막대(분모 다름) → 스택 막대(각 단계 안에서의 비중)
    stack = (
        country.assign(구분=lambda d: d["대상"].map({True: f"추천 {n_target}개국", False: "그 외"}))
        .groupby(["경보단계", "구분"], as_index=False)
        .size()
        .rename(columns={"size": "국가수"})
    )
    stack["단계명"] = stack["경보단계"].map(STAGE_LABEL)

    fig = px.bar(
        stack.sort_values("경보단계"),
        x="단계명", y="국가수", color="구분",
        text="국가수",
        labels={"단계명": "", "국가수": "국가 수"},
        color_discrete_map={f"추천 {n_target}개국": "#2E86DE", "그 외": "#D5DAE0"},
        category_orders={"구분": [f"추천 {n_target}개국", "그 외"]},
    )
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(height=400, legend_title_text="", barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

    # ── 2. 핵심 수치 ─────────────────────────────────────────
    risky = target[target["경보단계"] >= 2]
    lv4 = country[country["경보단계"] == 4]
    lv4_target = int(lv4["대상"].sum())

    c1, c2, c3 = st.columns(3)
    # 추가: 경보 미지정 국가 수. 51.6% 왜곡의 원인이었던 부분
    c1.metric("경보 미지정 (가장 안전)", f"{len(unlisted)}개국",
              help="여행경보가 지정되지 않은 국가. 외교부는 경보가 걸린 나라만 고시함")
    c2.metric("4단계 국가 중 추천 포함", f"{lv4_target} / {len(lv4)}개국")
    c3.metric(f"추천 {n_target}개국 중 주의 필요", f"{len(risky)}개국")

    st.caption(
        f"추천 {n_target}개국은 관광 목적지 위주라 경보 단계가 낮은 편입니다. "
        f"다만 아래 {len(risky)}개국은 2단계 이상이므로 방문 전 확인이 필요합니다."
    )

    # ── 3. 대상국 내부에서 갈리는 지점 ────────────────────────
    if len(risky):
        show = (
            risky.sort_values("경보단계", ascending=False)[["국가명", "continent", "경보단계"]]
            .rename(columns={"continent": "대륙"})
        )
        show["경보단계"] = show["경보단계"].map(lambda x: STAGE_LABEL[x].replace("\n", " "))
        st.dataframe(show, hide_index=True, use_container_width=True)