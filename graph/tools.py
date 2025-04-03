import json
from langchain.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()

@tool
def fetch_from_db(input: str) -> str:
    """ 입력: 회사명 
        출력: DB 속 회사에 대한 정보"""
    data_file_path = os.getenv("DATA_FILE_PATH")
    with open(data_file_path, 'r', encoding='utf-8') as file:
        dummy_db = json.load(file)
    result = dummy_db.get(input)
    if result:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return f"'{input}'에 대한 정보가 없습니다."

@tool
def search_web(input: str) -> str:
    """지금은 데모 단계라서 사용하지 않음"""
    if input.strip() != "업스테이지":
        return f"'{input}'에 대한 웹 검색은 허용되지 않습니다. 검색 가능한 회사는 '업스테이지'뿐입니다."
    return f"[MOCKED] 업스테이지에 대한 추가 웹 검색 결과가 없습니다." 

