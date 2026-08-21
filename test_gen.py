from src.mock_retriever import retrieve
from src.generator import generate_answer

q = "가나 치안 어때?"
docs = retrieve(q, "GH", k=3)
print(generate_answer(q, docs))

print("\n" + "=" * 40 + "\n")

# 빈 문서일 때 '자료가 없습니다'가 나오는지 확인
print(generate_answer("가나 물가 어때?", []))