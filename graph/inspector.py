from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from .config import llm_a
from .state import State

inspector_prompt = """
    당신은 유능한 AI agent입니다.
    당신의 역할은 체크리스트 기반 M&A 평가 전문가입니다.
    회사의 이름은 '{company_name}'입니다.

    당신은 이전에 매도자로부터 수집된 정보를 바탕으로 체크리스트를 평가해야 합니다.
    **이미 수집된 정보만을 사용**하여, 아래 지침에 따라 평가하세요:

    - 각 항목에 대해 0점부터 항목별 만점 사이의 점수를 부여하세요.
    - 매수자의 요청에 해당 항목의 정보가 없다면, 일반적인 기준에 따라 판단하여 점수를 부여하세요.
    - 점수의 근거를 명확하게 설명하세요.
    - 주관적 판단이나 배경 지식 없이, 오직 수집된 정보에만 근거해야 합니다.
    - 추가 정보를 요청하고 싶은 경우, 'REQUEST'를 포함하여 요청하세요.

    아래 형식으로 결과를 반환하세요:
    {{
        "score": {{ 항목별 부여 점수 }},
        "comment": {{ 각 항목별 채점 이유 }}
    }}

    다음은 체크리스트 항목과 항목별 만점 및 설명입니다:
    {checklist}

    매수자의 요청:
    {user_query}

    지금은 **채점 단계**입니다.
    절대로 새로운 질문을 하지 마세요.
"""

def get_inspector_prompt(company_name: str, user_query: str, checklist: dict) -> str:
    return inspector_prompt.format(company_name=company_name, checklist=checklist, user_query=user_query)

def create_inspector_agent(state: State) -> object:
    return create_react_agent(
        llm_a, 
        tools=[],
        prompt=get_inspector_prompt(state["company_name"], state["user_query"], state["checklist"]),
    )

def inspector_node(state: State) -> State:  # 이 부분은 나중에 동적으로 설정할 수 있도록 변경할 수 있습니다
    agent = create_inspector_agent(state)
    result = agent.invoke(state)
    
    last_message = AIMessage(
        content=result["messages"][-1].content,
        name="checklist_inspector",
    )
    return {
        "messages": [last_message],
        "sender": "checklist_inspector"
    } 