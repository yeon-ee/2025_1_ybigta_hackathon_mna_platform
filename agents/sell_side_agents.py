from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

SellSideAgent_prompt = """
    당신은 당신의 회사 {company_name} 소속의 전문가입니다.
    당신은 당신의 회사 {company_name}의 M&A 기업 평가를 위한 체크리스트 평가를 위한 컨텍스트를 생성하는 역할을 맡고 있습니다.
    다음은 당신의 회사에 대한 데이터입니다:
    {company_data}
    그리고 다음은 평가를 위한 체크리스트입니다:
    {checklist}
    이 데이터를 기반으로 체크리스트 평가에 필요한 컨텍스트를 생성하세요.
    컨텍스트는 평가자가 체크리스트를 평가할 수 있도록 충분히 구체적이어야 합니다.
    또한 주어진 데이터를 기반으로 한 정확한 사실만을 담아야 합니다.
"""

class SellSideAgent:
    def __init__(self, db_stub, llm_model="solar-pro", api_key=None):
        """
        SellSideAgent 초기화
        :param db_stub: DB에서 데이터를 검색하는 함수 (stub 처리)
        :param llm_model: 사용할 LLM 모델 이름
        :param api_key: Upstage API 키
        """
        self.db_stub = db_stub
        self.llm = ChatUpstage(api_key=api_key or os.getenv("SOLAR_API_KEY"), model=llm_model)
        self.prompt_template = PromptTemplate(
            input_variables=["company_name", "company_data", "checklist"],
            template=SellSideAgent_prompt
        )

    def fetch_company_data(self, company_name: str) -> str:
        """
        회사명으로 DB에서 필요한 데이터를 검색 (stub 처리)
        :param company_name: 평가 대상 회사명
        :return: 회사 관련 정보를 포함한 문자열
        """
        # Stub: DB에서 데이터를 검색하는 부분
        company_data = self.db_stub(company_name)
        return company_data

    def generate_context(self, company_name: str, checklist: dict) -> str:
        """
        회사명과 체크리스트를 기반으로 평가에 필요한 컨텍스트를 생성
        :param company_name: 평가 대상 회사명
        :param checklist: 체크리스트 딕셔너리
        :return: 평가에 필요한 컨텍스트 문자열
        """
        # 회사 데이터를 DB에서 검색
        company_data = self.fetch_company_data(company_name)
        
        # 체크리스트를 문자열로 변환
        checklist_str = "\n".join([f"- {key}: {value}" for key, value in checklist.items()])
        
        # 프롬프트 생성
        prompt = self.prompt_template.format(
            company_name=company_name,
            company_data=company_data,
            checklist=checklist_str
        )
        
        # LLM 호출
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        return response.content


# Stub function for DB access
def db_stub(company_name: str) -> str:
    """
    Stub: 회사명으로 DB에서 데이터를 검색하는 함수
    :param company_name: 평가 대상 회사명
    :return: 회사 관련 정보를 포함한 문자열
    """
    # Stub 데이터
    return f"{company_name}는 항목1, 항목3은 만족하지만, 항목2는 만족하지 않습니다."


# Example usage
if __name__ == "__main__":
    checklist = {
        "항목1": 10,
        "항목2": 20,
        "항목3": 15
    }
    company_name = "동연컴퍼니"

    agent = SellSideAgent(db_stub=db_stub, api_key="up_0ZIArDeLVB1tT2peOzqjjrnat91un")
    context = agent.generate_context(company_name, checklist)
    print("생성된 컨텍스트:", context)