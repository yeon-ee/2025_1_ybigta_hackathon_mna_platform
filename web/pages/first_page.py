import streamlit as st
import json
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from web.utils.report import process_input_to_report
from web.utils.save_factory import save_image_to_vector_db

st.set_page_config(
    page_title="M&A_Agent",
    layout="wide",  # 전체 화면 너비로 설정
    initial_sidebar_state="collapsed",
)


# Streamlit에서 UI 생성
st.title("M&A_Agent")

# 두 개의 탭 생성
tab1, tab2 = st.tabs(["매수자 페이지", "매도자 페이지"])

# --- 매수자 페이지 ---
with tab1:
    st.header("매수자 페이지")

    # 초기 상태값 설정
    if "search_completed" not in st.session_state:
        st.session_state.search_completed = False
    if "search_result" not in st.session_state:
        st.session_state.search_result = None

    # 1. 검색 전 화면
    if not st.session_state.search_completed:
        user_input = st.text_input("검색할 문자열을 입력하세요:")
        if st.button("검색"):
            if user_input:
                st.session_state.search_result = process_input_to_report(user_input)
                st.session_state.search_completed = True
                st.rerun()  # st.experimental_rerun() 대신 st.rerun() 사용
            else:
                st.error("무언가를 입력하세요!")

    # 2. 검색 후 화면
    else:
        st.success("처리가 완료되었습니다!")
        st.json(st.session_state.search_result)

        if st.button("다시 검색"):
            st.session_state.search_completed = False
            st.session_state.search_result = None
            st.rerun()  # st.experimental_rerun() 대신 st.rerun() 사용

# --- 매도자 페이지 ---
with tab2:
    st.header("매도자 페이지")

    uploaded_image = st.file_uploader("이미지를 업로드하세요:", type=["png", "jpg", "jpeg"])

    if st.button("저장"):
        if uploaded_image:
            save_status = save_image_to_vector_db(uploaded_image)
            st.success(save_status)
        else:
            st.error("이미지를 업로드하세요!")
