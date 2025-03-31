from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.solar import Solar
import os
from dotenv import load_dotenv

load_dotenv()

class SellSideAgent:
    def __init__(self, db_stub, llm_model="solar-pro", temperature=0.7):
        """
        SellSideAgent 초기화
        :param db_stub: DB에서 데이터를 검색하는 함수 (stub 처리)
        :param llm_model: 사용할 LLM 모델 이름
        :param temperature: LLM의 응답 다양성을 조정하는 파라미터
        """
        self.db_stub = db_stub
        self.llm = Solar(llm_model=llm_model, temperature=temperature, api_key=os.environ["SOLAR_API_KEY"])
        self.context_prompt = PromptTemplate(
            input_variables=["company_data", "checklist"],
            template=(
                "다음은 회사에 대한 데이터입니다:\n"
                "{company_data}\n\n"
                "그리고 다음은 평가를 위한 체크리스트입니다:\n"
                "{checklist}\n\n"
                "이 데이터를 기반으로 체크리스트 평가에 필요한 컨텍스트를 생성하세요. "
                "컨텍스트는 평가자가 체크리스트를 평가할 수 있도록 충분히 구체적이어야 합니다."
            )
        )
        self.context_chain = LLMChain(llm=self.llm, prompt=self.context_prompt)

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
        
        # LLMChain을 사용하여 컨텍스트 생성
        context = self.context_chain.run(company_data=company_data, checklist=checklist_str)
        return context


# Stub function for DB access
def db_stub(company_name: str) -> str:
    """
    Stub: 회사명으로 DB에서 데이터를 검색하는 함수
    :param company_name: 평가 대상 회사명
    :return: 회사 관련 정보를 포함한 문자열
    """
    # Stub 데이터
    return f"{company_name}에 대한 재무 정보, 시장 점유율, 제품 설명 등이 포함된 데이터입니다."


# Example usage
if __name__ == "__main__":
    checklist = {
        "재무 안정성": 10,
        "시장 점유율": 20,
        "제품 경쟁력": 15
    }
    company_name = "ABC Corp"

    agent = SellSideAgent(db_stub=db_stub)
    context = agent.generate_context(company_name, checklist)
    print("생성된 컨텍스트:", context)