from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def _format(d:dict) -> str:
    """문서 한 건을 출처 표기 문자열로 만듦"""
    title = d.get("title") or "외교부 사건사고 정보"
    return f"[{title}] / {d['date']}\n {d['content']}"

def generate_answer(question: str, docs: list[dict]) -> str:
    """근거 문서만 참고해 답변 문장을 만들어 돌려줍니다."""

    context = "\n\n".join(_format(d) for d in docs)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 해외여행 안전정보 도우미이자 해외 국가 사건사고를 다루는 전문가다. "
                "아래 지시사항을 반드시 지켜서 답하라.\n"
                "1. 문서가 비어 있으면 '자료가 없습니다'라고 답하라.\n"
                "2. 문서가 있어도 질문과 관련 없으면 '자료가 없습니다'라고 답하고, "
                "영사콜센터(+82-2-3210-0404) 문의를 안내하라.\n"
                "3. 정보를 인용할 때는 반드시 작성 연도를 함께 밝혀라.\n"
                "4. 추측하거나 일반 상식으로 채우지 마라.\n\n"
                "5. 한국어로 간결하고 친근하게 답할 것.\n"
                "6. 최신 자료와 오래된 자료가 함께 있으면 최신 자료를 우선 언급하라.\n"
                "문서:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
    #temperature=0으로 설정하면 모델이 항상 같은 답변을 내놓음 -> 안전정보 챗봇에 적합한 설정
    return chain.invoke({"context": context, "question": question})