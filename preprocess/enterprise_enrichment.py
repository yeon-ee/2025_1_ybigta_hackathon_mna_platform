# ✅ 재무 비율 및 수익성 등급 추가 (inno_company_with_ev.json 기반)
import json
import os

# ----------------------------
# 파일 로드
# ----------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(base_dir, 'Dataset', 'inno_company_with_ev.json')

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ----------------------------
# 금액 파싱 함수
# ----------------------------
def parse_amount(s):
    s = s.replace(",", "").replace("이상", "").strip()
    if "만원" in s:
        return float(s.replace("만원", "")) / 10000
    elif "억원" in s:
        return float(s.replace("억원", ""))
    elif "만" in s:
        return float(s.replace("만", "")) / 10000
    elif "억" in s:
        return float(s.replace("억", ""))
    else:
        return 0

# ----------------------------
# 수익성 등급 계산 함수
# ----------------------------
def calc_profitability(operating_income, net_income, sales):
    op_margin = (operating_income / sales) if sales > 0 else 0
    net_margin = (net_income / sales) if sales > 0 else 0

    if op_margin >= 0.15 or net_margin >= 0.15:
        return "A"
    elif op_margin >= 0.05 or net_margin >= 0.05:
        return "B"
    elif op_margin >= 0 or net_margin >= 0:
        return "C"
    else:
        return "D"

# ----------------------------
# 기업별 재무비율 및 수익성 등급 삽입
# ----------------------------
for company in data:
    sales = parse_amount(company.get("손익", {}).get("매출액", {}).get("2023", "0"))
    sales_2022 = parse_amount(company.get("손익", {}).get("매출액", {}).get("2022", "0"))
    operating_income = parse_amount(company.get("손익", {}).get("영업이익", {}).get("2023", "0"))
    net_income = parse_amount(company.get("손익", {}).get("순이익", {}).get("2023", "0"))
    assets = parse_amount(company.get("재무", {}).get("자산", {}).get("2023", "0"))
    assets_2022 = parse_amount(company.get("재무", {}).get("자산", {}).get("2022", "0"))
    debt = parse_amount(company.get("재무", {}).get("부채", {}).get("2023", "0"))
    capital = parse_amount(company.get("재무", {}).get("자본", {}).get("2023", "0"))

    # 수익성 등급
    profitability_grade = calc_profitability(operating_income, net_income, sales)

    # 재무비율
    debt_ratio = (debt / capital * 100) if capital > 0 else None
    operating_margin = (operating_income / sales * 100) if sales > 0 else None
    net_margin = (net_income / sales * 100) if sales > 0 else None
    asset_growth = ((assets - assets_2022) / assets_2022 * 100) if assets_2022 > 0 else None

    # 재무비율 삽입 (기업가치 하위로)
    company["재무비율"] = {
        "수익성등급": profitability_grade,
        "부채비율": f"{debt_ratio:.2f}%" if debt_ratio is not None else "N/A",
        "영업이익률": f"{operating_margin:.2f}%" if operating_margin is not None else "N/A",
        "순이익률": f"{net_margin:.2f}%" if net_margin is not None else "N/A",
        "자산증가율": f"{asset_growth:.2f}%" if asset_growth is not None else "N/A"
    }

# ----------------------------
# 저장
# ----------------------------
output_file = os.path.join(base_dir, 'Dataset', 'inno_company_with_ev_financial.json')

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✅ inno_company_with_ev_financial.json 생성 완료 (EV + 재무비율 + 수익성등급 포함)")
