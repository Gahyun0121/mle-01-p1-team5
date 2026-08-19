import re
import pandas as pd


# ==================================================
# 0. 데이터 불러오기
# ==================================================

incident = pd.read_json("./incident_data/incident_info.json")


# ==================================================
# 1. incident 기본 전처리
# ==================================================

# 필요한 컬럼만 선택
df_use = incident[[
    "국가명",
    "영문국가명",
    "ISO코드",
    "대륙명",
    "작성일",
    "사건사고내용"
]].copy()


# HTML 태그 및 불필요한 공백 제거
def clean_incident_text(text):

    # 결측치 처리
    if pd.isna(text):
        return ""

    # 1. 줄바꿈 역할을 하는 HTML 태그를 실제 줄바꿈으로 변경
    text = re.sub(
        r"<br\s*/?>|</p>|</div>|</li>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # 2. 나머지 HTML 태그 제거
    text = re.sub(r"<[^>]+>", " ", text)

    # 3. 줄바꿈이 아닌 공백 정리
    text = re.sub(r"[ \t]+", " ", text)

    # 4. 줄마다 앞뒤 공백 제거
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # 5. 다시 줄바꿈으로 연결
    return "\n".join(lines)


# 사건사고 내용 전처리
df_use["사건사고내용_clean"] = (
    df_use["사건사고내용"]
    .apply(clean_incident_text)
)


# 작성일 날짜형 변환
df_use["작성일"] = pd.to_datetime(
    df_use["작성일"],
    errors="coerce"
)


# 작성일 컬럼명 변경
df_use = df_use.rename(
    columns={
        "작성일": "사건사고_작성일"
    }
)


# ==================================================
# 2. 전처리 결과 확인
# ==================================================

# 데이터 타입 확인
print("\n=== 데이터 타입 ===")
print(df_use.dtypes)


# HTML 전처리 결과 확인
print("\n=== 전처리 전 ===")
print(df_use["사건사고내용"].iloc[0])

print("\n=== 전처리 후 ===")
print(df_use["사건사고내용_clean"].iloc[0])


# 날짜 확인
print("\n=== 작성일 범위 ===")
print("최초 작성일:", df_use["사건사고_작성일"].min())
print("최근 작성일:", df_use["사건사고_작성일"].max())


# 날짜 최신순 확인
print("\n=== 최근 작성 데이터 ===")
print(
    df_use.sort_values(
        "사건사고_작성일",
        ascending=False
    )[[
        "국가명",
        "사건사고_작성일"
    ]].head(10)
)


# 결측치 확인
print("\n=== 결측치 ===")
print(df_use.isna().sum())


# 중복 데이터 확인
print("\n=== 중복 데이터 ===")
print(df_use.duplicated().sum())


# 최종 데이터 크기 확인
print("\n=== 최종 데이터 크기 ===")
print(df_use.shape)


# 전체 국가 확인
print("\n=== 전체 사용 국가 ===")
print(df_use["국가명"].unique())

print("\n전체 국가 수:")
print(df_use["국가명"].nunique())


# 앞부분 확인
print("\n=== 전처리 결과 샘플 ===")
print(
    df_use[[
        "국가명",
        "ISO코드",
        "사건사고_작성일",
        "사건사고내용_clean"
    ]].head()
)


# 국가 하나 골라 사건사고 내용 확인
country = df_use["국가명"].iloc[0]

print(f"\n=== {country} 사건사고 내용 ===")
print(
    df_use.loc[
        df_use["국가명"] == country,
        "사건사고내용_clean"
    ].iloc[0]
)


# ==================================================
# 3. 최종 데이터
# ==================================================

df_final = df_use[[
    "국가명",
    "영문국가명",
    "ISO코드",
    "대륙명",
    "사건사고_작성일",
    "사건사고내용_clean"
]].copy()


# 최종 컬럼 확인
print("\n=== 최종 컬럼 ===")
print(df_final.columns.tolist())

print("\n=== 최종 크기 ===")
print(df_final.shape)


# ==================================================
# 4. 저장
# ==================================================

df_final.to_csv(
    "./incident_data/incident_info_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n저장 완료: ./incident_data/incident_info_clean.csv")