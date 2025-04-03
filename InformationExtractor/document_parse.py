# pip install requests python-dotenv beautifulsoup4
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import requests
import os
import json
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("SOLAR_API_KEY")
if not api_key:
    raise ValueError("SOLAR_API_KEY environment variable is not set")

DocumentSummarizer_prompt = """
    당신은 문서 요약 전문가입니다.
    주어진 문서의 내용을 분석하여 핵심적인 내용만 간단히 요약해주세요.
    불필요한 설명은 제외하고 중요한 내용만 추출하여 알기 쉽게 정리해주세요.

    문서 내용:
    {document_content}
"""

class DocumentSummarizer:
    def __init__(self, llm_model="solar-pro", api_key=None):
        """
        DocumentSummarizer 초기화
        :param llm_model: 사용할 LLM 모델 이름
        :param api_key: Upstage API 키
        """
        self.api_key = api_key or os.getenv("SOLAR_API_KEY")
        self.llm = ChatUpstage(api_key=self.api_key, model=llm_model)
        self.prompt_template = PromptTemplate(
            input_variables=["document_content"],
            template=DocumentSummarizer_prompt
        )

    def extract_document_content(self, filename: str) -> str:
        """
        문서에서 텍스트 추출
        :param filename: PDF 파일 경로
        :return: 추출된 텍스트
        """
        url = "https://api.upstage.ai/v1/document-digitization"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        with open(filename, "rb") as file:
            files = {"document": file}
            data = {
                "ocr": "true",
                "model": "document-parse",
                "language": "ko"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            
            json_response = response.json()
            if "content" in json_response:
                return json_response["content"].get("html", "")
        return ""

    def summarize(self, document_content: str) -> str:
        """
        문서 내용 요약
        :param document_content: 요약할 문서 내용
        :return: 요약된 내용
        """
        # HTML 태그 제거
        if document_content.strip().startswith('<'):
            soup = BeautifulSoup(document_content, 'html.parser')
            document_content = soup.get_text(separator='\n', strip=True)

        # 프롬프트 생성
        prompt = self.prompt_template.format(document_content=document_content)
        
        # LLM 호출
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        return response.content

    def process_document(self, filename: str) -> str:
        """
        문서 처리 및 요약 전체 프로세스
        :param filename: PDF 파일 경로
        :return: 요약된 내용
        """
        try:
            print("1. 문서 내용 추출 중...")
            document_content = self.extract_document_content(filename)
            
            if not document_content:
                raise ValueError("문서 내용을 추출할 수 없습니다.")
            
            print("2. 내용 요약 중...")
            summary = self.summarize(document_content)
            
            return summary
            
        except Exception as e:
            raise Exception(f"문서 처리 중 오류 발생: {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        filename = "Dataset/meatbox/meatbox_explain.pdf"
        summarizer = DocumentSummarizer()
        summary = summarizer.process_document(filename)
        
        print("\n=== 요약 결과 ===")
        print(summary)
        
    except Exception as e:
        print(f"오류 발생: {e}")