import json
from web.db.company_embed import get_matching_company
# 매수자: 예제 함수를 정의 (문자열을 처리해서 JSON 반환)
def process_input_to_report(input_string):
    # print(input_string)

    companies = get_matching_company(input_string, 30)
    company_names = [company['company_name'] for company in companies]

    print("companies:"+ company_names.__str__())
    print("-" * 50)
    return company_names
    # return json.dumps({"user_input": input_string}, ensure_ascii=False)

