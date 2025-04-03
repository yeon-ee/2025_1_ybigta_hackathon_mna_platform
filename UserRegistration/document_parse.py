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
from typing import List

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("SOLAR_API_KEY")
if not api_key:
    raise ValueError("SOLAR_API_KEY environment variable is not set")

DocumentSummarizer_prompt = """
    당신은 한국 중소기업 전문 M&A 중개인으로써 기업의 비재무적인 요인을 분석하는 데 탁월한 능력을 인정받는 전문가입니다. 
    분기별 재무제표 공시사항은 무시하고, 재무제표에서 파악할 수 있는 내용은 언급하지 말아 주세요. 재무적인 상황 외의 기업의 매력도를 요약 정리하여 구조화된 보고서로 출력해주세요. 
    다만 주장에는 근거를 반드시 작성해주시고 중복되는 내용도 없고 생략되는 내용도 없게 작성 부탁드립니다. 

    직접 인용하지 말고, 문장을 재구성하세요. 

    아래의 구조를 따르세요.
    1. 기업 소개 및 사업 개요
    2. 기업 특장점 및 경쟁력
    3. 시장의 전망
    4. 의견 종합

    너무 짧거나 긴 문서는 신뢰도의 하락으로 이어집니다. 당신의 신분은 숨겨야 합니다. 한국어로 말해.

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

    def process_documents(self, filenames: List[str]) -> str:
        """
        여러 문서 처리 및 요약 전체 프로세스
        :param filenames: PDF 파일 경로 리스트
        :return: 요약된 내용
        """
        try:
            print("1. 문서 내용 추출 중...")
            all_content = []
            
            # 모든 문서의 내용 추출
            for filename in filenames:
                print(f"- {filename} 처리 중...")
                content = self.extract_document_content(filename)
                if content:
                    # HTML 태그 제거
                    if content.strip().startswith('<'):
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text(separator='\n', strip=True)
                    all_content.append(f"[문서: {filename}]\n{content}")
                else:
                    print(f"경고: {filename}에서 내용을 추출할 수 없습니다.")
            
            if not all_content:
                raise ValueError("어떤 문서에서도 내용을 추출할 수 없습니다.")
            
            # 모든 문서 내용을 하나로 합침
            combined_content = "\n\n---\n\n".join(all_content)
            
            print("2. 통합 내용 요약 중...")
            # 프롬프트 생성 및 LLM 호출
            prompt = self.prompt_template.format(document_content=combined_content)
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            return response.content
            
        except Exception as e:
            raise Exception(f"문서 처리 중 오류 발생: {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        # 여러 파일 처리 예시
        filenames = [
            "Dataset/meatbox/meatbox_explain.pdf",
            "Dataset/meatbox/meatbox_IR.pdf",  # 예시 파일명
        ]
        
        summarizer = DocumentSummarizer()
        summary = summarizer.process_documents(filenames)
        
        print("\n=== 요약 결과 ===")
        print(summary)
        
    except Exception as e:
        print(f"오류 발생: {e}")