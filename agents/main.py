from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from checklist_insepctor import ChecklistInspector
from sell_side_agent import SellSideAgent

MAX_TURN = 4

# 상태 타입 정의
class EvaluationState(TypedDict):
    checklist: dict
    sellside_context: str
    user_query: str
    company_name: str
    question: Optional[str]
    final_score: Optional[dict]
    turn: int

# 인스펙터 노드 함수
def evaluate_checklist(state: EvaluationState) -> EvaluationState:
    inspector = ChecklistInspector()
    result = inspector.evaluate(
        company_name=state["company_name"],
        checklist=state["checklist"],
        sellside_context=state["sellside_context"],
        user_query=state["user_query"]
    )
    state["question"] = result.get("question")
    state["final_score"] = result.get("final_score")
    state["turn"] += 1  # turn 증가
    return state

# 셀사이드 노드 함수
def fetch_information(state: EvaluationState) -> EvaluationState:
    agent = SellSideAgent()
    new_info = agent.fetch(
        company_name=state["company_name"],
        question=state["question"],
        current_context=state["sellside_context"]
    )
    state["sellside_context"] += f"\n{new_info}"
    state["question"] = None
    return state

# 분기 조건 함수
def route(state: EvaluationState) -> str:
    if state["final_score"]:
        return END
    elif state["turn"] >= MAX_TURN:
        print(f"[INFO] 최대 턴 {MAX_TURN}회 도달. 강제 종료합니다.")
        return END
    elif state["question"]:
        return "fetch_info"
    else:
        return "evaluate"

# 그래프 구성
def build_graph():
    builder = StateGraph(EvaluationState)
    builder.add_node("evaluate", evaluate_checklist)
    builder.add_node("fetch_info", fetch_information)
    builder.set_entry_point("evaluate")
    builder.add_conditional_edges("evaluate", route)
    builder.add_edge("fetch_info", "evaluate")
    return builder.compile()

if __name__ == "__main__":
    # 초기 상태 입력
    initial_state = EvaluationState(
        checklist={
            "업종": 20,
            "연매출": 15,
            "투자유치": 25,
            "부채비율": 30,
            "영업이익률": 10
        },
        sellside_context="",
        user_query="헬스케어 산업에 종사하는, 연매출 100억 이상, 최근 1년 투자금 100억 이상, 작년 성장률 25% 이상, 영업이익률 10% 이상인 기업을 찾고 있습니다.",
        company_name="핀업",
        question=None,
        final_score=None,
        turn=0
    )

    graph = build_graph()
    result = graph.invoke(initial_state)
    print("최종 점수:", result["final_score"])