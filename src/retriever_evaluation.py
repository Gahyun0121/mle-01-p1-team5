# src/ 안에서 실행해도 프로젝트 루트를 찾도록 경로 등록
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

# 콘솔 인코딩을 거치지 않고 UTF-8 파일로 직접 저장 (Windows cp949 깨짐 방지)
_out = open("eval_result_retriever.txt", "w", encoding="utf-8")


def print(*args, **kwargs):  # noqa: A001
    kwargs["file"] = _out
    __builtins__.print(*args, **kwargs)


import pandas as pd

# 실제 챗봇과 동일한 검색 함수 사용 (국가 별칭 처리 + 유사도 임계값 0.25 포함)
from src.retriever import search_documents
# 지표 계산 로직은 src/metrics.py 로 분리
from src.metrics import hit, precision, recall, mrr


# ============================================================
# 1. 평가셋 불러오기
# ============================================================

# 평가셋을 코드에서 분리 — 문항 수정 시 CSV만 고치면 됨
# keep_default_na=False : 빈 gold_chunks가 NaN으로 읽히는 것 방지
eval_df = pd.read_csv("data/eval_set.csv", keep_default_na=False)

questions = [
    {
        "id": row["query_id"],
        "type": row["type"],
        "country": row["country"],
        "question": row["question"],
    }
    for _, row in eval_df.iterrows()
]

# gold가 있는 A·B 유형만 검색 지표 대상
# C 유형(답변 불가)은 검색이 아니라 생성 단계에서 평가
gold_set = {
    row["query_id"]: row["gold_chunks"].split(";")
    for _, row in eval_df.iterrows()
    if row["gold_chunks"]
}

print("평가셋 총 문항:", len(questions))
print("검색 지표 대상(A·B):", len(gold_set))
print("생성 단계 대상(C):", len(questions) - len(gold_set))


# ============================================================
# 2. Retriever 실행
# ============================================================

retrieval_results = {}

for item in questions:
    query_id = item["id"]
    country = item["country"]
    query = item["question"]

    print("\n" + "=" * 100)
    print(f"{query_id} [{item['type']}]: {query}")
    print(f"국가 필터: {country}")
    print("=" * 100)

    # 챗봇 페이지와 같은 형태로 전달 (내부에서 국가 추출 후 쿼리에서 제거)
    docs = search_documents(f"{country} {query}")

    retrieval_results[query_id] = [d["chunk_id"] for d in docs]

    print("검색 결과 개수:", len(docs))

    for rank, d in enumerate(docs, start=1):
        print(f"\n=== 검색 결과 {rank} ===")
        print("chunk_id:", d["chunk_id"], "/ score:", d["score"])
        print("내용:")
        print(d["content"][:500])


# ============================================================
# 3. 평가 함수
# ============================================================

def evaluate_retriever(gold_set, retrieval_results):
    evaluation_results = []

    for query_id, gold_chunks in gold_set.items():
        retrieved_chunks = retrieval_results[query_id]

        correct_chunks = [
            chunk
            for chunk in retrieved_chunks
            if chunk in gold_chunks
        ]

        # 지표 계산은 src/metrics.py 의 함수 사용
        hit_at_5 = hit(retrieved_chunks, gold_chunks, 5)
        precision_at_5 = precision(retrieved_chunks, gold_chunks, 5)
        recall_at_5 = recall(retrieved_chunks, gold_chunks, 5)
        mrr_score = mrr(retrieved_chunks, gold_chunks, 5)

        # 첫 정답 순위 (MRR의 역수)
        first_gold_rank = int(1 / mrr_score) if mrr_score else None
        
        evaluation_results.append({
            "query_id": query_id,
            "gold_chunks": gold_chunks,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_count": len(retrieved_chunks),
            "correct_chunks": correct_chunks,
            "first_gold_rank": first_gold_rank,
            "Hit@5": hit_at_5,
            "Precision@5": precision_at_5,
            "Recall@5": recall_at_5,
            "MRR": mrr_score,
        })

    return evaluation_results


# ============================================================
# 4. 평가 실행
# ============================================================

evaluation_results = evaluate_retriever(gold_set, retrieval_results)

df_eval = pd.DataFrame(evaluation_results)


# ============================================================
# 5. 질문별 전체 평가 결과
# ============================================================

print("\n")
print("=" * 100)
print("질문별 Retriever 평가 결과")
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
# 6. 핵심 점수만 보기
# ============================================================

df_score = df_eval[
    [
        "query_id",
        "retrieved_count",
        "Hit@5",
        "Precision@5",
        "Recall@5",
        "MRR",
    ]
]

print("\n")
print("=" * 100)
print("핵심 평가 지표")
print("=" * 100)

print(df_score.to_string(index=False))


# ============================================================
# 7. 전체 평균 성능
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
print("Retriever 전체 평균 성능 (A·B 유형)")
print("=" * 100)

print(average_scores)


# ============================================================
# 8. 유형별 평균 성능
# ============================================================

# A(단일 근거)와 B(다중 근거)는 난이도가 달라 나눠서 확인
type_map = {row["query_id"]: row["type"] for _, row in eval_df.iterrows()}
df_eval["type"] = df_eval["query_id"].map(type_map)

print("\n")
print("=" * 100)
print("유형별 평균 성능")
print("=" * 100)

print(
    df_eval.groupby("type")[
        ["Hit@5", "Precision@5", "Recall@5", "MRR"]
    ].mean().to_string()
)


# ============================================================
# 9. 임계값에 걸려 5건 미만으로 줄어든 문항
# ============================================================

thin_queries = df_eval[df_eval["retrieved_count"] < 5]

print("\n")
print("=" * 100)
print("검색 결과가 5건 미만인 문항 (유사도 0.25 미만 제외됨)")
print("=" * 100)

if len(thin_queries) == 0:
    print("모든 문항이 5건을 채웠습니다.")
else:
    print(
        thin_queries[
            [
                "query_id",
                "retrieved_count",
                "Hit@5",
                "Recall@5",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 10. 검색 실패 문항
# ============================================================

failed_queries = df_eval[df_eval["Hit@5"] == 0]

print("\n")
print("=" * 100)
print("검색 실패 문항")
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
# 11. 부분 성공 문항
# Recall@5가 0보다 크고 1보다 작은 경우
# ============================================================

partial_queries = df_eval[
    (df_eval["Recall@5"] > 0)
    & (df_eval["Recall@5"] < 1)
]

print("\n")
print("=" * 100)
print("부분 검색 성공 문항")
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
# 12. C 유형 검색 결과 확인
# 검색 지표 대상은 아니지만, 무엇을 물고 오는지 확인용
# ============================================================

c_ids = [
    row["query_id"]
    for _, row in eval_df.iterrows()
    if not row["gold_chunks"]
]

print("\n")
print("=" * 100)
print("C 유형(답변 불가) 검색 결과 — 생성 단계 평가용 참고")
print("=" * 100)

for cid in c_ids:
    chunks = retrieval_results[cid]
    print(f"{cid}: {len(chunks)}건 {chunks}")


_out.close()