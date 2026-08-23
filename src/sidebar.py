import streamlit as st


def render_sidebar():
    """모든 페이지에서 호출. 사이드바 하단에 범례와 연락처를 붙임"""
    with st.sidebar:
        st.markdown("""
        <style>
        .sb-head{padding:4px 8px 16px 8px;border-bottom:1px solid #DDE1E8;margin-bottom:8px;}
        .sb-title{font-size:15px;font-weight:600;color:#0F172A;}
        .sb-sub{font-size:11px;color:#64748B;margin-top:4px;}

        .sb-sec{margin-top:20px;padding-top:14px;border-top:1px solid #DDE1E8;}
        .sb-label{font-size:11px;color:#64748B;margin-bottom:8px;}
        .sb-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
        .sb-dot{width:10px;height:10px;border-radius:3px;display:inline-block;}
        .sb-text{font-size:11px;color:#475569;}

        .sb-call{background:#fff;border-radius:8px;padding:12px;margin-top:20px;}
        .sb-call-label{font-size:11px;color:#64748B;}
        .sb-call-num{font-size:13px;font-weight:600;color:#1D4ED8;margin-top:3px;}
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-sec">
            <div class="sb-label">경보단계</div>
            <div class="sb-row"><span class="sb-dot" style="background:#60A5FA"></span><span class="sb-text">1단계 여행유의</span></div>
            <div class="sb-row"><span class="sb-dot" style="background:#FBBF24"></span><span class="sb-text">2단계 여행자제</span></div>
            <div class="sb-row"><span class="sb-dot" style="background:#F97316"></span><span class="sb-text">3단계 출국권고</span></div>
            <div class="sb-row"><span class="sb-dot" style="background:#DC2626"></span><span class="sb-text">4단계 여행금지</span></div>
        </div>

        <div class="sb-call">
            <div class="sb-call-label">영사콜센터 24시간</div>
            <div class="sb-call-num">+82-2-3210-0404</div>
        </div>
        """, unsafe_allow_html=True)