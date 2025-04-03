
from langchain.prompts import PromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

checklist = {
    "업종": ("매수자가 요구한 매물 기업의 업종 또는 산업군과 동일하거나 유사한 업종인지 평가해주세요. 이후, 유사도 수준에 따라 차등적인 점수를 부여하세요.", 10),

    "EV": ("EV(기업가치평가)가 매수자의 요구한 EV 범위 내에 있어 DEAL 성사가 가능한지 (EV ≥ 최소 / EV ≤ 최대) 판단해주세요. 이후, EV가 범위 내에서 클수록 높은 점수를 부여하세요.", 10),

    "연매출": ("최근 연매출이 매수자가 제시한 최소 연매출 이상인지 (연매출 ≥ 최소) 판단해주세요. 이후, 요구치를 초과한 정도에 따라 차등적으로 높은 점수를 부여하세요.", 5),

    "투자단계": ("투자단계가 매수자가 요구한 최소 투자단계 이상인지 (ex: series A 이상) 확인해주세요. 이후, 높은 단계일수록 더 높은 점수를 부여하세요.", 5),

    "성장률": ("최근 매출 성장률이 매수자가 요구하는 최소 성장률 이상인지 평가해주세요. 이후, 성장률이 높을수록 높은 점수를 부여하세요.", 5),

    "누적투자유치금액": ("누적 투자유치금액이 최소 요구치를 초과한 경우, 초과 정도에 따라 차등적으로 높은 점수를 부여하세요.", 5),

    "투자유치건수": ("투자유치 건수가 최소 요구치 이상이면, 건수가 많을수록 높은 점수를 부여하세요.", 3),

    "수익성등급": ("수익성등급이 요구치 이상이면, 등급이 높을수록 높은 점수를 부여하세요.", 3),

    "자산규모": ("자산규모가 최소 요구치 이상인 경우, 자산규모가 클수록 높은 점수를 부여하세요.", 3),

    "기술등급": ("기술등급이 요구치 이상이면, 등급이 높을수록 높은 점수를 부여하세요.", 3),

    "부채비율": ("부채비율이 요구한 최대 부채비율 이하인 경우, 부채비율이 낮을수록 높은 점수를 부여하세요.", 3),

    "영업이익률": ("영업이익률이 최소 요구치를 초과한 경우, 초과 정도에 따라 차등적인 점수를 부여하세요.", 3),

    "순이익률": ("순이익률이 최소 요구치를 초과한 경우, 초과 정도에 따라 차등적인 점수를 부여하세요.", 3),

    "자산증가율": ("자산증가율이 최소 요구치를 초과한 경우, 초과 정도에 따라 차등적인 점수를 부여하세요.", 3)
}

Reviewer_prompt = """
당신은 M&A 체크리스트 Reviewer입니다.

다음은 매수자의 인수 희망 조건입니다:
{user_query}

각 체크리스트 항목에 대해 아래 두 가지를 판단하세요.

1. 매수자가 해당 항목을 언급했는가? (언급했으면 포함)
2. 언급한 항목이라면, 매수자의 요청 속에서 해당 항목의 중요도가 높다고 판단되는 경우 [1,2,3,4,5] 중 중요도 점수로 출력하세요.

[항목]
{checklist}

Output Format (예시):
{
    "업종": 5,
    "EV": 4,
    "성장률": 2
}

언급되지 않은 항목은 절대 출력하지 마세요.
"""

class ChecklistReviewer:
    def __init__(self, llm_model="solar-pro", api_key=None):
        self.llm = ChatUpstage(api_key=api_key or os.getenv("SOLAR_API_KEY"), model=llm_model)
        self.prompt_template = PromptTemplate(
            input_variables=["checklist", "user_query"],
            template=Reviewer_prompt
        )

    def review_checklist(self, user_query: str) -> dict:
        checklist_str = "\n".join([f"- {key}: {desc}" for key, (desc, _) in checklist.items()])
        prompt = self.prompt_template.format(
            checklist=checklist_str,
            user_query=user_query
        )

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        try:
            result = eval(response.content)
            return result
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    user_query = "업종은 AI, 연매출 100억 이상, 성장률은 20% 이상이어야 합니다."
    reviewer = ChecklistReviewer()
    result = reviewer.review_checklist(user_query)
    print(result)


# Reviewer는 언급 여부 + 중요도 점수 추출까지 담당
# Inspector는  유저쿼리 내 중요도× 항목별만점 으로 실제 점수화