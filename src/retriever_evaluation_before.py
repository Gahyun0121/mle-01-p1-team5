from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd


# ============================================================
# 1. 임베딩 모델
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)


# ============================================================
# 2. Before / After Vector DB 불러오기
# ============================================================

before_db = Chroma(
    persist_directory="data/vector_db_before",
    embedding_function=embeddings,
    collection_name="travel_safety",
)

after_db = Chroma(
    persist_directory="data/vector_db_after",
    embedding_function=embeddings,
    collection_name="travel_safety",
)

print("Before Vector DB 저장 개수:", before_db._collection.count())
print("After Vector DB 저장 개수:", after_db._collection.count())


# ============================================================
# 3. After DB를 이용해서 page_content -> chunk_id 매핑 생성
# ============================================================

def normalize_text(text):
    return " ".join(text.split())


after_data = after_db.get(
    include=["documents", "metadatas"]
)

chunk_text_to_id = {}

for text, metadata in zip(
    after_data["documents"],
    after_data["metadatas"],
):
    chunk_id = metadata.get("chunk_id")

    if chunk_id:
        normalized_text = normalize_text(text)
        chunk_text_to_id[normalized_text] = chunk_id


print("chunk_id 매핑 개수:", len(chunk_text_to_id))


def get_chunk_id_from_content(page_content):
    normalized_text = normalize_text(page_content)
    return chunk_text_to_id.get(normalized_text)


# ============================================================
# 4. 평가 질문
# ============================================================

questions = [
    {
        "id": "Q01",
        "country": "미합중국",
        "question": "여자 혼자 미국 여행해도 괜찮을까? 밤에는 많이 위험해?",
    },
    {
        "id": "Q02",
        "country": "미합중국",
        "question": "미국 여행 중 렌터카에 짐이나 귀중품을 두고 내려도 괜찮아?",
    },
    {
        "id": "Q03",
        "country": "미합중국",
        "question": "미국 여행할 때 총기 범죄도 조심해야 해?",
    },
    {
        "id": "Q04",
        "country": "일본",
        "question": "일본 여행 중 지진이 자주 발생한다는데 많이 걱정해야 해?",
    },
    {
        "id": "Q05",
        "country": "일본",
        "question": "일본 여행 가면 한국인 관광객을 대상으로 바가지를 씌우는 경우가 많아?",
    },
    {
        "id": "Q06",
        "country": "일본",
        "question": "홋카이도에서 렌터카로 여행하려는데 한국에서 운전할 때와 비교해서 특히 조심해야 할 점이 뭐야?",
    },
    {
        "id": "Q07",
        "country": "중국",
        "question": "중국 여행 가는데 전반적인 치안은 어떤 편이야?",
    },
    {
        "id": "Q08",
        "country": "중국",
        "question": "중국 관광지에서 가방이나 카메라를 도난당할 위험이 큰 편이야?",
    },
    {
        "id": "Q09",
        "country": "중국",
        "question": "티베트 라싸 같은 지역은 그냥 자유롭게 여행할 수 있는 게 아니야?",
    },
    {
        "id": "Q10",
        "country": "베트남",
        "question": "베트남에서 휴대폰 들고 걸어 다니면 날치기 위험이 커?",
    },
    {
        "id": "Q11",
        "country": "베트남",
        "question": "베트남 공항에서 Grab 직원이라고 접근하는 사람이 있으면 믿어도 돼?",
    },
    {
        "id": "Q12",
        "country": "베트남",
        "question": "베트남에서는 전자담배를 가지고만 있어도 문제가 될 수 있어?",
    },
    {
        "id": "Q13",
        "country": "태국",
        "question": "태국 여행 가는데 치안 괜찮아?",
    },
    {
        "id": "Q14",
        "country": "태국",
        "question": "태국 야시장이나 클럽처럼 사람이 많은 곳에서는 어떤 범죄를 조심해야 해?",
    },
    {
        "id": "Q15",
        "country": "필리핀",
        "question": "필리핀 요즘 치안 괜찮아? 강도나 소매치기 위험이 커?",
    },
    {
        "id": "Q16",
        "country": "필리핀",
        "question": "필리핀에서 총기나 흉기를 든 강도를 만나면 어떻게 해야 해?",
    },
    {
        "id": "Q17",
        "country": "홍콩",
        "question": "홍콩에 태풍 오면 여행 일정은 어떻게 해야 해?",
    },
    {
        "id": "Q18",
        "country": "홍콩",
        "question": "홍콩에서 분실 신고한 여권을 다시 찾았는데 그대로 써도 돼?",
    },
    {
        "id": "Q19",
        "country": "그리스",
        "question": "그리스 여행 가는데 산불이나 폭염 때문에 위험하지 않을까?",
    },
    {
        "id": "Q20",
        "country": "그리스",
        "question": "아테네 근처에서 산불 대피령이 내려지면 관광객도 바로 이동해야 해?",
    },
    {
        "id": "Q21",
        "country": "남아프리카공화국",
        "question": "남아공 자유여행은 치안 때문에 많이 위험해?",
    },
    {
        "id": "Q22",
        "country": "나이지리아",
        "question": "나이지리아는 여행을 고민할 정도로 납치나 강도 위험이 큰 편이야?",
    },
    {
        "id": "Q23",
        "country": "케냐",
        "question": "케냐 여행할 때 치안 위험은 어느 정도로 생각해야 해?",
    },
    {
        "id": "Q24",
        "country": None,
        "question": "아프리카 국가에 여행경보 3단계가 내려져 있으면 여행을 취소해야 하는 수준이야?",
    },
    {
        "id": "Q25",
        "country": "몰디브",
        "question": "몰디브 리조트면 치안 걱정은 거의 안 해도 돼?",
    },
    {
        "id": "Q26",
        "country": "몰디브",
        "question": "여자 혼자 몰디브 리조트에 머물 때 성범죄나 절도도 조심해야 해?",
    },
    {
        "id": "Q27",
        "country": "몽골",
        "question": "여자 혼자 몽골 여행해도 괜찮을까?",
    },
    {
        "id": "Q28",
        "country": "아랍에미리트",
        "question": "두바이 클럽에서 모르는 사람이 주는 음료를 받아 마셔도 괜찮아?",
    },
    {
        "id": "Q29",
        "country": None,
        "question": "여자 혼자 여행 중 처음 만난 사람이 주는 음료를 마셔도 괜찮을까?",
    },
    {
        "id": "Q30",
        "country": None,
        "question": "여자 혼자 여행할 때 성범죄나 강도 피해를 줄이려면 어떤 상황을 특히 피해야 해?",
    },
]


