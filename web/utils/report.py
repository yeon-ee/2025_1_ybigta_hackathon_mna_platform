import json

from graph.checklist import checklist
from graph.agentic_flow import agentic_flow
from web.db.company_embed import get_matching_company
# 매수자: 예제 함수를 정의 (문자열을 처리해서 JSON 반환)
def process_input_to_report(input_string):
    # print(input_string)

    companies = get_matching_company(input_string, 5)
    company_names = [company['company_name'] for company in companies]

    print("companies:"+ company_names.__str__())
    print("-" * 50)
    reports = {}
    for company_name in company_names:
        report = agentic_flow(company_name, input_string, checklist)
#         report = {"score":{"업종":30,"EV":30,"연매출":15,"투자단계":15,"성장률":15,"누적투자유치금액":15,"투자유치건수":10,
# "수익성등급":10,"자산규모":10,"기술등급":10,"부채비율":10,"영업이익률":10,"순이익률":10,"자산증가율":10},
# "comment":{"업종":"래블업은 인공지능, 자연어처리/텍스트마이닝 등의 업종에 속해 있어 매수자가 요구한 업종과 일치합니다.","EV":"래블업의 EV는 343.8억원으로, 매수자의 요구 범위 내에 있습니다.",
# "연매출":"래블업의 최근 연매출은 68.0억원으로, 매수자가 제시한 최소 연매출 이상입니다.","투자단계":"래블업은 'series A' 투자단계에 위치해 있어, 매수자가 요구한 최소 투자단계 이상입니다.",
# "성장률":"래블업의 최근 성장률은 170.9%로, 매수자가 요구하는 최소 성장률 이상입니다.","누적투자유치금액":"래블업이 지금까지 누적하여 투자 유치한 금액은 125.0억원으로, 최소 요구치를 초과합니다.",
# "투자유치건수":"래블업이 지금까지 투자를 유치한 건수는 2건으로, 최소 요구치 이상입니다.","수익성등급":"래블업의 수익성 등급은 'A'로, 요구치 이상입니다.",
# "자산규모":"래블업의 현재 자산 규모는 181.1억원으로, 최소 요구치 이상입니다.","기술등급":"래블업의 기술 등급은 2.0으로, 요구치 이상입니다.",
# "부채비율":"래블업의 현재 부채비율은 6.03%로, 요구한 최대 부채비율 이하입니다.","영업이익률":"래블업의 최근 영업이익률은 46.62%로, 최소 요구치를 초과합니다.","순이익률":"래블업의 최근 순이익률은 47.21%로, 최소 요구치를 초과합니다.",
# "자산증가율":"래블업의 최근 자산 증가율은 70.37%로, 최소 요구치를 초과합니다."}}
        # print(report)
        reports[company_name] = report
    return reports
    # return json.dumps({"user_input": input_string}, ensure_ascii=False)

