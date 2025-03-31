from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.solar import Solar
import os
from dotenv import load_dotenv

load_dotenv()

ChecklistInspector_prompt = """
    당신은 M&A 기업 평가를 위한 체크리스트 평가 전문가입니다.
    체크리스트 항목에 대한 점수를 평가하는 역할을 맡고 있습니다.
    다음은 체크리스트 항목과 항목별 만점입니다:
    {checklist}
    그리고 다음은 매수자의 요청입니다:
    {user_query}
    그리고 평가 대상 회사의 정보는 다음과 같습니다:
    {sellside_context}
    각 체크리스트 항목에 대해 매수자의 요청과 평가 대상 회사의 정보를 기반으로 점수를 평가하세요.
    점수는 0에서 항목별 만점 사이의 정수여야 하며, 각 항목에 대한 점수를 JSON 형식으로 반환하세요.
    예: {'항목1': 8, '항목2': 10, '항목3': 5}
"""

class ChecklistInspector:
    def __init__(self, llm_model="solar-pro", temperature=0.7):
        """
        ChecklistInspector 초기화
        :param llm_model: 사용할 LLM 모델 이름
        :param temperature: LLM의 응답 다양성을 조정하는 파라미터
        """
        self.llm = Solar(llm_model=llm_model, temperature=temperature, api_key=os.environ["SOLAR_API_KEY"])
        self.prompt_template = PromptTemplate(
            input_variables=["checklist", "sellside_context"],
            template=(ChecklistInspector_prompt + "\n\n")
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def inspect_checklist(self, checklist: dict, sellside_context: str) -> tuple:
        """
        체크리스트를 평가하고 각 항목의 점수와 총점을 반환
        :param checklist: 체크리스트 딕셔너리 (key: 체크할 항목, value: 배점)
        :param sellside_context: 평가 대상의 요청 문자열
        :return: 각 항목의 점수 딕셔너리와 총점
        """
        # 체크리스트를 문자열로 변환
        checklist_str = "\n".join([f"- {key}: {value}" for key, value in checklist.items()])
        
        # LLMChain 실행
        response = self.chain.run(checklist=checklist_str, sellside_context=sellside_context)
        
        # 응답을 딕셔너리로 변환
        try:
            scores = eval(response)  # JSON 형식의 응답을 딕셔너리로 변환
        except Exception as e:
            raise ValueError(f"LLM 응답을 처리하는 중 오류 발생: {e}")
        
        # 총점 계산
        total_score = sum(scores.values())
        
        return scores, total_score


# Example usage
if __name__ == "__main__":
    checklist = {
        "항목1": 10,
        "항목2": 20,
        "항목3": 15
    }
    sellside_context = "항목1과 항목2에 대한 자세한 설명이 포함되어 있습니다."

    inspector = ChecklistInspector()
    scores, total_score = inspector.inspect_checklist(checklist, sellside_context)
    print("항목별 점수:", scores)
    print("총점:", total_score)