# ============================================================
# 5. Gold Set
# ============================================================

gold_set = {
    "Q01": ["i_00132"],
    "Q02": ["i_00131", "i_00128"],
    "Q03": ["sn_02086", "i_00128"],
    "Q04": ["i_00323"],
    "Q05": ["i_00320", "i_00323"],
    "Q06": ["sn_05010", "i_00321"],
    "Q07": ["i_00335", "i_00336", "sn_05140"],
    "Q08": ["i_00332", "i_00336"],
    "Q09": ["i_00336"],
    "Q10": ["sn_02376", "i_00148"],
    "Q11": ["sn_02381"],
    "Q12": ["sn_02376", "sn_02395", "sn_02366"],
    "Q13": ["i_00419", "sn_06224", "i_00417"],
    "Q14": ["i_00422", "i_00424", "i_00426"],
    "Q15": ["sn_07001", "sn_07019", "sn_06983"],
    "Q16": ["sn_07034"],
    "Q17": ["sn_07294", "sn_07267"],
    "Q18": ["sn_07307"],
    "Q19": ["sn_00229", "sn_00224", "sn_00228"],
    "Q20": ["sn_00217"],
    "Q21": ["sn_00559", "i_00024"],
    "Q22": ["sn_00406", "i_00021", "sn_00405"],
    "Q23": ["i_00370", "sn_05710"],
    "Q24": ["sn_06851"],
    "Q25": ["i_00119"],
    "Q26": ["i_00119", "i_00120"],
    "Q27": ["i_00122"],
    "Q28": ["i_00226"],
    "Q29": ["sn_05984", "i_00441"],
    "Q30": ["i_00314", "i_00106", "i_00424", "i_00008"],
}


# ============================================================
# 6. Before Retriever 실행
# ============================================================

retrieval_results = {}
mapping_failure_count = 0

for item in questions:
    query_id = item["id"]
    country = item["country"]
    query = item["question"]

    print("\n" + "=" * 100)
    print(f"{query_id}: {query}")
    print(f"국가 필터: {country}")
    print("=" * 100)

    # 중요:
    # 평가 대상은 Before DB
    if country:
        results = before_db.similarity_search(
            query,
            k=5,
            filter={"국가명": country},
        )
    else:
        results = before_db.similarity_search(
            query,
            k=5,
        )

    mapped_chunks = []

    for doc in results:
        chunk_id = get_chunk_id_from_content(
            doc.page_content
        )

        if chunk_id is None:
            mapping_failure_count += 1

            print("\n⚠ chunk_id 매핑 실패")
            print("Before doc.id:", doc.id)
            print("metadata:", doc.metadata)
            print("내용:")
            print(doc.page_content[:200])

        mapped_chunks.append(chunk_id)

    retrieval_results[query_id] = mapped_chunks

    print("검색 결과 개수:", len(results))

    for rank, (doc, chunk_id) in enumerate(
        zip(results, mapped_chunks),
        start=1,
    ):
        print(f"\n=== 검색 결과 {rank} ===")
        print("Before doc.id:", doc.id)
        print("복원 chunk_id:", chunk_id)
        print("내용:")
        print(doc.page_content[:500])


