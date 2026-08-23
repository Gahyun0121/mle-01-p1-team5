import pandas as pd
from tqdm import tqdm

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 1. 데이터 불러오기
incident = pd.read_csv("data/incident_info_clean.csv")
notice = pd.read_csv("data/safety_notice_processed.csv")


# 2. incident → Document 변환
incident_docs = []

for _, row in incident.iterrows():

    # 사건사고 내용이 없는 행은 제외
    if pd.isna(row["사건사고내용_clean"]):
        continue

    doc = Document(
        page_content=row["사건사고내용_clean"],
        metadata={
            "국가명": row["국가명"],
            "영문국가명": row["영문국가명"],
            "ISO코드": row["ISO코드"],
            "대륙명": row["대륙명"],
            "작성일": row["사건사고_작성일"],
            "source": "incident",
        },
    )

    incident_docs.append(doc)

print("Incident Document 개수:", len(incident_docs))


# 3. safety_notice → Document 변환

# metadata 결측치 처리
notice = notice.fillna({
    "국가명": "ALL",
    "영문국가명": "",
    "ISO코드": "",
    "대륙명": "",
    "공지제목": "",
    "공지유형": "",
})

notice_docs = []

for _, row in notice.iterrows():

    # 공지 내용이 없는 행은 제외
    if pd.isna(row["공지내용_텍스트"]):
        continue

    title = str(row["공지제목"])

    content = f"""
제목: {title}

내용:
{row["공지내용_텍스트"]}
""".strip()

    doc = Document(
        page_content=content,
        metadata={
            "국가명": row["국가명"],
            "영문국가명": row["영문국가명"],
            "ISO코드": row["ISO코드"],
            "대륙명": row["대륙명"],
            "작성일": row["안전공지_작성일"],
            "공지유형": row["공지유형"],
            "source": "safety_notice",
        },
    )

    notice_docs.append(doc)

print("Safety Notice Document 개수:", len(notice_docs))


# 4. 전체 Document 합치기
all_docs = incident_docs + notice_docs

print("전체 Document 개수:", len(all_docs))


# 5. 긴 Document를 작은 Chunk로 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)

chunks = text_splitter.split_documents(all_docs)

print("필터링 전 Chunk 개수:", len(chunks))


# 6. 의미 없는 Chunk 제거
INVALID_TEXTS = {
    "",
    "내용:",
    "제목:",
    "제목:\n내용:",
}

chunks = [
    chunk
    for chunk in chunks
    if chunk.page_content.strip() not in INVALID_TEXTS
]

print("필터링 후 Chunk 개수:", len(chunks))


# 7. source별 chunk_id 생성
source_counts = {
    "incident": 0,
    "safety_notice": 0,
}

for chunk in chunks:
    source = chunk.metadata["source"]

    if source == "incident":
        chunk.metadata["chunk_id"] = f"i_{source_counts[source]:05d}"

    elif source == "safety_notice":
        chunk.metadata["chunk_id"] = f"sn_{source_counts[source]:05d}"

    source_counts[source] += 1


# 8. chunk_id 중복 확인
chunk_ids = [
    chunk.metadata["chunk_id"]
    for chunk in chunks
]

assert len(chunk_ids) == len(set(chunk_ids)), \
    "중복된 chunk_id가 있습니다."

print("Incident Chunk 개수:", source_counts["incident"])
print("Safety Notice Chunk 개수:", source_counts["safety_notice"])
print("최종 Chunk 개수:", len(chunks))
print("chunk_id 중복 없음")


# 9. 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)


# 10. Vector DB 생성
vector_db = Chroma(
    collection_name="travel_safety",
    embedding_function=embeddings,
    persist_directory="data/vector_db",
)


# 11. Batch 단위로 임베딩 및 저장
batch_size = 100

for i in tqdm(
    range(0, len(chunks), batch_size),
    desc="Embedding & Saving",
):
    batch = chunks[i:i + batch_size]

    vector_db.add_documents(
        documents=batch,
        ids=[chunk.metadata["chunk_id"] for chunk in batch],
    )


print("\nVector DB 저장 완료")
print("저장 위치: data/vector_db")
print("저장된 Chunk 개수:", len(chunks))