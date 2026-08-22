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

# 저장된 데이터 샘플 확인
sample = vector_db._collection.peek(limit=3)

for metadata in sample["metadatas"]:
    print(metadata)

print("Chroma IDs:", sample["ids"])
print("Metadata:", sample["metadatas"])



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


# query = "택시 이용할 때 주의할 점은?"

# results = vector_db.similarity_search(
#     query,
#     k=5,
#     filter={"국가명": "가나"},
# )

# for i, doc in enumerate(results, start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("metadata:", doc.metadata)
#     print("내용:")
#     print(doc.page_content[:700])





# 테스트 - 가나
# if __name__ == "__main__":
#     query = "가나에서 택시 이용할 때 주의할 점은?"

#     print("추출된 국가:", extract_country(query))

#     docs = search_documents(query, k=3)

#     for i, doc in enumerate(docs, start=1):
#         print(f"\n=== 검색 결과 {i} ===")
#         print("국가:", doc.metadata.get("국가명"))
#         print("출처:", doc.metadata.get("source"))
#         print(doc.page_content[:500])

# 테스트 - 일본
# if __name__ == "__main__":
#     query = "일본에서 지진이 나면 어떻게 해야 해?"

#     print("추출된 국가:", extract_country(query))

#     docs = search_documents(query, k=3)

#     for i, doc in enumerate(docs, start=1):
#         print(f"\n=== 검색 결과 {i} ===")
#         print("국가:", doc.metadata.get("국가명"))
#         print("출처:", doc.metadata.get("source"))
#         print(doc.page_content[:500])

# 테스트 - 프랑스
# if __name__ == "__main__":
#     query = "프랑스에서 소매치기를 조심해야 하나?"

#     print("추출된 국가:", extract_country(query))

#     docs = search_documents(query, k=3)

#     for i, doc in enumerate(docs, start=1):
#         print(f"\n=== 검색 결과 {i} ===")
#         print("국가:", doc.metadata.get("국가명"))
#         print("출처:", doc.metadata.get("source"))
#         print(doc.page_content[:500])

# 테스트 - 국가없음
# if __name__ == "__main__":
#     query = "해외에서 택시 이용할 때 주의할 점은?"

#     print("추출된 국가:", extract_country(query))

#     docs = search_documents(query, k=3)

#     for i, doc in enumerate(docs, start=1):
#         print(f"\n=== 검색 결과 {i} ===")
#         print("국가:", doc.metadata.get("국가명"))
#         print("출처:", doc.metadata.get("source"))
#         print(doc.page_content[:500])

# 테스트 k5 - 일본
# if __name__ == "__main__":
#     query = "일본에서 지진이 나면 어떻게 해야 해?"

#     print("추출된 국가:", extract_country(query))

#     docs = search_documents(query, k=5)

#     for i, doc in enumerate(docs, start=1):
#         print(f"\n=== 검색 결과 {i} ===")
#         print("국가:", doc.metadata.get("국가명"))
#         print("출처:", doc.metadata.get("source"))
#         print(doc.page_content[:500])

# score 테스트 1

# query = "일본에서 지진이 나면 어떻게 해야 해?"

# results = search_documents(query)

# for i, (doc, score) in enumerate(results, start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("국가:", doc.metadata.get("국가명"))
#     print("출처:", doc.metadata.get("source"))
#     print("점수:", round(score, 3))
#     print(doc.page_content[:500])


# score 테스트 2
# query = "일본에서 맛있는 라멘집 추천해줘"

# results = search_documents(query)

# for i, (doc, score) in enumerate(results, start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("국가:", doc.metadata.get("국가명"))
#     print("출처:", doc.metadata.get("source"))
#     print("점수:", round(score, 3))
#     print(doc.page_content[:500])


# score 테스트 3
# query = "파이썬에서 딕셔너리는 어떻게 사용해?"

# results = search_documents(query)

# for i, (doc, score) in enumerate(results, start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("국가:", doc.metadata.get("국가명"))
#     print("출처:", doc.metadata.get("source"))
#     print("점수:", round(score, 3))
#     print(doc.page_content[:500])


# threshold 정하는 테스트

