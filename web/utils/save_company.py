from pathlib import Path

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
    return save_image_to_vector_db(non_financial_pdfs, financial_pdf, test_input)


# 매도자: 예제 함수를 정의 (이미지를 벡터 DB에 저장)
def save_image_to_vector_db(non_financial_pdfs, financial_pdf, user_input):

    return "asdfasdfasdf", {"asdfs":"sdafdsf"}

if __name__ == "__main__":
    result, metadata = load_test_pdfs(
        non_financial_dir="./test_data/non_financial",
        financial_dir="./test_data/financial"
    )
