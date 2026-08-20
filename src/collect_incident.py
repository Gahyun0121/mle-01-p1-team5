import os
from dotenv import load_dotenv
import requests
import pandas as pd
from io import BytesIO
import json

load_dotenv()

API_KEY = os.getenv("GONGGONG_API_KEY")  # .env 생성 후 자기 키 변수명 넣기


def get_incident_info(page_no=1, rows_num=100):
    """API 호출해서 JSON 반환"""
    endpoint_url = (
        "https://apis.data.go.kr/1262000/CountryAccidentService2/CountryAccidentService2" # 자기 API 주소 + 상세기능명으로 교체
    )
    params = {
        "ServiceKey": API_KEY,
        "returnType": "JSON",
        "numOfRows": rows_num,
        "pageNo": page_no}

    try:
        response = requests.get(endpoint_url, params=params)

    except requests.exceptions.RequestException as e:
        print(f"요청에 실패했습니다.: {e}")
        return None

    if response.status_code == 200:
        # print(response.text[:300])
        return response

    print("에러:", response.status_code, "-", response.text[:100])
    return None


os.makedirs("./incident_data", exist_ok=True)

country_data = []

for p in range(1, 2): # totalCount 198건이라 1000개 요청 시 1페이지만 필요
    
    r = get_incident_info(
        page_no=p,
        rows_num=1000
        )
    
    if r is None:
        continue

    data = r.json()

    items = (
        data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
    )

    for row in items:
        country_data.append( # 자기 데이터 컬럼으로 전체 교체
            {
                "국가명": row.get("country_nm"),
                "영문국가명": row.get("country_eng_nm"),
                "ISO코드": row.get("country_iso_alp2"),
                "대륙코드": row.get("continent_cd"),
                "대륙명": row.get("continent_nm"),
                "영문대륙명": row.get("continent_eng_nm"),
                "사건사고내용": row.get("news"),
                "작성일": row.get("wrt_dt"),
                "위험지도": row.get("dang_map_download_url"),
                "국기": row.get("flag_download_url"),
                "지도": row.get("map_download_url"),
            }
        )

# JSON 저장
with open(
    "./incident_data/incident_info.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        country_data,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"총 {len(country_data)}건 수집 완료")