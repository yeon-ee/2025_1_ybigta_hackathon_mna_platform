import json
import os

# ----------------------------
# EV 배수 테이블 정의
# ----------------------------
sector_multiples = {
    "모빌리티/교통": 1.25,
    "금융/보험/핀테크": 3.0,
    "AI/딥테크/블록체인":3.0,
    "커머스": 1.5,
    "교육": 1.5,
    "부동산/건설": 1.5,
    "헬스케어": 2.0,
    "F&B": 1.25,
    "콘텐츠": 1.25,
}

# Stage별 투자배수
stage_multiples = {
    "seed": 2.0,
    "pre-a": 2.25,
    "series a": 2.75,
    "pre-b": 3.0,
    "series b": 3.25,
    "series c": 3.5
}

# ----------------------------
# 파일 로드
# ----------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
open_file = os.path.join(base_dir,'db', 'json', 'inno_company.json')

with open(open_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ----------------------------
# 금액 파싱 함수
# ----------------------------
def parse_sales(s):   # 손익 / 매출 관련
    s = s.replace(",", "").strip()
    if "만" in s:
        return float(s.replace("만", "")) / 10000
    elif "억" in s:
        return float(s.replace("억", ""))
    else:
        return 0

def parse_investment(s):  # 투자유치금액 관련
    s = s.replace(",", "").replace("이상", "").strip()
    if "만원" in s:
        return float(s.replace("만원", "")) / 10000
    elif "억원" in s:
        return float(s.replace("억원", ""))
    else:
        return 0


# ----------------------------
# EV 계산 함수
# ----------------------------
def estimate_ev(company):
    sectors = company.get("카테고리", [])

    # [1] 매출 기반 EV (2023 손익 매출액 사용)
    sales = parse_sales(company.get("손익", {}).get("매출액", {}).get("2023", "0"))
    applicable_multiples = [sector_multiples[s] for s in sectors if s in sector_multiples]
    base_multiple = sum(applicable_multiples) / len(applicable_multiples) if applicable_multiples else 0
    sales_ev = sales * base_multiple if sales > 0 and base_multiple > 0 else 0

    # [2] 투자유치 기반 EV
    stage = company.get("투자유치정보", {}).get("최종투자단계", "")
    investment_str = company.get("주요정보", {}).get("누적투자유치금액", "")

    # 비공개 or 없음 처리
    if stage in ["비공개", "", None] or investment_str in ["비공개", "", None]:
        investment_ev = 0
        investment_multiple = 0
        investment = 0
        method = "매출기반"  # 강제로 매출기반 사용
    else:
        investment = parse_investment(investment_str)
        investment_multiple = stage_multiples.get(stage.lower(), 0)
        investment_ev = investment * investment_multiple if investment > 0 and investment_multiple > 0 else 0
        method = "투자유치기반" if investment_ev > sales_ev else "매출기반"

    # [3] 최종 EV
    final_ev = max(sales_ev, investment_ev)

    # [4] 성장률
    sales_2022 = parse_sales(company.get("손익", {}).get("매출액", {}).get("2022", "0"))
    try:
        growth_rate = (sales - sales_2022) / sales_2022 if sales_2022 > 0 else 0
    except:
        growth_rate = 0

    return final_ev, base_multiple, investment_multiple, sales_ev, investment_ev, growth_rate, sales, investment, method

# ----------------------------
# EV 삽입
# ----------------------------
for company in data:
    final_ev, base_multiple, investment_multiple, sales_ev, investment_ev, growth_rate, sales, investment, method = estimate_ev(company)
    if final_ev > 0:
        company["기업가치"] = {
            "EV추정": f"{final_ev:.1f}억원",
            "산출근거": {
                "기준년도": "2023",
                "Sales기반EV": f"{sales_ev:.1f}억원 (배수 {base_multiple:.2f})",
                "투자유치기반EV": f"{investment_ev:.1f}억원 (투자 {investment:.1f}억 × 배수 {investment_multiple:.1f})" if investment_ev > 0 else "비공개 or 없음",
                "적용EV": method,
                "연매출": f"{sales:.2f}억",
                "성장률(2022→2023)": f"{growth_rate*100:.1f}%"
            }
        }
    else:
        company["기업가치"] = {
            "EV추정": "N/A",
            "산출근거": {}
        }

# ----------------------------
# 저장
# ----------------------------
output_file = os.path.join(base_dir,'db' ,'json', 'inno_company_with_ev.json')

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("[OK] 기업가치 추가 완료 → inno_company_with_ev.json 생성")


