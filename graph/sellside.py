from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from config import llm_b
from tools import fetch_from_db, search_web
from state import State

sellside_prompt = """
    당신은 친절한 AI agent입니다.
    당신의 역할은 '{company_name}'의 M&A 매도자입니다. 
    당신은 평가자가 요청한 정보만을 사실만을 정확히 제공해야 합니다.
    도구를 쓰세요.
    도구 사용 원칙:
    1. fetch_from_db를 먼저 사용하세요.
    2. fetch_from_db에서 정보가 없으면 search_web을 사용하세요.
    3. fetch_from_db와 search_web에서 모두 정보가 없으면, 해당 항목의 정보가 없다고 대답하세요.
    4. 도구의 입력 회사명을 영어로 바꾸지 마세요.
    수집된 정보를 평가자에게 전달할 대답을 대화 형식으로 생성하세요.
    반드시 대화의 흐름에 따라 요청한 정보만을 전달하세요.
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