# test_queries = [
#     # 정상적인 여행 안전 질문
#     "가나에서 택시 이용할 때 주의할 점은?",
#     "프랑스에서 소매치기를 당하면 어떻게 해야 해?",
#     "태국에서 야간에 돌아다녀도 괜찮아?",
#     "미국 여행 중 강도를 만나면 어떻게 해야 해?",
#     "필리핀에서 태풍이 오면 어떻게 해야 해?",
#     "일본에서 지진이 나면 어떻게 해야 해?",

#     # 주제와 관련 없는 질문
#     "일본에서 맛있는 라멘집 추천해줘",
#     "파이썬에서 딕셔너리는 어떻게 사용해?",
#     "오늘 저녁 메뉴 추천해줘",
# ]


# for query in test_queries:
#     country = extract_country(query)
#     results = search_documents(query, k=5)

#     print("\n" + "=" * 70)
#     print("질문:", query)
#     print("추출 국가:", country)

#     if results:
#         top_doc, top_score = results[0]

#         print("최고 score:", round(top_score, 3))
#         print("1위 국가:", top_doc.metadata.get("국가명"))
#         print("1위 출처:", top_doc.metadata.get("source"))
#         print("1위 내용:", top_doc.page_content[:100].replace("\n", " "))

#     else:
#         print("검색 결과 없음")

# 국가명 수정 테스트
# test_queries = [
#     "미국 여행 중 강도를 만나면 어떻게 해야 해?",
#     "터키 여행할 때 주의할 점은?",
#     "네팔에서 여행할 때 위험한 지역이 있어?",
#     "콩고민주공화국 여행은 안전해?",
# ]

# for query in test_queries:
#     print(query, "→", extract_country(query))

# 국가명 수정 후 테스트
# test_queries = [
#     # 정상 여행 안전 질문
#     "가나에서 택시 이용할 때 주의할 점은?",
#     "프랑스에서 소매치기를 당하면 어떻게 해야 해?",
#     "태국에서 야간에 돌아다녀도 괜찮아?",
#     "미국 여행 중 강도를 만나면 어떻게 해야 해?",
#     "필리핀에서 태풍이 오면 어떻게 해야 해?",
#     "일본에서 지진이 나면 어떻게 해야 해?",
#     "터키 여행할 때 주의할 점은?",
#     "네팔에서 여행할 때 위험한 지역이 있어?",

#     # 주제 밖 질문
#     "일본에서 맛있는 라멘집 추천해줘",
#     "파이썬에서 딕셔너리는 어떻게 사용해?",
#     "오늘 저녁 메뉴 추천해줘",
# ]

# for query in test_queries:
#     country = extract_country(query)
#     results = search_documents(query)

#     top_score = results[0][1] if results else None

#     print(
#         f"{query} | "
#         f"국가: {country} | "
#         f"최고 score: {round(top_score, 3) if top_score is not None else None}"
#     )

# threshold 적용 후 확인할 테스트
# test_queries = [
#     "일본에서 지진이 나면 어떻게 해야 해?",
#     "오늘 저녁 메뉴 추천해줘",
# ]

# for query in test_queries:
#     results = search_documents(query)

#     print("\n질문:", query)
#     print("남은 결과 수:", len(results))

#     if results:
#         print("최고 score:", round(results[0][1], 3))

# 최종 테스트
# query = "미국 여행 중 강도를 만나면 어떻게 해야 해?"

# country = extract_country(query)
# search_query = remove_country_from_query(query, country)
# results = search_documents(query)

# print("원본 질문:", query)
# print("추출 국가:", country)
# print("검색용 질문:", search_query)
# print("검색 결과 수:", len(results))

# for i, (doc, score) in enumerate(results[:3], start=1):
#     print(f"\n=== 검색 결과 {i} ===")
#     print("국가:", doc.metadata.get("국가명"))
#     print("점수:", round(score, 3))
#     print(doc.page_content[:300])


# 최종 검색 함수 테스트

# from retriever import search_documents

# print(search_documents("일본에서 지진이 나면 어떻게 해야 해?"))
# print(search_documents("오늘 저녁 메뉴 추천해줘"))