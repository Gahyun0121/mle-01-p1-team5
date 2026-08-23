import sys
from pathlib import Path
from src.sidebar import render_sidebar

sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.retriever import search_documents
from src.generator import generate_answer

st.set_page_config(page_title="안전 Q&A", page_icon="💬", layout="centered")
render_sidebar()

st.markdown("""
<style>
.block-container { max-width: 58rem; }
[data-testid="stBottomBlockContainer"] { max-width: 58rem; }

[data-testid="stChatMessage"] { background: transparent; padding: 2px 0; }
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] { display: none; }

.page-title { font-size: 44px; font-weight: 600; color: #2c3742; margin-bottom: 14px; }

.bubble-user {
    background: #dbeafe;
    color: #1e3a5f;
    padding: 10px 16px;
    border-radius: 14px;
    display: inline-block;
    max-width: 78%;
    float: right;
    clear: both;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 6px;
}
.bubble-bot {
    color: #2c3742;
    padding: 10px 2px;
    display: block;
    clear: both;
    font-size: 14px;
    line-height: 1.75;
    margin-bottom: 4px;
}
.src {
    color: #9aa7b3;
    font-size: 12px;
    clear: both;
    display: block;
    margin: 0 0 18px 2px;
}
.stButton button {
    border-radius: 16px;
    border: 1px solid #dde3e9;
    background: #fff;
    color: #55636f;
    font-size: 13px;
    padding: 4px 14px;
    width: 100%;
}
.stButton button:hover { border-color: #9cc3e0; color: #2d6a9f; }
hr { margin: 10px 0 18px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🔍 안전 Q&A</div>', unsafe_allow_html=True)


@st.cache_data
def load_countries():
    inc = pd.read_csv("data/incident_info_clean.csv")
    inc = inc[inc["사건사고내용_clean"].notna()]
    return sorted(inc["국가명"].dropna().unique())


def kind_of(d):
    return {"incident": "외교부 사건사고", "safety_notice": "외교부 안전공지"}.get(
        d.get("source"), "외교부 자료"
    )


def source_line(docs):
    if not docs:
        return ""
    d = docs[0]
    label = kind_of(d)
    title = d.get("title")
    if title:
        label = f"{label} · {title}"
    return f'<span class="src">📄 {label} · {d["date"]}</span>'


countries = load_countries()
st.caption("궁금한 국가를 선택하세요.")
default = st.session_state.get("selected_country")
idx = countries.index(default) if default in countries else 0
country = st.selectbox("국가", countries, index=idx, label_visibility="collapsed")

examples = ["사건사고가 있어?", "주의할 사기 유형", "안전 유의사항"]
cols = st.columns(len(examples))
picked = None
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        picked = ex

st.divider()

if st.session_state.get("country") != country:
    st.session_state.country = country
    st.session_state.messages = []

for m in st.session_state.get("messages", []):
    if m["role"] == "user":
        st.markdown(f'<div class="bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-bot">{m["content"]}</div>', unsafe_allow_html=True)
        if m.get("docs") and "자료가 없습니다" not in m["content"]:
            st.markdown(source_line(m["docs"]), unsafe_allow_html=True)

typed = st.chat_input(f"{country}에 대해 궁금한 점을 입력하세요")
question = picked or typed

if question:
    st.markdown(f'<div class="bubble-user">{question}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": question, "docs": []})

    with st.spinner(""):
        docs = search_documents(f"{country} {question}")
        answer = generate_answer(question, docs, country)

    st.markdown(f'<div class="bubble-bot">{answer}</div>', unsafe_allow_html=True)
    if docs and "자료가 없습니다" not in answer:
        st.markdown(source_line(docs), unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": answer, "docs": docs})