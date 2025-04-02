import json
# 매수자: 예제 함수를 정의 (문자열을 처리해서 JSON 반환)
def process_input_to_report(input_string):
    return json.dumps({"user_input": input_string}, ensure_ascii=False)