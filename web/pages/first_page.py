import chromadb
from chromadb import Settings
import streamlit as st
import json
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
chroma_path = os.path.join(web_root, "db", "chroma_data")

from web.db.vector_db import connect_to_vector_db
from web.utils.report import process_input_to_report
from web.utils.save_company import save_image_to_vector_db

st.set_page_config(
    page_title="M&A_Agent",
    layout="wide",  # 전체 화면 너비로 설정
    initial_sidebar_state="collapsed",
)


if 'chroma_collection' not in st.session_state:
    st.session_state.chroma_collection = connect_to_vector_db()

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
                # # 디버깅 정보 출력
                # st.write(f"현재 작업 디렉토리: {os.getcwd()}")
                # st.write(f"프로젝트 루트: {project_root}")
                #
                # # ChromaDB 경로 확인
                # chroma_path = os.path.join(project_root, "chroma_data")
                # st.write(f"ChromaDB 경로: {chroma_path}")
                # st.write(f"ChromaDB 경로 존재?: {os.path.exists(chroma_path)}")

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
