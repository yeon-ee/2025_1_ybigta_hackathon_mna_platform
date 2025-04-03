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

def display_companies(results):
    # 회사별 총점 계산 및 정렬
    companies_with_scores = []
    for company_name, data in results.items():
        total_score = sum(data['score'].values())
        companies_with_scores.append((company_name, data, total_score))

    sorted_companies = sorted(companies_with_scores, key=lambda x: x[2], reverse=True)

    # 두 개의 회사씩 나란히 표시
    for i in range(0, len(sorted_companies), 2):
        cols = st.columns(2, gap="large")

        # 왼쪽 칼럼
        with cols[0]:
            company_name, data, total_score = sorted_companies[i]
            with st.container():
                st.markdown(f"# {i + 1}위: {company_name}")
                st.markdown(f"## 총점: {total_score}점")

                for criterion in data['score'].keys():
                    with st.expander(f"{criterion} (점수: {data['score'][criterion]}점)"):
                        st.markdown(data['comment'][criterion])

        # 오른쪽 칼럼 (남은 회사가 있을 경우)
        if i + 1 < len(sorted_companies):
            with cols[1]:
                company_name, data, total_score = sorted_companies[i + 1]
                with st.container():
                    st.markdown(f"# {i + 2}위: {company_name}")
                    st.markdown(f"## 총점: {total_score}점")

                    for criterion in data['score'].keys():
                        with st.expander(f"{criterion} (점수: {data['score'][criterion]}점)"):
                            st.markdown(data['comment'][criterion])


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
        display_companies(st.session_state.search_result)


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

        # 기업명
        company_name = st.text_input("기업명")

        # 카테고리 선택
        category = st.selectbox(
            "카테고리",
            options=[
                "모빌리티/교통",
                "금융/보험/핀테크",
                "AI/딥테크/블록체인",
                "커머스",
                "교육",
                "부동산/건설",
                "헬스케어",
                "F&B",
                "콘텐츠"
            ]
        )

        # 주요정보 섹션
        st.subheader("주요정보")

        # 금액 관련 정보 (억 단위)
        capital = st.number_input("자본금 (억 원)", min_value=0, value=0)
        investment = st.number_input("누적투자유치금액 (억 원)", min_value=0, value=0)
        investment_count = st.number_input("투자유치건수", min_value=0, value=0)
        annual_sales = st.number_input("연매출 (억 원)", min_value=0, value=0)

        # 기술등급 입력
        st.subheader("기술등급")
        st.caption("각 등급별 특허 개수를 입력하세요")
        tech_grade_count = st.number_input("특허 개수 입력", min_value=0, value=0)


        # 기술등급 변환 함수
        def convert_to_tech_grade(count):
            if count >= 8:
                return "A+"

            grade_map = {
                8: "A+",
                7: "A0",
                6: "A-",
                5: "B+",
                4: "B0",
                3: "B-",
                2: "C"
            }
            return grade_map.get(count, "C")  # 기본값 C

    # 저장 버튼은 컬럼 밖에 배치
    if st.button("저장", type="primary"):
        # 모든 필수 입력값 확인
        if not non_financial_pdfs:
            st.warning("비재무 PDF 파일을 업로드해주세요.")
            st.stop()

        if not financial_pdf:
            st.warning("재무 PDF 파일을 업로드해주세요.")
            st.stop()

        if not company_name:
            st.warning("기업명을 입력해주세요.")
            st.stop()

        if capital <= 0:
            st.warning("자본금을 입력해주세요.")
            st.stop()

        if investment <= 0:
            st.warning("누적투자유치금액을 입력해주세요.")
            st.stop()

        if investment_count <= 0:
            st.warning("투자유치건수를 입력해주세요.")
            st.stop()

        if annual_sales <= 0:
            st.warning("연매출을 입력해주세요.")
            st.stop()

        if tech_grade_count <= 0:
            st.warning("특허 개수를 입력해주세요.")
            st.stop()

        try:
            # 입력 데이터를 딕셔너리로 구성
            tech_grade = convert_to_tech_grade(tech_grade_count)
            user_input = {
                "company_name": company_name,
                "category": category,
                "capital": capital,
                "investment": investment,
                "investment_count": investment_count,
                "annual_sales": annual_sales,
                "tech_grade": tech_grade
            }

            result, metadata = extract_company_info(non_financial_pdfs, financial_pdf, user_input)
            st.success("성공적으로 저장되었습니다!")
            # st.json(metadata)
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {str(e)}")