# ============================================================
# 7. chunk_id 매핑 상태 확인
# ============================================================

print("\n")
print("=" * 100)
print("chunk_id 매핑 상태")
print("=" * 100)

print("매핑 실패 개수:", mapping_failure_count)

if mapping_failure_count > 0:
    print(
        "\n⚠ 매핑 실패가 있습니다."
        "\n평가 점수를 확정하기 전에 실패한 청크를 확인하세요."
    )
else:
    print("모든 Before 검색 결과의 chunk_id 매핑 성공")


# ============================================================
# 8. 평가 함수
# ============================================================

def evaluate_retriever(
    gold_set,
    retrieval_results,
):
    evaluation_results = []

    for query_id, gold_chunks in gold_set.items():
        retrieved_chunks = retrieval_results[query_id]

        correct_chunks = [
            chunk
            for chunk in retrieved_chunks
            if chunk in gold_chunks
        ]

        # Hit@5
        hit_at_5 = 1 if len(correct_chunks) > 0 else 0

        # Precision@5
        if len(retrieved_chunks) > 0:
            precision_at_5 = (
                len(correct_chunks)
                / len(retrieved_chunks)
            )
        else:
            precision_at_5 = 0

        # Recall@5
        if len(gold_chunks) > 0:
            recall_at_5 = (
                len(correct_chunks)
                / len(gold_chunks)
            )
        else:
            recall_at_5 = 0

        # MRR
        mrr = 0
        first_gold_rank = None

        for rank, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            if chunk in gold_chunks:
                first_gold_rank = rank
                mrr = 1 / rank
                break

        evaluation_results.append(
            {
                "query_id": query_id,
                "gold_chunks": gold_chunks,
                "retrieved_chunks": retrieved_chunks,
                "correct_chunks": correct_chunks,
                "first_gold_rank": first_gold_rank,
                "Hit@5": hit_at_5,
                "Precision@5": precision_at_5,
                "Recall@5": recall_at_5,
                "MRR": mrr,
            }
        )

    return evaluation_results


# ============================================================
# 9. 평가 실행
# ============================================================

evaluation_results = evaluate_retriever(
    gold_set,
    retrieval_results,
)

df_eval = pd.DataFrame(evaluation_results)


# ============================================================
# 10. 질문별 전체 평가 결과
# ============================================================

print("\n")
print("=" * 100)
print("Before 질문별 Retriever 평가 결과")
print("=" * 100)

print(
    df_eval[
        [
            "query_id",
            "gold_chunks",
            "retrieved_chunks",
            "correct_chunks",
            "first_gold_rank",
            "Hit@5",
            "Precision@5",
            "Recall@5",
            "MRR",
        ]
    ].to_string(index=False)
)


# ============================================================
# 11. 핵심 점수
# ============================================================

df_score = df_eval[
    [
        "query_id",
        "Hit@5",
        "Precision@5",
        "Recall@5",
        "MRR",
    ]
]

print("\n")
print("=" * 100)
print("Before 핵심 평가 지표")
print("=" * 100)

print(df_score.to_string(index=False))


# ============================================================
# 12. 전체 평균 성능
# ============================================================

average_scores = df_score[
    [
        "Hit@5",
        "Precision@5",
        "Recall@5",
        "MRR",
    ]
].mean()

print("\n")
print("=" * 100)
print("Before Retriever 전체 평균 성능")
print("=" * 100)

print(average_scores)


# ============================================================
# 13. 검색 실패 문항
# ============================================================

failed_queries = df_eval[
    df_eval["Hit@5"] == 0
]

print("\n")
print("=" * 100)
print("Before 검색 실패 문항")
print("=" * 100)

if len(failed_queries) == 0:
    print("검색 실패 문항이 없습니다.")
else:
    print(
        failed_queries[
            [
                "query_id",
                "gold_chunks",
                "retrieved_chunks",
                "Hit@5",
                "Recall@5",
                "MRR",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 14. 부분 성공 문항
# ============================================================

partial_queries = df_eval[
    (df_eval["Recall@5"] > 0)
    & (df_eval["Recall@5"] < 1)
]

print("\n")
print("=" * 100)
print("Before 부분 검색 성공 문항")
print("=" * 100)

if len(partial_queries) == 0:
    print("부분 검색 성공 문항이 없습니다.")
else:
    print(
        partial_queries[
            [
                "query_id",
                "gold_chunks",
                "retrieved_chunks",
                "correct_chunks",
                "Recall@5",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 15. Before 평가 완료
# ============================================================

print("\n")
print("=" * 100)
print("Before Retriever 평가 완료")
print("=" * 100)