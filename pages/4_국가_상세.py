import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import src.country_detail as C

st.set_page_config(page_title="국가 상세", layout="wide")

# 경보단계별 (배경색, 글자색)
LEVEL_COLOR = {
    1: ("#E8F0FE", "#1A56DB"),   # 파랑
    2: ("#FEF3C7", "#92400E"),   # 노랑
    3: ("#FFEDD5", "#C2410C"),   # 주황
    4: ("#FEE2E2", "#B91C1C"),   # 빨강
}

st.markdown("""
<style>
.card{background:#fff;border:1px solid #E5E7EB;border-radius:12px;
      padding:16px 18px;margin-bottom:14px;}
.card-title{font-size:14px;font-weight:600;color:#111827;margin-bottom:12px;}
.m-label{font-size:13px;color:#6B7280;margin-bottom:6px;}
.m-value{font-size:26px;font-weight:700;line-height:1.2;}
.badge{display:inline-block;padding:2px 9px;border-radius:6px;
       font-size:12px;font-weight:600;margin-right:10px;}
.alarm-row{display:flex;align-items:center;margin-bottom:9px;}
.alarm-text{font-size:13px;color:#374151;}
.tag{display:inline-block;border:1px solid #E5E7EB;border-radius:8px;
     padding:5px 12px;font-size:13px;color:#374151;margin:0 7px 7px 0;
     background:#fff;}
.news{font-size:13px;color:#374151;margin-bottom:7px;}
.news-date{color:#9CA3AF;margin-right:8px;}
</style>
""", unsafe_allow_html=True)


def card(title, body):
    """제목 + 내용을 흰 박스로 감싸는 함수. 박스가 4개라 함수로 뺌"""
    st.markdown(
        f'<div class="card"><div class="card-title">{title}</div>{body}</div>',
        unsafe_allow_html=True,
    )


# 국가 선택
목록 = C.get_country_list()
라벨, iso3 = st.selectbox(
    f"국가 선택 ({len(목록)}개국)",
    options=목록,
    format_func=lambda x: x[0],
)

요약 = C.get_summary(iso3)
대표, 지역표 = C.get_alarms(iso3)
태그 = C.get_tags(iso3)
뉴스 = C.get_news(iso3)


# 상단 3칸
단계 = 요약["경보단계"]
_, 글자색 = LEVEL_COLOR.get(단계, ("#F3F4F6", "#374151"))

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f'<div class="card"><div class="m-label">경보단계</div>'
        f'<div class="m-value" style="color:{글자색}">{단계}단계</div></div>',
        unsafe_allow_html=True)

with c2:
    st.markdown(
        f'<div class="card"><div class="m-label">안전공지</div>'
        f'<div class="m-value">{요약["공지수"]}건</div></div>',
        unsafe_allow_html=True)

with c3:
    대표태그 = 태그[0] if 태그 else "자료 없음"
    st.markdown(
        f'<div class="card"><div class="m-label">주요 사건사고</div>'
        f'<div class="m-value">{대표태그}</div></div>',
        unsafe_allow_html=True)


# 지역별 여행경보
if 지역표.empty:
    card("지역별 여행경보", '<div class="alarm-text">외교부 여행경보 미지정 국가</div>')
else:
    rows = ""
    for _, r in 지역표.iterrows():
        bg, fg = LEVEL_COLOR.get(int(r["경보단계"]), ("#F3F4F6", "#374151"))
        rows += (f'<div class="alarm-row">'
                 f'<span class="badge" style="background:{bg};color:{fg}">'
                 f'{int(r["경보단계"])}단계</span>'
                 f'<span class="alarm-text">{r["경보내용"]}</span></div>')
    card("지역별 여행경보", rows)


# 사건사고 유형
if 태그:
    card("사건사고 유형", "".join(f'<span class="tag">{t}</span>' for t in 태그))
else:
    card("사건사고 유형", '<div class="alarm-text">자료 없음</div>')


# 최신 안전공지
if 뉴스.empty:
    card("최신 안전공지", '<div class="alarm-text">자료 없음</div>')
else:
    items = "".join(
        f'<div class="news"><span class="news-date">{r["안전공지_작성일"]}</span>'
        f'{r["공지제목"]}</div>'
        for _, r in 뉴스.iterrows())
    card("최신 안전공지", items)


# 하단 챗봇 링크
left, right = st.columns([3, 1])
with left:
    st.markdown('<div style="padding-top:8px;color:#6B7280;font-size:14px;">'
                '더 궁금한 점이 있나요?</div>', unsafe_allow_html=True)
with right:
    st.page_link("pages/3_챗봇.py", label="챗봇에게 물어보기 →")