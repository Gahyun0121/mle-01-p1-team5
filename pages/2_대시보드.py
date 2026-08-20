import streamlit as st
from src.viz_map import load_alarm, make_alarm_map

st.title("대시보드")

@st.cache_data          # 페이지 전환할 때마다 csv 다시 안 읽게
def load():
    return load_alarm()

df = load()

st.plotly_chart(make_alarm_map(df), use_container_width=True)
st.caption("시각적 참고용, 자세한 정보는 챗봇이나 검색 서비스를 이용해주세요.")

# TODO: 차트 1 - 담당 OOO
# TODO: 차트 2 - 담당 OOO