import pandas as pd
import plotly.express as px

csv_path = "data/alarm_clean.csv"

keys = ["iso3", "국가명", "한글 대륙명"]

rest_region = "제외한|전 지역|전지역|이외"

manual = {
    "EGY": 1,
    "RUS": 0, "COD": 0, "ROU": 0, "BOL": 0,
    "SAU": 0, "ETH": 0, "JOR": 0, "JPN": 0,
}

iso3_fix = {"코소보": "XKX"}

labels = {0: "세부 경보 확인 필요", 1: "1단계", 2: "2단계", 3: "3단계", 4: "4단계"}

colors = {
    "세부 경보 확인 필요": "#7BCE81",
    "1단계": "#6EC1E4",      # 남색: 여행유의
    "2단계": "#F7C948",      # 황색: 여행자제
    "3단계": "#EF6C3D",      # 적색: 출국권고
    "4단계": "#C62828",      # 흑색: 여행금지
}

order = ["세부 경보 확인 필요", "1단계", "2단계", "3단계", "4단계"]


def load_alarm(path=csv_path):
    """경보 데이터 읽고 iso3 빈 값 보정"""
    df = pd.read_csv(path)
    df["iso3"] = df["iso3"].fillna(df["국가명"].map(iso3_fix))
    return df.dropna(subset=["iso3"])


def get_base_level(df):
    """국가별 대표 경보단계 뽑기 (base = 대부분 지역 기준)"""
    
    is_base = df["경보내용"].str.contains(rest_region, na=False)
    base = df[is_base].groupby(keys, as_index=False)["경보단계"].min()
    rest = df[~df["iso3"].isin(base["iso3"])].groupby(keys, as_index=False)["경보단계"].min()
    rest["경보단계"] = rest["iso3"].map(manual).fillna(0).astype(int)

    return pd.concat([base, rest], ignore_index=True)


def make_hover(g, max_len=45):
    """hover용 요약 텍스트, 길면 자르기"""
    g = g.sort_values("경보단계", ascending=False)
    lines = []
    for r in g.itertuples():
        txt = str(r.경보내용)
        if len(txt) > max_len:
            txt = txt[:max_len] + "…"
        lines.append(f"{r.경보단계}단계 · {txt}")

    # 특별여행주의보 언급 있으면 안내 문구 추가
    if g["경보내용"].str.contains("특별여행주의보").any():
        lines.append("<b>※ 특별여행주의보는 별도 제도로 미포함</b>")
        
    return "<br>".join(lines)


def make_alarm_map(df):
    rep = get_base_level(df)

    hover = df.groupby("iso3").apply(make_hover, include_groups=False).rename("지역별")
    rep = rep.merge(hover, on="iso3")

    rep["단계"] = rep["경보단계"].map(labels)

    fig = px.choropleth(
        rep,
        locations="iso3",
        locationmode="ISO-3",
        color="단계",
        color_discrete_map=colors,
        category_orders={"단계": order},      # 범례 순서 고정
        hover_name="국가명",
        custom_data=["단계", "한글 대륙명", "지역별"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b> · %{customdata[1]}<br>"
            "대표: %{customdata[0]}<br><br>"
            "%{customdata[2]}"
            "<extra></extra>"
        )
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="white",
        showframe=False,
        landcolor="#E8E8E8",              # 경보 데이터 없는 나라
        projection_type="natural earth",
    )

    fig.update_layout(
        title="국가별 여행경보 단계 (대부분 지역 기준)",
        legend_title="경보단계",
        margin=dict(l=0, r=0, t=45, b=0),
    )

    return fig


if __name__ == "__main__":
    df = load_alarm()
    rep = get_base_level(df)

    print("국가 수:", len(rep))
    print(rep["경보단계"].value_counts().sort_index().to_string())

    make_alarm_map(df).write_html("alarm_map.html")
    print("→ alarm_map.html 생성 완료")