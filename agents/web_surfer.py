from langchain_community.document_loaders import WebBaseLoader
from langchain.tools import Tool
from typing import Optional
import logging


class WebSurfer:
    """inno_company.json 파일 내 기업의 보도자료 URL을 크롤링하는 클래스"""
    
    def __init__(self):
        self.name = "web_surfer"
        self.description = "웹 페이지의 내용을 수집하고 처리하는 도구입니다."

    def fetch_content(self, url: str) -> Optional[str]:
        """
        주어진 URL의 웹 페이지 내용을 가져옴
        :param url: 웹 페이지 URL
        :return: 웹 페이지 내용 또는 에러 시 None
        """
        try:
            loader = WebBaseLoader(
                url,
                verify_ssl=False,
            )
            docs = loader.load()
            content = "\n".join([doc.page_content for doc in docs])
            return content
        except Exception as e:
            logging.error(f"Error fetching content from {url}: {str(e)}")
            return None

    def create_tools(self) -> list[Tool]:
        """
        웹 서핑 관련 도구들을 생성
        :return: Tool 객체 리스트
        """
        return [
            Tool(
                name="fetch_webpage_content",
                func=self.fetch_content,
                description="웹 페이지의 내용을 가져옵니다. 입력: URL 문자열"
            )
        ]

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    web_surfer = WebSurfer()
    tools = web_surfer.create_tools()
    
    # 테스트 URL
    test_url = "https://www.dnews.co.kr/uhtml/view.jsp?idxno=202105141046002310246"
    
    print(f"테스트 URL: {test_url}")
    content = tools[0].run(test_url)
    
    if content:
        print("웹 페이지 내용 수집 성공:")
        print(content[:200].replace('\n', ' ') + "...")
        print(f"총 텍스트 길이: {len(content)} 자")
    else:
        print("웹 페이지 내용 수집 실패")
    