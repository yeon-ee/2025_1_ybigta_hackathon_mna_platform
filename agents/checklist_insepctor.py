from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

class ChecklistInspector:
    def __init__(self, llm_model="solar-pro", api_key=None):
        self.llm = ChatUpstage(api_key=api_key or os.getenv("SOLAR_API_KEY"), model=llm_model, max_tokens=500)
        self.prompt_template = PromptTemplate(
            input_variables=["checklist", "company_name" ,"sellside_context", "user_query"],
            template="""
            당신은 체크리스트 기반 M&A 평가 전문가입니다.
            회사 '{company_name}'의 M&A 평가를 위해 체크리스트를 검토하고 있습니다.
            다음은 체크리스트 항목과 항목별 배점입니다:
            {checklist}

            매수자의 요청:
            {user_query}

            현재까지 확보된 평가 대상 회사의 정보:
            {sellside_context}

            이 정보를 기반으로 아래 JSON 형식으로 응답하세요:
            {{
                "question": "...에 대한 정보가 부족합니다. 추가 정보를 요청합니다.",
                "final_score": {{"항목1": 10, "항목2": 20, ...}}
            }}

            단, 정보가 부족하거나 모호한 항목이 있다면 "question"에 질문 내용을 작성하고 "final_score"는 빈 문자열로 반환하세요.
            대답을 충분히 듣고 평가하기에 정보가 충분하다고 판단되면 "question"은 빈 문자열로 설정하고 "final_score"에 항목별 점수를 JSON 형식으로 작성하세요.
            """
        )

    def evaluate(self, company_name: str, checklist: dict, sellside_context: str, user_query: str) -> dict:
        checklist_str = "\n".join([f"- {key}: {value}" for key, value in checklist.items()])
        prompt = self.prompt_template.format(
            company_name=company_name,
            checklist=checklist_str,
            sellside_context=sellside_context,
            user_query=user_query
        )
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        try:
            result = eval(response.content)
            return result
        except Exception as e:
            return {"question": "LLM 응답 파싱 실패: 정보 제공이 필요합니다.", "final_score": None}
