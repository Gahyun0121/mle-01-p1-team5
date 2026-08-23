import pandas as pd

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 1. 국가명 목록 불러오기
incident = pd.read_csv("data/incident_info_clean.csv")
notice = pd.read_csv("data/safety_notice_processed.csv")


country_names = set(
    incident["국가명"].dropna().tolist()
    + notice["국가명"].dropna().tolist()
)

country_names.discard("ALL")

# 사용자가 입력한 국가명과 데이터 속 국가명 차이 없애기
country_aliases = {
    "미국": "미합중국",
    "UAE": "아랍에미리트",
    "아랍에미리트연합": "아랍에미리트",
    "터키": "튀르키예공화국",
    "튀르키예": "튀르키예공화국",
    "네팔": "네팔연방",
    "키르기스스탄": "키르기즈공화국",
    "키르기즈스탄": "키르기즈공화국",
    "베네수엘라": "베네수엘라볼리바르",
    "남아공": "남아프리카공화국",
    "바티칸": "교황청",
    "바티칸시국": "교황청",
    "키프로스": "사이프러스",
    "오스트레일리아": "호주",
    "UK": "영국",
}


# 2. 임베딩 모델 불러오기
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)


# 3. 기존 Vector DB 불러오기
vector_db = Chroma(
    persist_directory="data/vector_db",
    embedding_function=embeddings,
    collection_name="travel_safety",
)


# 4. 질문에서 국가명 찾기
def extract_country(query):

    # 1. DB 정식 국가명 확인
    # 이름이 겹치는 경우 긴 국가명부터 검사
    for country in sorted(country_names, key=len, reverse=True):
        if country in query:
            return country

    # 2. 국가 별칭 확인
    for alias, country in country_aliases.items():
        if alias.lower() in query.lower():
            return country

    return None


# 별칭 입력시 질문에서 국가명 삭제하기 

def remove_country_from_query(query, country):

    # DB의 정식 국가명을 입력한 경우 먼저 제거
    if country in query:
        return query.replace(country, "").strip()

    # 별칭으로 입력한 경우
    for alias, standard_country in country_aliases.items():
        if standard_country == country and alias.lower() in query.lower():
            return query.replace(alias, "").strip()

    return query.strip()






# 5. 관련 문서 검색

def search_documents(query, k=5, threshold=0.25):
    country = extract_country(query)

    if country:
        search_query = remove_country_from_query(query, country)

        results = vector_db.similarity_search_with_relevance_scores(
            search_query,
            k=k,
            filter={"국가명": country},
            )
    else:
        results = vector_db.similarity_search_with_relevance_scores(
            query,
            k=k,
        )

    formatted_results = []

    for doc, score in results:

        # threshold 미만 제외
        if score < threshold:
            continue

        # safety_notice 제목 추출
        title = ""

        if doc.page_content.startswith("제목:"):
            first_line = doc.page_content.split("\n", 1)[0]
            title = first_line.replace("제목:", "").strip()

        formatted_results.append({
            "content": doc.page_content,
            "title": title,
            "country": doc.metadata.get("국가명", ""),
            "date": doc.metadata.get("작성일", ""),
            "iso": doc.metadata.get("ISO코드", ""),
            "source": doc.metadata.get("source", ""),
            "chunk_id": doc.metadata.get("chunk_id", ""),
            "score": round(score, 3),
        })

    return formatted_results