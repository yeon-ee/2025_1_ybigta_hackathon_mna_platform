from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from .config import llm_b
from .tools import fetch_from_db, search_web
from .state import State

sellside_prompt = """
    당신은 친절한 AI 에이전트입니다.
    당신의 역할은 '{company_name}'의 M&A 매도자입니다. 
    당신은 평가자가 요청한 정보에 대해 정확하고 간결하게 답해야 하며, 정보를 제공하기 위해 필요한 경우 도구를 사용할 수 있습니다.

    당신은 아래의 도구를 사용할 수 있습니다:
    - fetch_from_db: 내부 데이터베이스에서 정보를 가져옵니다.
    - search_web: 웹에서 정보를 검색합니다.

    도구 사용 가이드라인:
    1. 먼저 fetch_from_db를 시도합니다.
    2. 적절한 정보가 없을 경우에만 search_web을 사용합니다.
    3. 둘 다 실패할 경우, 정보를 찾을 수 없다고 알려주세요.
    4. 도구의 입력 회사명을 영어로 번역하지 마세요.

    가능한 경우, 이전 대화에서 얻은 정보를 재사용하거나 추가적인 도구 호출 없이 답변하세요.
    마지막에는 사용자가 이해할 수 있도록 자연스러운 대화 형식으로 응답을 구성하세요.
    예시:
    Question: 회사의 주요 고객이 누구입니까?
    Thought: 고객 정보를 찾기 위해 데이터베이스를 확인해야 합니다.
    Action: fetch_from_db
    Action Input: "삼성전자"
    Observation: 주요 고객은 애플, 구글입니다.
    Thought: 정보를 찾았습니다. 이제 사용자에게 답할 수 있습니다.
    Final Answer: 삼성전자의 주요 고객은 애플과 구글입니다.
"""

def get_sellside_prompt(company_name: str) -> str:
    return sellside_prompt.format(company_name=company_name)

def create_sellside_agent(state: State):
    return create_react_agent(
        llm_b, 
        tools=[fetch_from_db, search_web],
        prompt=get_sellside_prompt(state["company_name"]),
    )

def sellside_node(state: State) -> State: # 이 부분은 나중에 동적으로 설정할 수 있도록 변경할 수 있습니다
    agent = create_sellside_agent(state)
    result = agent.invoke(state)

    last_message = AIMessage(
        content=result["messages"][-1].content,
        name="sellside",
    )
    return {
        "messages": [last_message],
        "sender": "sellside"
    } 