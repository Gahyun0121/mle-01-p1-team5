from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 임베딩 모델
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)


# 기존 Vector DB 불러오기
vector_db = Chroma(
    persist_directory="data/vector_db",
    embedding_function=embeddings,
    collection_name="travel_safety",
)


# 저장된 데이터 개수 확인
print("Vector DB 저장 개수:", vector_db._collection.count())

# query = "가나에서 택시 이용할 때 주의할 점은?"

# results = vector_db.similarity_search(
#     query,
#     k=10,
# )

# print("\n질문:", query)

# for i, doc in enumerate(results, start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("metadata:", doc.metadata)
#     print("내용:")
#     print(doc.page_content[:500])


query = "택시 이용할 때 주의할 점은?"

results = vector_db.similarity_search(
    query,
    k=5,
    filter={"국가명": "가나"},
)

for i, doc in enumerate(results, start=1):
    print(f"\n=== 검색 결과 {i} ===")
    print("metadata:", doc.metadata)
    print("내용:")
    print(doc.page_content[:700])