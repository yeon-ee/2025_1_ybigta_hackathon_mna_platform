import os
import tempfile
from pathlib import Path

from web.utils.document_parse import DocumentSummarizer
from web.utils.financial_info_extractor import add_new_company

def load_test_pdfs(non_financial_dir: str, financial_dir: str):
    """
    개발/테스트용 함수: 저장된 PDF 파일들을 읽어서 save_image_to_vector_db 함수에 전달하기 위한 형식으로 변환

    Args:
        non_financial_dir (str): 비재무 PDF 파일들이 있는 테스트 디렉토리
        financial_dir (str): 재무 PDF 파일이 있는 테스트 디렉토리
    """
    # 비재무 PDF 파일들 로드
    non_financial_pdfs = []
    for pdf_path in Path(non_financial_dir).glob("*.pdf"):
        with open(pdf_path, 'rb') as f:
            non_financial_pdfs.append(f.read())

    # 재무 PDF 파일 로드 (첫 번째 파일)
    financial_path = next(Path(financial_dir).glob("*.pdf"))
    with open(financial_path, 'rb') as f:
        financial_pdf = f.read()

    # 테스트용 입력 데이터
    test_input = {"test": "data"}

    # 실제 함수 호출
    return extract_company_info(non_financial_pdfs, financial_pdf, test_input)



def extract_company_info(non_financial_pdfs, financial_pdf, user_input):
    """
    회사 정보 추출 함수

    Args:
        non_financial_pdfs (list): Streamlit의 UploadedFile 객체들의 리스트
        financial_pdf: Streamlit의 UploadedFile 객체
        user_input (dict): 사용자 입력 데이터
    """
    temp_files = []
    try:
        # 비재무 PDF들 임시 저장
        non_financial_paths = []
        for pdf in non_financial_pdfs:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf.getvalue())
                non_financial_paths.append(tmp_file.name)
                temp_files.append(tmp_file.name)

        # 재무 PDF 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(financial_pdf.getvalue())
            financial_path = tmp_file.name
            temp_files.append(tmp_file.name)

        # 여기서 실제 파일 처리 로직 수행
        print("=== 입력값 확인 ===")
        print(f"비재무 PDF 파일 수: {len(non_financial_paths)}")
        print(f"재무 PDF 파일: {financial_path}")
        print(f"사용자 입력값: {user_input}")

        # DocumentSummarizer를 사용하여 문서 처리
        summarizer = DocumentSummarizer()
        summary = summarizer.process_documents(non_financial_paths)
        print("summary: " + summary)

        success, info_extract_result = add_new_company(financial_path, user_input)
        print("info_extract_result: " + str(info_extract_result))

        return summary, info_extract_result

    finally:
        # 임시 파일들 삭제
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


if __name__ == "__main__":
    result, metadata = load_test_pdfs(
        non_financial_dir="./test_data/non_financial",
        financial_dir="./test_data/financial"
    )
