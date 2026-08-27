def hit(retrieved, gold, k):
    """상위 k개 중 관련 문서가 하나라도 있으면 1, 없으면 0"""
    return 1 if any(p in gold for p in retrieved[:k]) else 0

def precision(retrieved, gold, k):
    """상상위 k개 중 관련 문서의 비율(관련 수 / k)"""
    hits = sum(1 for p in retrieved[:k] if p in gold)
    return hits/k

def recall(retrieved, gold, k):
    """전체 관련 문서 중 상위 k개가 찾아낸 비율(관련 수 / 전체 관련 수)"""
    hits = sum(1 for p in retrieved[:k] if p in gold)
    return hits/len(gold)

def mrr(retrieved, gold, k):
    """첫 번째 관련 문서 순위의 역수. 목록 안에 없으면 0"""
    for i, p in enumerate(retrieved[:k], 1):
        if p in gold:
            return 1/i
    return 0.0