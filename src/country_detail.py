import pandas as pd
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "data" / "processed"
DEST = ROOT / "data"

KEYWORDS = ["소매치기","강도","절도","납치","성범죄","마약","사기",
            "테러","시위","교통사고","분실","폭행","자연재해","감염병","살인"]

@st.cache_data
def load_all():
    cd  = pd.read_csv(BASE / "country_dashboard.csv")
    al  = pd.read_csv(BASE / "alarm_final.csv")
    inc = pd.read_csv(BASE / "incident_final.csv")
    sn  = pd.read_csv(BASE / "safety_notice_final.csv")
    de  = pd.read_csv(DEST / "destinations_clean.csv")

    iso2to3 = cd.set_index("ISO 코드")["iso3"].to_dict()

    inc["iso3"] = inc["ISO코드"].map(iso2to3)
    sn["iso3"]  = sn["ISO코드"].map(iso2to3)

    return cd, al, inc, sn, de

cd, al, inc, sn, de = load_all()

def get_country_list():
    """드롭다운용 117개국, (표시이름, iso3) 리스트"""
    safe = cd[['국가명', 'iso3']].sort_values('국가명')
    safe['label'] = safe['국가명'] + " (" + safe['iso3'] + ")"

    # 추천 정보 o, 안전 정보 x
    only_rec = de[~de['iso3'].isin(cd['iso3'])].dropna(subset=['iso3'])
    only_rec = only_rec[['country_kr','iso3']].drop_duplicates()
    only_rec.columns = ['국가명','iso3']
    only_rec['label'] = only_rec['국가명'] + " (추천전용)"

    both = pd.concat([safe, only_rec]).sort_values('국가명')

    return list(zip(safe['국가명'], safe['iso3']))

def get_summary(iso3):
    """상단 3칸, 없으면 None 반환"""
    hit = cd[cd['iso3'] == iso3]


    if hit.empty:
        return None
    
    r = hit.iloc[0]

    return {
        "국가명": r["국가명"],
        "경보단계": int(r["경보단계"]),
        "공지수": int(r["안전공지_총건수"])
    }

def get_alarms(iso3):
    """대표 경보 + 지역별 목록, 없으면 (None, 빈 표) 반환"""
    a = al[al['iso3'] == iso3].sort_values("경보단계", ascending=False)

    if a.empty:
        return None, a

    top = a.iloc[0]
    대표 = f"{top['경보단계']}단계: {top['경보내용']}"

    return 대표, a[['경보단계','경보내용']]

def get_tags(iso3, n=5):
    """사건사고 태그, 등장 횟수 많은 순 최대 n개, 없으면 빈 리스트 반환"""
    hit = inc[inc['iso3'] == iso3]

    if hit.empty:
        return []

    text = str(hit['사건사고내용_clean'].iloc[0])
    counts = {k: text.count(k) for k in KEYWORDS if text.count(k) > 0}
    return sorted(counts, key=counts.get, reverse=True)[:n]

def get_news(iso3, n=5):
    """최근 안전공지 n개, 없으면 빈 표 반환"""
    hit = sn[sn["iso3"] == iso3].sort_values("안전공지_작성일", ascending=False)

    hit = hit.drop_duplicates(subset=["공지제목", "안전공지_작성일"], keep="first")

    return hit.head(n)[["안전공지_작성일", "공지제목"]]

def get_recommendations(iso3):
    """캐글 추천 정보, 없으면 None 반환"""
    d = de[de["iso3"] == iso3]

    if d.empty:
        return None

    도시 = sorted(d["city"].dropna().unique().tolist())

    테마 = sorted(
        set(
            d["themes"]
            .dropna()
            .str.split("|")
            .explode()
        )
    )

    월 = sorted(
        set(
            d["months"]
            .dropna()
            .str.split("|")
            .explode()
        )
    )

    return {
        "도시": 도시,
        "테마": 테마,
        "월": 월
    }