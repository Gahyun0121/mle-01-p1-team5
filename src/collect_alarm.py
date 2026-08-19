import os
from dotenv import load_dotenv
import requests
import pandas as pd
from io import BytesIO
import json

load_dotenv()

API_KEY = os.getenv("GONGGONG_API_KEY")


def get_alarm(page_no=1, rows_num=100):
    """API 호출해서 reponse 반환"""
    endpoint_url = (
        "https://apis.data.go.kr/1262000/TravelAlarmService0404/getTravelAlarm0404List"
    )
    params = {"serviceKey": API_KEY, "numOfRows": rows_num, "pageNo": page_no}

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


os.makedirs("data/raw", exist_ok=True)

country_data = []
for p in range(1, 2):
    r = get_alarm(page_no=p, rows_num=1000)
    df = pd.DataFrame(r.json()['response']['body']['items']['item'])
    for _, row in df.iterrows():
        country_data.append(
            {
                "국가명": row["country_nm"],
                "영문국가명": row["country_eng_nm"],
                "ISO 코드": row["country_iso_alp2"],
                "대륙 코드": row["continent_cd"],
                "영문 대륙명": row["continent_eng_nm"],
                "한글 대륙명": row["continent_nm"],
                "경보단계": row["alarm_lvl"],
                "경보내용": row["remark"],
                "작성일": row["written_dt"],
            }
        )

with open("data/raw/alarm.json", "w", encoding="utf-8") as f:
    json.dump(country_data, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {len(country_data)}건")  # 건수 확인 추가

# 최신 확인
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

alarm = pd.DataFrame(country_data)
print(alarm[alarm['국가명'].isin(['우크라이나','러시아','일본','태국'])])