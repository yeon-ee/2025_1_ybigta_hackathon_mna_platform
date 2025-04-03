from langchain_core.runnables import RunnableConfig
from langchain_teddynote.messages import random_uuid
import json
from .graph import create_workflow

def agentic_flow(company_name: str, user_query: str, checklist: dict) -> dict:
    try:
        # 워크플로우 생성
        app = create_workflow()
        
        # 실행 설정
        config = RunnableConfig(recursion_limit=10, configurable={"thread_id": random_uuid()})
        
        # 초기 상태 설정
        inputs = {
            "messages": [],
            "score": {},
            "comment": {},
            "sender": "",
            "company_name": company_name,
            "user_query": user_query,
            "checklist": checklist,
        }
        
        # 워크플로우 실행
        result = app.invoke(inputs, config)
        result = json.loads(result["messages"][-1].content)
    except Exception as e:
        print("Error: e")
        return {
            "score": {"항목": 0},
            "comment": {"항목": "Error"},
        }
    print("Result:", result)
    return result

if __name__ == "__main__":
    from checklist import checklist
    agentic_flow("업스테이지", "헬스케어 산업에 종사하는, 연매출 100억 이상, 최근 1년 투자금 100억 이상, 작년 성장률 25% 이상, 영업이익률 10% 이상인 기업을 찾고 있습니다.", checklist) 