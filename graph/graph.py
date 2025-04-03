import json
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import State
from sellside import sellside_node
from questioner import questioner_node
from inspector import inspector_node

def qustioner_router(state: State) -> str:
    if state["sender"] == "questioner" and "INSPECT" in state["messages"][-1].content:
        return "checklist_inspector"
    else:
        return "sellside"

def inspector_router(state: State) -> str:
    if state["sender"] == "checklist_inspector" and "REQUEST" in state["messages"][-1].content:
        return "questioner"
    elif state["sender"] == "checklist_inspector" and "score" in state["messages"][-1].content:
        data = json.loads(state["messages"][-1].content)
        state["score"] = data["score"]
        state["final_comment"] = data["comment"]
        return END
    else:
        return "checklist_inspector"

def create_workflow():
    workflow = StateGraph(State)
    workflow.add_node("checklist_inspector", inspector_node)
    workflow.add_node("questioner", questioner_node)
    workflow.add_node("sellside", sellside_node)

    workflow.add_edge(START, "questioner")

    workflow.add_conditional_edges(
        source="questioner",
        path=qustioner_router,
        path_map={
            "sellside": "sellside",
            "checklist_inspector": "checklist_inspector"
        },
    )
    workflow.add_edge("sellside", "questioner")

    workflow.add_conditional_edges(
        source="checklist_inspector",
        path=inspector_router,
        path_map={
            "questioner": "questioner",
            "checklist_inspector": "checklist_inspector",
            END: END
        },
    )
    
    return workflow.compile(checkpointer=MemorySaver()) 