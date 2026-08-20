from pathlib import Path

import pandas as pd

# 0. 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# processed 폴더가 없으면 생성
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# 1. 데이터 불러오기

alarm = pd.read_csv(DATA_DIR / "alarm_clean.csv")
incident = pd.read_csv(DATA_DIR / "incident_info_clean.csv")
safety = pd.read_csv(DATA_DIR / "safety_clean.csv")
notice = pd.read_csv(DATA_DIR / "safety_notice_processed.csv")


# 2. alarm + incident + notice (ISO2 기준 교집합)

alarm_iso2 = set(alarm["ISO 코드"].dropna())
incident_iso2 = set(incident["ISO코드"].dropna())
notice_iso2 = set(notice["ISO코드"].dropna())

common_iso2 = (
    alarm_iso2
    & incident_iso2
    & notice_iso2
)

print("ISO2 공통 국가 수:", len(common_iso2))


# 3. 공통 ISO2 국가의 ISO3 추출 (alarm을 ISO2 ↔ ISO3 연결 기준으로 사용)

alarm_common = alarm[
    alarm["ISO 코드"].isin(common_iso2)
].copy()

alarm_common_iso3 = set(
    alarm_common["iso3"].dropna()
)


# 4. safety와 ISO3 기준 교집합

safety_iso3 = set(safety["iso3"].dropna())

final_iso3 = (
    alarm_common_iso3
    & safety_iso3
)

print("최종 공통 국가 수:", len(final_iso3))


# 5. 최종 ISO3에 대응하는 ISO2 추출

final_codes = (
    alarm[
        alarm["iso3"].isin(final_iso3)
    ][["ISO 코드", "iso3"]]
    .dropna()
    .drop_duplicates()
)

final_iso2 = set(final_codes["ISO 코드"])


# 6. 4개 데이터에 최종 공통 국가만 남기기

alarm_final = alarm[
    alarm["iso3"].isin(final_iso3)
].copy()

incident_final = incident[
    incident["ISO코드"].isin(final_iso2)
].copy()

notice_final = notice[
    notice["ISO코드"].isin(final_iso2)
].copy()

safety_final = safety[
    safety["iso3"].isin(final_iso3)
].copy()


# 7. 결과 검증

alarm_count = alarm_final["iso3"].nunique()
incident_count = incident_final["ISO코드"].nunique()
notice_count = notice_final["ISO코드"].nunique()
safety_count = safety_final["iso3"].nunique()

print("\n=== 최종 국가 수 ===")
print("alarm:", alarm_count)
print("incident:", incident_count)
print("notice:", notice_count)
print("safety:", safety_count)


# 4개 데이터의 국가 수가 동일한지 확인
assert (
    alarm_count
    == incident_count
    == notice_count
    == safety_count
), "4개 데이터의 최종 국가 수가 서로 다릅니다."


# 현재 확인한 기준: 최종 117개
assert alarm_count == 117, (
    f"예상한 117개가 아닙니다. 현재 국가 수: {alarm_count}"
)

print("\n검증 완료: 최종 공통 국가가 정상적으로 추출되었습니다.")


# 8. 최종 국가 목록 확인

final_country_list = (
    alarm_final[
        ["국가명", "ISO 코드", "iso3"]
    ]
    .drop_duplicates()
    .sort_values("국가명")
    .reset_index(drop=True)
)

print("\n=== 최종 공통 국가 목록 ===")
print(final_country_list.to_string(index=False))


# 9. 저장

alarm_final.to_csv(
    PROCESSED_DIR / "alarm_final.csv",
    index=False,
    encoding="utf-8-sig",
)

incident_final.to_csv(
    PROCESSED_DIR / "incident_final.csv",
    index=False,
    encoding="utf-8-sig",
)

safety_final.to_csv(
    PROCESSED_DIR / "safety_final.csv",
    index=False,
    encoding="utf-8-sig",
)

notice_final.to_csv(
    PROCESSED_DIR / "safety_notice_final.csv",
    index=False,
    encoding="utf-8-sig",
)


print("\n=== 저장 완료 ===")
print(PROCESSED_DIR / "alarm_final.csv")
print(PROCESSED_DIR / "incident_final.csv")
print(PROCESSED_DIR / "safety_final.csv")
print(PROCESSED_DIR / "safety_notice_final.csv")