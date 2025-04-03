from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from config import llm_c
from state import State

questioner_prompt = """
    당신은 유능한 AI agent입니다.
    당신의 역할은 체크리스트 기반 M&A 평가를 위한 정보 수집 전문가입니다.
    회사의 이름은 '{company_name}'입니다.

    당신은 아래의 체크리스트 항목을 기반으로, 채점에 필요한 정보를 매도자에게 질문해야 합니다.

    당신의 목표는 **각 체크리스트 항목을 평가하기 위해 반드시 필요한 정보**를 수집하는 것입니다.
    질문은 다음의 지침을 따르세요:

    - 간결하고 명확해야 합니다.
    - 매도자가 이해할 수 있는 비즈니스 언어로 작성하세요.
    - 각 질문은 하나의 정보만 묻도록 하세요.
    - 질문을 통해 이미 알고 있는 정보를 추측하거나 추가하지 마세요.

    다음은 체크리스트 항목입니다:
    {checklist_keys}

    지금은 **정보 수집 단계**입니다.
    절대로 지금 체크리스트를 채점하지 마세요.
    **정보가 충분히 모여서 채점이 가능해지면, "INSPECT"이라는 메시지를 보내주세요.**
"""

def get_questioner_prompt(company_name: str, checklist: dict) -> str:
    return questioner_prompt.format(company_name=company_name, checklist_keys=checklist.keys())

def create_questioner_agent(state: State) -> object:
    return create_react_agent(
        llm_c, 
        tools=[],
        prompt=get_questioner_prompt(state["company_name"], state["checklist"]),
    )

def questioner_node(state: State) -> State:
    agent = create_questioner_agent(state)
    result = agent.invoke(state)

    last_message = AIMessage(
        content=result["messages"][-1].content,
        name="questioner",
    )

    return {
        "messages": [last_message],
        "sender": "questioner"
    } 