from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


def _format(d: dict) -> str:
    """문서 한 건을 출처 표기 문자열로 만듦."""
    source = d.get("source")
    kind = {"incident": "사건사고", "safety_notice": "안전공지"}.get(source, "")

    title = d.get("title") or (f"외교부 {kind} 자료" if kind else "외교부 자료")
    head = " / ".join(x for x in [title, d.get("date", ""), kind] if x)
    return f"[{head}]\n{d['content']}"


def generate_answer(question: str, docs: list[dict], country: str = "") -> str:
    """근거 문서만 참고해 답변 문장을 만들어 돌려줍니다."""
    context = "\n\n".join(_format(d) for d in docs)
    target = country or "질문에 언급된 국가"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 해외여행 안전정보 도우미이자 해외 국가 사건사고를 다루는 전문가다. "
                f"사용자가 묻는 나라는 '{target}'이다. "
                "아래 지시사항을 반드시 지켜서 답하라.\n"
                "1. 문서가 비어 있으면 '자료가 없습니다'라고 답하라.\n"
                f"2. 문서 내용이 '{target}'이 아닌 다른 나라에 관한 것이면 그 문서는 무시하라. "
                f"쓸 문서가 하나도 남지 않으면 '{target}에 대한 자료가 없습니다'라고 답하라.\n"
                "3. 문서에 질문과 조금이라도 관련된 내용이 있으면 그 부분을 근거로 답하라. "
                "문서가 특정 사건이나 특정 지역에 관한 것이어도, 질문이 그 나라의 안전 전반을 "
                "묻는다면 문서 내용을 요약해 답하라.\n"
                "4. 문서 내용이 질문 주제와 완전히 무관할 때만 '자료가 없습니다'라고 답하고, "
                "영사콜센터(+82-2-3210-0404) 문의를 안내하라.\n"
                "5. 정보를 인용할 때는 반드시 작성 연도를 밝혀라. "
                "대괄호에 자료 종류가 적혀 있을 때만 종류도 함께 밝히고, 없으면 추측하지 마라.\n"
                "6. 추측하거나 일반 상식으로 채우지 마라.\n"
                "7. 최신 자료와 오래된 자료가 함께 있으면 최신 자료를 우선 언급하라.\n"
                "8. 한국어로 간결하고 친근하게 답하라.\n\n"
                "문서:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
    return chain.invoke({"context": context, "question": question})