import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.retriever import search_documents
from src.generator import generate_answer

# 평가셋을 코드에서 분리 — 검색 평가와 같은 파일을 공유
# keep_default_na=False : 빈 gold_chunks가 NaN으로 읽히는 것 방지
eval_df = pd.read_csv("data/eval_set.csv", keep_default_na=False)

with open("eval_result.md", "w", encoding="utf-8") as f:
    for _, row in eval_df.iterrows():
        qid = row["query_id"]
        qtype = row["type"]
        country = row["country"]
        question = row["question"]

        # 챗봇 페이지와 동일한 호출 형태
        docs = search_documents(f"{country} {question}")
        answer = generate_answer(question, docs, country)

        f.write(f"## {qid} [{qtype}] {country} — {question}\n\n")
        f.write(f"검색 {len(docs)}건: {[d['chunk_id'] for d in docs]}\n\n")

        # C 유형은 거절 여부가 판정 기준이라 사유를 같이 기록
        if qtype == "C":
            f.write(f"> 답변 불가 사유: {row['note']}\n\n")

        f.write(f"{answer}\n\n---\n\n")

        print(f"{qid} 완료")