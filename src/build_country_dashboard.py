from pathlib import Path

import pandas as pd


# 0. 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# 1. 데이터 불러오기
alarm = pd.read_csv(PROCESSED_DIR / "alarm_final.csv")
notice = pd.read_csv(PROCESSED_DIR / "safety_notice_final.csv")


# 2. 국가 기본 정보 만들기
country_dashboard = (
    alarm[
        [
            "국가명",
            "영문국가명",
            "ISO 코드",
            "iso3",
            "한글 대륙명",
            "경보단계",
            "경보내용",
        ]
    ]
    .drop_duplicates(subset=["ISO 코드"])
    .copy()
)


# 3. 국가별 안전공지 개수
notice_count = (
    notice
    .groupby("ISO코드")
    .size()
    .reset_index(name="안전공지_총건수")
)


# 4. 최근 안전공지 찾기
notice["안전공지_작성일"] = pd.to_datetime(
    notice["안전공지_작성일"]
)

latest_notice = (
    notice
    .sort_values("안전공지_작성일", ascending=False)
    .drop_duplicates(subset=["ISO코드"])
    [
        [
            "ISO코드",
            "안전공지_작성일",
            "공지제목",
        ]
    ]
)

latest_notice = latest_notice.rename(
    columns={
        "안전공지_작성일": "최근_안전공지일",
        "공지제목": "최근_안전공지제목",
    }
)


# 5. country_dashboard에 안전공지 정보 붙이기
country_dashboard = country_dashboard.merge(
    notice_count,
    left_on="ISO 코드",
    right_on="ISO코드",
    how="left",
)

country_dashboard = country_dashboard.merge(
    latest_notice,
    left_on="ISO 코드",
    right_on="ISO코드",
    how="left",
)


# merge하면서 생긴 중복 ISO코드 제거
country_dashboard = country_dashboard.drop(
    columns=["ISO코드_x", "ISO코드_y"]
)


# 6. 결과 확인
print("국가 수:", country_dashboard["ISO 코드"].nunique())
print("데이터 크기:", country_dashboard.shape)
print("\n컬럼")
print(country_dashboard.columns.tolist())

print("\n미국 데이터")
print(
    country_dashboard[
        country_dashboard["ISO 코드"] == "US"
    ].to_string(index=False)
)


# 7. 저장
country_dashboard.to_csv(
    PROCESSED_DIR / "country_dashboard.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\ncountry_dashboard.csv 저장 완료")