import os
from dotenv import load_dotenv
import requests
import pandas as pd
from io import BytesIO
import json

load_dotenv()

API_KEY = os.getenv("GONGGONG_API_KEY")


def get_safety_info(page_no=1, rows_num=100):
    """API 호출해서 DataFrame 반환"""
    endpoint_url = (
        "https://apis.data.go.kr/1262000/CountrySafetyService/getCountrySafetyList"
    )
    params = {"serviceKey": API_KEY, "numOfRows": rows_num, "pageNo": page_no}

    try:
        response = requests.get(endpoint_url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"요청에 실패했습니다.: {e}")
        return None

    if response.status_code == 200:
        return response

    print("에러:", response.status_code, "-", response.text[:100])
    return None


os.makedirs("data/raw", exist_ok=True)

ROWS = 1000

country_data = []
for p in range(1, 7): 
    r = get_safety_info(page_no=p, rows_num=1000)
    df = pd.read_xml(BytesIO(r.content), xpath=".//item")
    for _, row in df.iterrows():
        country_data.append( 
            {
                "국가명": row["countryName"],
                "영문국가명": row["countryEnName"],
                "id": row["id"],
                "제목": row["title"],
                "내용": row["content"],
                "작성일": row["wrtDt"],
                "첨부파일": row["fileUrl"],
            }
        )

with open("data/raw/safety_info.json", "w", encoding="utf-8") as f:
    json.dump(country_data, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {len(country_data)}건")