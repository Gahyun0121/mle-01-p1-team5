import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

API_KEY = os.getenv("SARAMIN2_API_KEY")


def get_safety_notice(page_no=1, rows_num=1000):
    """외교부 안전공지 API 호출"""

    endpoint_url = (
        "https://apis.data.go.kr/1262000/"
        "CountrySafetyService6/getCountrySafetyList6"
    )

    params = {
        "serviceKey": API_KEY,
        "numOfRows": rows_num,
        "pageNo": page_no,
        "returnType": "JSON",
    }

    try:
        response = requests.get(
            endpoint_url,
            params=params,
            timeout=30
        )

    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {e}")
        return None

    if response.status_code == 200:
        return response

    print("에러:", response.status_code)
    print(response.text[:500])
    return None


# 저장 폴더 생성
os.makedirs("./safety_notice_data", exist_ok=True)

# 전체 데이터를 담을 리스트
safety_notice_data = []


# 1페이지 ~ 5페이지 수집
for page in range(1, 6):

    r = get_safety_notice(
        page_no=page,
        rows_num=1000
    )

    if r is None:
        print(f"{page}페이지 수집 실패")
        continue

    data = r.json()

    body = data["response"]["body"]
    items = body["items"]["item"]

    # 현재 페이지의 데이터를 한글 컬럼명으로 변환
    for item in items:
        safety_notice_data.append(
            {
                "국가명": item.get("country_nm"),
                "영문국가명": item.get("country_eng_nm"),                                
                "ISO코드": item.get("country_iso_alp2"),
                "대륙코드": item.get("continent_cd"),
                "대륙명": item.get("continent_nm"),
                "대륙영문명": item.get("continent_eng_nm"),
                "안전공지레벨": item.get("sfty_notice_lv"),
                "작성일": item.get("wrt_dt"),
                "공지제목": item.get("title"),
                "공지내용": item.get("txt_origin_cn"),
            }
        )

    # 이 print는 반드시 for item 밖에 있어야 함
    print(
        f"{page}페이지 수집 완료: "
        f"{len(items)}건 / "
        f"누적 {len(safety_notice_data)}건"
    )


# 전부 수집한 뒤 한 번만 저장
with open(
    "./safety_notice_data/safety_notice_info.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        safety_notice_data,
        f,
        ensure_ascii=False,
        indent=2
    )


print("------------------------------")
print(f"총 {len(safety_notice_data)}건 저장 완료")