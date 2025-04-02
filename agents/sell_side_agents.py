from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

SellSideAgent_prompt = """
    당신은 당신의 회사 {company_name} 소속의 전문가입니다.
    당신의 회사 {company_name}의 M&A 매도자로서 체크리스트 기반 평가를 받을 예정입니다.
    당신은 체크리스트 평가자를 돕기 위해 제공할 컨텍스트를 생성해야 합니다.
    당신의 회사 {company_name}의 M&A 매도자로서 체크리스트 기반 평가를 받을 예정입니다.
    당신은 체크리스트 평가자를 돕기 위해 제공할 컨텍스트를 생성해야 합니다.
    다음은 당신의 회사에 대한 데이터입니다:
    {company_data}
    그리고 다음은 평가자가 평가에 사용할 체크리스트 항목입니다:
    {checklist_keys}
    그리고 다음은 평가자가 평가에 사용할 체크리스트 항목입니다:
    {checklist_keys}
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
        self.llm = ChatUpstage(api_key=api_key or os.getenv("SOLAR_API_KEY"), model=llm_model, max_tokens=2000)
        self.prompt_template = PromptTemplate(
            input_variables=["company_name", "company_data", "checklist_keys"],
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
        
        # 체크리스트 항목들을 문자열로 변환
        checklist_keys = "\n".join([f"- {key}" for key, value in checklist.items()])
        # 체크리스트 항목들을 문자열로 변환
        checklist_keys = "\n".join([f"- {key}" for key, value in checklist.items()])
        
        # 프롬프트 생성
        prompt = self.prompt_template.format(
            company_name=company_name,
            company_data=company_data,
            checklist_keys=checklist_keys
        )
        prompt = self.prompt_template.format(
            company_name=company_name,
            company_data=company_data,
            checklist_keys=checklist_keys
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
    return f"{company_name}는 PT 강사 매칭 플랫폼으로, 2023년 매출 1235604450원을 기록하고 있으며, 2022년 6월에 200억원, 2021년 3월에 100억원의 투자금을 유치했습니다. 최근 3년 YoY Growth 30%입니다. 총 부채는 150000000000이며, 자기자본은 50000000000입니다."
    return f"{company_name}는 PT 강사 매칭 플랫폼으로, 2023년 매출 1235604450원을 기록하고 있으며, 2022년 6월에 200억원, 2021년 3월에 100억원의 투자금을 유치했습니다. 최근 3년 YoY Growth 30%입니다. 총 부채는 150000000000이며, 자기자본은 50000000000입니다."


# Example usage
if __name__ == "__main__":
    checklist = {
        "업종": 20,
        "연매출": 15,
        "투자유치": 25,
        "부채비율": 30,
        "영업이익률": 10
        "업종": 20,
        "연매출": 15,
        "투자유치": 25,
        "부채비율": 30,
        "영업이익률": 10
    }
    company_name = "동연컴퍼니"

    agent = SellSideAgent(db_stub=db_stub)
    agent = SellSideAgent(db_stub=db_stub)
    context = agent.generate_context(company_name, checklist)
    print("생성된 컨텍스트:", context)