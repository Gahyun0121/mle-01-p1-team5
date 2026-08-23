from retriever import extract_country, search_documents, vector_db

# test_queries = [
#     "가나 택시 주의사항 알려줘",
#     "미국 총기 사고 알려줘",
#     "터키 시위 관련 내용 알려줘",
#     "네팔 자연재해 알려줘",
#     "해외여행 시 소매치기 주의사항 알려줘",
# ]

# test_queries = [
#     # 1. 별칭
#     "UAE 여행 안전정보 알려줘",
#     "남아공 치안 알려줘",
#     "바티칸 여행 주의사항 알려줘",

#     # 2. DB의 정식 국가명 직접 입력
#     "미합중국 총기 사고 알려줘",
#     "튀르키예공화국 시위 알려줘",

#     # 3. 국가 없이 일반 질문
#     "여행 중 여권을 분실하면 어떻게 해야 해?",
#     "해외여행 중 사기 주의사항 알려줘",

#     # 4. 관련 문서가 적을 것 같은 질문
#     "가나 지진 주의사항 알려줘",
# ]

# test_queries = [
#     "터키 시위 알려줘",
#     "튀르키예 시위 알려줘",
#     "튀르키예공화국 시위 알려줘",
# ]

test_queries = [
    # 1. 새로운 국가 + 구체적인 범죄
    "프랑스 소매치기 주의사항 알려줘",
    "필리핀 납치 관련 정보 알려줘",
    "태국 마약 관련 주의사항 알려줘",

    # 2. 새로운 국가 + 자연재해
    "일본 지진 관련 안전정보 알려줘",
    "인도네시아 화산 관련 주의사항 알려줘",

    # 3. 새로운 국가 + 시위/테러
    "영국 테러 관련 안전정보 알려줘",
    "프랑스 시위 관련 내용 알려줘",

    # 4. 국가 + 여행 중 실제 행동 질문
    "베트남에서 여권 잃어버리면 어떻게 해야 해?",
    "일본에서 지진이 나면 어떻게 해야 해?",

    # 5. 국가 없이 검색
    "해외여행 중 강도를 당하면 어떻게 해야 해?",
    "여행 중 자연재해가 발생하면 어떻게 해야 해?",

    # 6. 일부러 애매하거나 자료가 없을 법한 질문
    "캐나다 납치 주의사항 알려줘",
    "싱가포르 지진 주의사항 알려줘",

    # 7. 질문 내용은 같지만 표현이 다른 질문들
    "일본 지진 주의사항 알려줘",
    "일본에서 지진 나면 어떡해?",
    "일본 여행가는데 지진 괜찮아?",
]



for query in test_queries:
    print("=" * 80)
    print("질문:", query)

    country = extract_country(query)
    print("인식 국가:", country)

    results = search_documents(query)

    print("검색 결과 개수:", len(results))

    for i, result in enumerate(results, 1):
        print(f"\n[{i}]")
        print("국가:", result["country"])
        print("source:", result["source"])
        print("chunk_id:", result["chunk_id"])
        print("score:", result["score"])
        print("title:", result["title"])
        print("내용:", result["content"][:200])

# results = vector_db.similarity_search_with_relevance_scores(
#     "시위 관련 내용 알려줘",
#     k=5,
#     filter={"국가명": "튀르키예공화국"},
# )

# for doc, score in results:
#     print("=" * 50)
#     print("국가:", doc.metadata.get("국가명"))
#     print("source:", doc.metadata.get("source"))
#     print("score:", round(score, 3))
#     print("내용:", doc.page_content[:300])

# from retriever import extract_country, search_documents


# test_queries = [
#     # 정상 국가명
#     "가나 택시 주의사항 알려줘",
#     "네팔 자연재해 알려줘",

#     # 별칭
#     "미국 총기 사고 알려줘",
#     "터키 시위 관련 내용 알려줘",
#     "남아공 강도 사건 알려줘",
#     "바티칸 여행 안전 알려줘",

#     # 국가 없는 일반 질문
#     "해외여행 시 소매치기 주의사항 알려줘",
#     "여행 중 여권 분실하면 어떻게 해야 해?",
#     "해외여행 중 시위 발생 시 주의사항 알려줘",

#     # 조금 애매한 질문
#     "유럽에서 테러 관련 주의사항 알려줘",
#     "여행 중 택시 이용할 때 조심할 점 알려줘",

#     # 데이터에 없거나 인식 어려운 국가
#     "북한 여행 안전정보 알려줘",
# ]


# # for query in test_queries:
# #     print("=" * 80)
# #     print("질문:", query)

# #     country = extract_country(query)
# #     print("인식 국가:", country)

# #     results = search_documents(query)

# #     print("검색 결과 개수:", len(results))

# #     for i, result in enumerate(results, 1):
# #         print(f"\n[{i}]")
# #         print("국가:", result["country"])
# #         print("source:", result["source"])
# #         print("chunk_id:", result["chunk_id"])
# #         print("score:", result["score"])
# #         print("date:", result["date"])
# #         print("title:", result["title"])
# #         print("내용:", result["content"][:200])