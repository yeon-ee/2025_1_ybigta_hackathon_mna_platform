from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.solar import Solar
import os
from dotenv import load_dotenv

load_dotenv()

ChecklistReviewer_prompt = """
    당신은 M&A 기업 평가를 위한 체크리스트 검수 전문가입니다.
    당신은 체크리스트 항목에 대한 매수자의 요청을 검토하고,
    유저의 요청에 포함된 정보가 부족한 항목을 체크리스트에서 제외해야 합니다.
    체크리스트 항목과 항목별 만점은 다음과 같습니다:
    {checklist}
    그리고 매수자의 요청은 다음과 같습니다:
    {user_query}
    체크리스트 항목 중에서 매수자의 요청에 포함된 정보가 부족한 항목을 제외하세요.
    제외할 항목은 JSON 형식으로 반환하세요. 예: ['항목1', '항목2']
"""

class ChecklistReviewer:
    def __init__(self, llm_model="solar-pro", temperature=0.7):
        """
        ChecklistReviewer 초기화
        :param llm_model: 사용할 LLM 모델 이름
        :param temperature: LLM의 응답 다양성을 조정하는 파라미터
        """
        self.llm = Solar(llm_model=llm_model, temperature=temperature, api_key=os.environ["SOLAR_API_KEY"])
        self.prompt_template = PromptTemplate(
            input_variables=["checklists", "user_query"],
            template=(ChecklistReviewer_prompt + "\n\n")
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def review_checklist(self, checklist: dict, user_query: str) -> list:
        """
        체크리스트를 검수하고 제외할 항목을 반환
        :param checklist: 체크리스트 딕셔너리 (key: 체크할 항목, value: 배점)
        :param user_query: 유저의 요청 문자열
        :return: 제외할 항목 리스트
        """
        # 체크리스트를 문자열로 변환
        checklist_str = "\n".join([f"- {key}: {value}" for key, value in checklist.items()])
        
        # LLMChain 실행
        response = self.chain.run(checklist=checklist_str, user_query=user_query)
        
        # 응답을 리스트로 변환
        excluded_items = [item.strip() for item in response.split(",") if item.strip()]
        return excluded_items


# Example usage
if __name__ == "__main__":
    checklist = {
        "항목1": 10,
        "항목2": 20,
        "항목3": 15
    }
    user_query = "항목1에 대한 자세한 설명만 포함되어 있습니다."

    reviewer = ChecklistReviewer()
    excluded_items = reviewer.review_checklist(checklist, user_query)
    print("제외할 항목:", excluded_items)