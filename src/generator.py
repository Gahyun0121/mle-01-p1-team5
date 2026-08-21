from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


def _format(d: dict) -> str:
    """문서 한 건을 출처 표기 문자열로 만듦."""
    # source가 없으면 추정하지 않음. 틀린 출처를 답변에 쓰는 것보다 생략이 안전
    source = d.get("source")
    kind = {"incident": "사건사고", "safety_notice": "안전공지"}.get(source, "")

    title = d.get("title") or f"외교부 {kind} 자료".replace("  ", " ").strip()
    head = " / ".join(x for x in [title, d.get("date", ""), kind] if x)
    return f"[{head}]\n{d['content']}"


def generate_answer(question: str, docs: list[dict]) -> str:
    """근거 문서만 참고해 답변 문장을 만들어 돌려줍니다."""
    context = "\n\n".join(_format(d) for d in docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "1. 문서가 비어 있으면 '자료가 없습니다'라고 답하라.\n"
                "2. 문서에 질문과 조금이라도 관련된 내용이 있으면 그 부분을 근거로 답하라. "
                "문서가 특정 사건이나 특정 지역에 관한 것이어도, 질문이 그 나라의 안전 전반을 "
                "묻는다면 문서 내용을 요약해 답하라.\n"
                "3. 문서 내용이 질문 주제와 완전히 무관할 때만 '자료가 없습니다'라고 답하고, "
                "영사콜센터(+82-2-3210-0404) 문의를 안내하라.\n"
                "4. 정보를 인용할 때는 반드시 작성 연도를 밝혀라. "
                "대괄호에 자료 종류가 적혀 있을 때만 종류도 함께 밝히고, 없으면 추측하지 마라.\n"
                "5. 추측하거나 일반 상식으로 채우지 마라.\n"
                "6. 최신 자료와 오래된 자료가 함께 있으면 최신 자료를 우선 언급하라.\n"
                "7. 한국어로 간결하고 친근하게 답하라.\n\n"
                "문서:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
    return chain.invoke({"context": context, "question": question})