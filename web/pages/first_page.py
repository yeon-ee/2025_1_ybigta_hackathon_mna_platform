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
from web.utils.save_company import extract_company_info

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

    # 3개의 컬럼 생성
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("비재무 PDF 파일")
        non_financial_pdfs = st.file_uploader(
            "비재무 PDF 파일들을 업로드하세요",
            type=["pdf"],
            accept_multiple_files=True
        )
        if non_financial_pdfs:
            st.success(f"{len(non_financial_pdfs)}개의 파일이 업로드됨")
            for pdf in non_financial_pdfs:
                st.write(f"📄 {pdf.name}")

    with col2:
        st.subheader("재무 PDF 파일")
        financial_pdf = st.file_uploader(
            "재무 PDF 파일을 업로드하세요",
            type=["pdf"],
            accept_multiple_files=False
        )
        if financial_pdf:
            st.success(f"파일 업로드됨: {financial_pdf.name}")

    with col3:
        st.subheader("추가 정보 입력")
        # 여기에 추가 필드들이 들어갈 예정
        st.info("추가 필드는 곧 업데이트될 예정입니다")

    # 저장 버튼은 컬럼 밖에 배치
    if st.button("저장", type="primary"):
        if non_financial_pdfs and financial_pdf:
            try:
                result, metadata = extract_company_info(non_financial_pdfs, financial_pdf, {})
                st.success("성공적으로 저장되었습니다!")
                st.json(metadata)
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("모든 필수 파일을 업로드해주세요.")

