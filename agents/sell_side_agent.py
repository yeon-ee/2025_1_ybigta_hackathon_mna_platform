from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
import os
from dotenv import load_dotenv
import json

load_dotenv()

@tool
def fetch_from_db(input: str) -> str:
    """
    회사 이름을 받아 DB에서 모든 정보를 조회합니다.
    입력 형식: "회사명"
    """
    dummy_db = {
        "핀업": {
            "url": "https://www.innoforest.co.kr/company/CP00011911/%ED%95%80%EC%97%85",
            "기업명": "핀업",
            "기업소개": "주식 종목 추천 및 투자(금융, 재테크, 창업 등) 강의 플랫폼 '핀업'을 운영하는 기업",
            "상장여부": "비상장",
            "설립일": "2015-06-30",
            "홈페이지": "http://stock.finup.co.kr/",
            "주소": "서울 강남구",
            "카테고리": ["금융/보험/핀테크", "AI/딥테크/블록체인", "교육", "투자"],
            "자본금": "7.0억원",
            "고용인원": "21명",
            "연매출": "98.5억원",
            "영업이익": "8.9억",
            "순이익": "1.1억",
            "자산": "277.2억",
            "부채": "165.7억",
            "자본": "111.6억"
        }
    }
    result = dummy_db["핀업"]
    if result:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return f"'{input}'에 대한 정보가 없습니다."

@tool
def search_web(input: str) -> str:
    """
    웹 검색 도구는 데모용으로 제한되어 있으며, 오직 '핀업' 관련 정보만 검색할 수 있습니다.
    """
    if input.strip() != "핀업":
        return f"'{input}'에 대한 웹 검색은 허용되지 않습니다. 검색 가능한 회사는 '핀업'뿐입니다."
    return f"[MOCKED] 핀업에 대한 추가 웹 검색 결과가 없습니다."

class SellSideAgent:
    def __init__(self, llm_model="solar-pro", api_key=None):
        self.llm = ChatUpstage(api_key=api_key or os.getenv("SOLAR_API_KEY"), model=llm_model)
        self.tools = [fetch_from_db, search_web]

    def fetch(self, company_name: str, question: str, current_context: str) -> str:
        system_message = f"""
        당신은 {company_name}의 M&A 매도자입니다. 당신의 역할은 평가자가 요청한 정보를 정확히 제공하는 것입니다.

        도구 사용 규칙:
        1. 반드시 fetch_from_db 도구를 먼저 시도하세요.
        2. search_web 도구는 오직 DB에 정보가 없을 경우에만 사용하세요.
        3. 도구 호출 시 Final Answer를 작성하지 마세요.
        4. Final Answer는 모든 정보를 수집한 후에만 작성하세요.
        5. 당신은 정보를 상상하지 마세요. fetch_from_db 또는 search_web 결과에 기반해서만 응답하세요.
        6. 당신은 오직 "{company_name}" 회사에 대한 정보만 조회할 수 있습니다. 다른 회사에 대한 검색은 허용되지 않습니다.

        현재까지 확보된 회사 정보:
        {current_context}

        평가자의 질문:
        "{question}"

        명확하고 검증된 정보만 제공하세요.
        Final Answer는 반드시 Observation 이후에 단독으로 작성
        """

        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            system_message=system_message
        )

        return agent.run(question)