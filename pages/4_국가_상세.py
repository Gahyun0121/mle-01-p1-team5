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

TAG_CLASS = {
    # 재산 범죄
    "소매치기": "tag-property",
    "강도": "tag-property",
    "절도": "tag-property",
    "사기": "tag-property",
    "분실": "tag-property",

    # 신체·강력 범죄
    "납치": "tag-violence",
    "성범죄": "tag-violence",
    "폭행": "tag-violence",
    "살인": "tag-violence",

    # 사회적 위험
    "마약": "tag-social",
    "테러": "tag-social",
    "시위": "tag-social",

    # 사고
    "교통사고": "tag-accident",

    # 재난·보건
    "자연재해": "tag-disaster",
    "감염병": "tag-disaster",
}

st.markdown("""
<style>
.card{background:#fff;border:1px solid #E5E7EB;border-radius:12px;
      padding:16px 18px;margin-bottom:14px;}
.rec-card{
    background:#fff;
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:16px 18px;
    margin-bottom:14px;
    box-sizing:border-box;
    overflow:hidden;
}
.card-title{font-size:14px;font-weight:600;color:#111827;margin-bottom:12px;}
.section-title{
    font-size:14px;
    font-weight:600;
    color:#111827;
    margin-top:12px;
    margin-bottom:10px;
    padding-left:9px;
    border-left:3px solid #2563EB;
}
.m-label{font-size:13px;color:#6B7280;margin-bottom:6px;}
.m-value{font-size:26px;font-weight:700;line-height:1.2;}
.alarm-row{
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:8px;
}
.alarm-row:last-child{
    margin-bottom:0;
}
.badge{
    display:inline-flex;
    align-items:center;
    justify-content:center;

    padding:5px 10px;
    border-radius:7px;

    font-size:12px;
    font-weight:600;
    white-space:nowrap;

    min-width:48px;
    flex-shrink:0;
    box-sizing:border-box;
}

.alarm-text{
    font-size:13px;
    color:#374151;
    line-height:1.65;
    word-break:keep-all;
}
.tag{
    display:inline-block;
    border:1px solid #E5E7EB;
    border-radius:8px;
    padding:5px 12px;
    font-size:13px;
    color:#374151;
    margin:0 7px 7px 0;
    background:#fff;
}

/* 재산 범죄 - 파랑 */
.tag-property{
    background:#EFF6FF;
    color:#1D4ED8;
    border-color:#BFDBFE;
}

/* 신체·강력 범죄 - 빨강 */
.tag-violence{
    background:#FEF2F2;
    color:#B91C1C;
    border-color:#FECACA;
}

/* 사회적 위험 - 주황 */
.tag-social{
    background:#FFF7ED;
    color:#C2410C;
    border-color:#FED7AA;
}

/* 사고 - 노랑 */
.tag-accident{
    background:#FEFCE8;
    color:#A16207;
    border-color:#FEF08A;
}

/* 재난·보건 - 초록 */
.tag-disaster{
    background:#F0FDF4;
    color:#15803D;
    border-color:#BBF7D0;
}
.rec-content{
    margin-top:12px;
    display:flex;
    flex-wrap:wrap;
    align-items:flex-start;
    align-content:flex-start;
    gap:8px;
}
.rec-content .tag{
    margin:0;
}
.safety-card{
    background:#fff;
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:14px 18px 18px 18px;
    margin-bottom:14px;
    box-sizing:border-box;
    overflow:hidden;
}
.news{font-size:13px;color:#374151;margin-bottom:7px;}
.news-date {
    display: inline-block;
    width: 85px;
    color: #94a3b8;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


def card(title, body):
    """제목 + 내용을 흰 박스로 감싸는 함수. 박스가 4개라 함수로 뺌"""
    st.markdown(
        f'<div class="card"><div class="card-title">{title}</div>{body}</div>',
        unsafe_allow_html=True,
    )

def safety_card(title, body, height):
    st.markdown(
        f'''
        <div class="safety-card" style="height:{height}px;">
            <div class="card-title">{title}</div>
            {body}
        </div>
        ''',
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
추천 = C.get_recommendations(iso3)



# 상단 3칸
단계 = 요약["경보단계"]
배경색, 글자색 = LEVEL_COLOR.get(단계, ("#F3F4F6", "#374151"))

c1, c2, c3 = st.columns(3)

# 경보단계
with c1:
    st.markdown(
        f'''
        <div class="card" style="
            background:{배경색};
            border-color:{글자색}40;
        ">
            <div class="m-label">경보단계</div>
            <div class="m-value" style="color:{글자색}">
                {단계}단계
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# 안전공지
with c2:
    st.markdown(
        f'''
        <div class="card" style="
            background:#F8FAFC;
            border-color:#CBD5E1;
        ">
            <div class="m-label">안전공지</div>
            <div class="m-value">
                {요약["공지수"]}건
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# 주요 사건사고
with c3:
    대표태그 = 태그[0] if 태그 else "자료 없음"

    st.markdown(
        f'''
        <div class="card" style="
            background:#FFF7ED;
            border-color:#FED7AA;
        ">
            <div class="m-label">주요 사건사고 유형</div>
            <div class="m-value" style="color:#C2410C;">
                {대표태그}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# 여행 추천 정보 - 추천 데이터가 있는 국가만 표시

if 추천:
    # 추천 정보 양에 따라 카드 높이 조절
    # 추천 정보 카드 높이 계산
    도시개수 = len(추천["도시"])
    테마개수 = len(추천["테마"])
    월개수 = len(추천["월"])

    # 대략적인 줄 수 계산
    도시줄 = 1 if 도시개수 <= 3 else 2

    테마줄 = 1 if 테마개수 <= 5 else 2

    월줄 = 1 if 월개수 <= 7 else 2

    # 세 카드 중 가장 많은 줄 수 기준
    최대줄 = max(도시줄, 테마줄, 월줄)

    if 최대줄 == 1:
        rec_height = 110
    else:
        rec_height = 140

# 여행 추천 정보 제목

    st.markdown(
        '<div class="section-title">여행 추천 정보</div>',
        unsafe_allow_html=True
    )

    r1, r2, r3 = st.columns(3)


    # 추천 도시
    with r1:
        도시 = " · ".join(추천["도시"])

        st.markdown(
            f'''
            <div class="rec-card" style="height:{rec_height}px;">
                <div class="m-label">추천 도시</div>
                <div class="rec-content"
                    style="font-size:14px;color:#374151;">
                    {도시}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # 추천 테마
    with r2:
        테마태그 = "".join(
            f'<span class="tag">#{t}</span>'
            for t in 추천["테마"]
        )

        st.markdown(
            f'''
            <div class="rec-card" style="height:{rec_height}px;">
                <div class="m-label">추천 테마</div>
                <div class="rec-content">
                    {테마태그}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # 추천 시기
    with r3:
        MONTH_KR = {
            "Jan": "1월",
            "Feb": "2월",
            "Mar": "3월",
            "Apr": "4월",
            "May": "5월",
            "Jun": "6월",
            "Jul": "7월",
            "Aug": "8월",
            "Sep": "9월",
            "Oct": "10월",
            "Nov": "11월",
            "Dec": "12월",
        }

        월목록 = [
            MONTH_KR.get(m, m)
            for m in 추천["월"]
        ]

        월목록 = sorted(
            set(월목록),
            key=lambda x: int(x.replace("월", ""))
        )

        월태그 = "".join(
        f'<span class="tag">{m}</span>'
        for m in 월목록
    )

        st.markdown(
            f'''
            <div class="rec-card" style="height:{rec_height}px;">
                <div class="m-label">추천 시기</div>
                <div class="rec-content">
                    {월태그}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )


# 여행 안전 정보 제목

st.markdown(
    '<div class="section-title">여행 안전 정보</div>',
    unsafe_allow_html=True
)


# 지역별 여행경보 내용량에 따라 카드 높이 계산

# 지역별 여행경보 예상 줄 수 계산
import math

예상줄수 = 0

for 내용 in 지역표["경보내용"].fillna("").astype(str):
    예상줄수 += max(1, math.ceil(len(내용) / 75))

경보개수 = len(지역표)

전체글자수 = (
    지역표["경보내용"]
    .fillna("")
    .astype(str)
    .str.len()
    .sum()
)

safety_height = (
    55                  # 제목 + 위아래 여백
    + 예상줄수 * 24      # 실제 텍스트 줄
    + 경보개수 * 8       # 경보 행 사이 간격
)

# 내용이 아주 짧으면 카드도 작게
if 경보개수 == 1 and 전체글자수 <= 30:
    safety_height = 95
else:
    safety_height = max(120, min(safety_height + 20, 230))


# 지역별 여행경보 + 사건사고 유형
left_col, right_col = st.columns(2)


# 왼쪽: 지역별 여행경보
with left_col:
    if 지역표.empty:
        safety_card(
            "지역별 여행경보",
            '<div class="alarm-text">외교부 여행경보 미지정 국가</div>',
            safety_height
        )

    else:
        rows = ""

        for _, r in 지역표.iterrows():
            bg, fg = LEVEL_COLOR.get(
                int(r["경보단계"]),
                ("#F3F4F6", "#374151")
            )

            rows += (
                f'<div class="alarm-row">'
                f'<span class="badge" style="background:{bg};color:{fg}">'
                f'{int(r["경보단계"])}단계</span>'
                f'<span class="alarm-text">{r["경보내용"]}</span>'
                f'</div>'
            )

        safety_card(
            "지역별 여행경보",
            rows,
            safety_height
        )


# 오른쪽: 사건사고 유형
with right_col:
    if 태그:
        태그_html = "".join(
            f'<span class="tag {TAG_CLASS.get(t, "")}">{t}</span>'
            for t in 태그
        )

        safety_card(
            "사건사고 유형",
            태그_html,
            safety_height
        )

    else:
        safety_card(
            "사건사고 유형",
            '<div class="alarm-text">자료 없음</div>',
            safety_height
        )


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