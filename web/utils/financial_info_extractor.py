import base64
import json
import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# .env 파일 로드
load_dotenv()

class FinancialInfoExtractor:
    def __init__(self):
        # .env 파일에서 API 키 로드
        self.api_key = os.getenv('SOLAR_API_KEY')
        if not self.api_key:
            raise ValueError("SOLAR_API_KEY not found in .env file")
            
        self.client = OpenAI(
            base_url="https://api.upstage.ai/v1/information-extraction",
            api_key=self.api_key
        )
        self.mime_type = "application/pdf"

    # Read file
    def encode_to_base64(self, file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
            return base64_encoded

    # Information Extraction
    def extract_information(self, file_path):
        base64_encoded = self.encode_to_base64(file_path)
        extraction_response = self.client.chat.completions.create(
            model="information-extract",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{self.mime_type};base64,{base64_encoded}"},
                        },
                    ],
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "document_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "단위(unit)": {
                                "type": "number",
                                "description": "단위는 1 단위입니다. "
                            },
                            "Table_2": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "reportingYear": {
                                            "type": "string",
                                            "description": "The reporting Year for the financial statements"
                                        },
                                        "매출액(영업수익)": {
                                            "type": "number",
                                            "description": "Operating revenue refers to the income a company earns from its core business activities, such as sales of goods or services."
                                        },
                                        "영업이익(영업수익 - 영업비용)_": {
                                            "type": "number",
                                            "description": "영업이익은 영업수익과 영업비용의 차로 계산한다. "
                                        },
                                        "순이익(법인세차감후이익 또는 당기순이익": {
                                            "type": "number",
                                            "description": "순이익은 법인세차감후이익 또는 당기순이익을 의미한다. "
                                        },
                                        "자산(자산총계)": {
                                            "type": "number",
                                            "description": "자산은 자본총계이다. "
                                        },
                                        "부채(부채총계)": {
                                            "type": "number",
                                            "description": "부채는 부채총계이다."
                                        },
                                        "자본(자본총계)": {
                                            "type": "number",
                                            "description": "자본은 자본총계이다."
                                        }
                                    },
                                    "required": [
                                        "reportingYear",
                                        "매출액(영업수익)",
                                        "영업이익(영업수익 - 영업비용)_",
                                        "순이익(법인세차감후이익 또는 당기순이익",
                                        "자산(자산총계)",
                                        "부채(부채총계)",
                                        "자본(자본총계)"
                                    ]
                                }
                            }
                        },
                        "required": [
                            "단위(unit)",
                            "Table_2"
                        ]
                    }
                }
            },
        )
        return json.loads(extraction_response.choices[0].message.content)

def format_financial_data(raw_data):
    """재무 데이터를 정확한 형식으로 포맷팅 (예: '73.7억', '-1,632만'), 원 단위는 제거"""
    if not raw_data or 'Table_2' not in raw_data:
        return None
    
    formatted_data = {
        '손익': {
            '매출액': {},
            '영업이익': {},
            '순이익': {}
        },
        '재무': {
            '자산': {},
            '부채': {},
            '자본': {}
        }
    }
    
    def format_amount(value):
        # unit이 곧 곱해야 할 값
        unit = raw_data.get('단위(unit)', 1)
        amount = value * unit
        
        # 1억 이상인 경우
        if abs(amount) >= 100000000:
            amount_eok = amount / 100000000
            return f"{amount_eok:,.1f}억"
        # 1억 미만인 경우
        else:
            amount_man = amount / 10000
            return f"{amount_man:,.1f}만"
    
    # Table_2 데이터를 연도 기준으로 정렬 (최신 연도부터)
    sorted_entries = sorted(raw_data['Table_2'], 
                          key=lambda x: x['reportingYear'],
                          reverse=True)
    
    for entry in sorted_entries:
        year = entry['reportingYear']
        
        # 손익 정보
        formatted_data['손익']['매출액'][year] = format_amount(entry['매출액(영업수익)'])
        formatted_data['손익']['영업이익'][year] = format_amount(entry['영업이익(영업수익 - 영업비용)_'])
        formatted_data['손익']['순이익'][year] = format_amount(entry['순이익(법인세차감후이익 또는 당기순이익'])
        
        # 재무 정보
        formatted_data['재무']['자산'][year] = format_amount(entry['자산(자산총계)'])
        formatted_data['재무']['부채'][year] = format_amount(entry['부채(부채총계)'])
        formatted_data['재무']['자본'][year] = format_amount(entry['자본(자본총계)'])
    
    return formatted_data

def get_user_input(prompt, allow_empty=True):
    """사용자 입력을 받는 헬퍼 함수"""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value if value else ""
        print("이 필드는 필수입니다. 다시 입력해주세요.")

def get_list_input(prompt):
    """리스트 형태의 입력을 받는 헬퍼 함수"""
    print(prompt)
    print("(여러 항목은 쉼표로 구분하여 입력하세요. 입력을 마치려면 엔터를 누르세요)")
    value = input("> ").strip()
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def add_new_company(pdf_path, user_input, company_name=None, company_info=None):
    """새로운 기업을 inno_company.json에 추가하고 기업가치를 계산"""
    
    print(f"\n=== 기업 정보 추출 시작 ===")
    print(f"PDF 파일: {pdf_path}")
    
    # FinancialInfoExtractor 인스턴스 생성
    print("1. API 초기화 중...")
    extractor = FinancialInfoExtractor()
    
    try:
        # PDF에서 재무 정보 추출
        print("2. PDF에서 재무 정보 추출 중... (약 1-2분 소요될 수 있습니다)")
        raw_result = extractor.extract_information(pdf_path)
        print("   ✓ 재무 정보 추출 완료")
        
        print("3. 추출된 데이터 포맷팅 중...")
        formatted_result = format_financial_data(raw_result)
        
        if not formatted_result:
            print(f"❌ 오류: {pdf_path}에서 재무 데이터를 추출할 수 없습니다")
            return False, None
        print("   ✓ 데이터 포맷팅 완료")
        
        # inno_company.json 파일 읽기
        print("4. 기존 기업 데이터 로딩 중...")
        current_dir = os.path.dirname(os.path.abspath(__file__))  # web/utils
        inno_company_path = os.path.join(current_dir, '..', 'db', 'json', 'inno_company.json')
        print(f"   JSON 파일 경로: {inno_company_path}")
        
        if not os.path.exists(inno_company_path):
            print(f"❌ 오류: 파일을 찾을 수 없습니다: {inno_company_path}")
            return False, None
            
        with open(inno_company_path, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        print("   ✓ 기존 데이터 로딩 완료")
        
        print("\n=== 기업 정보 입력 ===")
        if company_info is None:
            company_info = {}
        
        if company_name is None:
            company_name = user_input.get('company_name', '')
        
        # 기본 정보 입력
        url = user_input.get('url', '')
        intro = user_input.get('intro', '')
        listing = user_input.get('listing', '')
        founded_date = user_input.get('founded_date', '')
        website = user_input.get('website', '')
        address = user_input.get('address', '')
        categories = [user_input.get('category', '')] if user_input.get('category') else []
        
        # 투자 정보 입력
        print("\n=== 투자 정보 입력 ===")
        investment_stage = user_input.get('investment_stage', '')
        investment_amount = user_input.get('investment', '')
        investment_count = user_input.get('investment_count', '')
        
        # 투자 이력, 보도자료 URL, 특허 목록은 빈 리스트로 처리
        investment_history = []
        news_urls = []
        patents = []
        
        print("\n5. 새 기업 정보 생성 중...")
        # 새 기업 정보 생성
        new_company = {
            "url": url,
            "기업명": company_name,
            "기업소개": intro,
            "상장여부": listing,
            "설립일": founded_date,
            "홈페이지": website,
            "주소": address,
            "카테고리": categories,
            "주요정보": {
                "자본금": user_input.get('capital', ''),
                "연매출": user_input.get('annual_sales', ''),
                "기술등급": user_input.get('tech_grade', '')
            },
            "투자유치정보": {
                "최종투자단계": investment_stage,
                "누적투자유치금액": investment_amount,
                "투자유치건수": investment_count,
                "투자유치이력": investment_history
            },
            "손익": formatted_result['손익'],
            "재무": formatted_result['재무'],
            "보도자료": news_urls,
            "특허명칭리스트": patents
        }
        print("   ✓ 새 기업 정보 생성 완료")
        
        # 기업 목록에 추가
        companies[company_name] = new_company
        
        print("6. 업데이트된 데이터 저장 중...")
        # 업데이트된 데이터 저장
        with open(inno_company_path, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
        print("   ✓ 데이터 저장 완료")
        
        print("7. 기업가치 계산 및 재무비율 분석 중...")
        try:
            # 프로젝트 루트 디렉토리 경로 계산
            current_dir = os.path.dirname(os.path.abspath(__file__))  # web/utils
            project_root = os.path.dirname(current_dir)  # web
            
            # enterprise_value.py와 enterprise_enrichment.py 경로
            enterprise_value_path = os.path.join(project_root, 'db', 'enterprise_value.py')
            enterprise_enrichment_path = os.path.join(project_root, 'db', 'enterprise_enrichment.py')
            
            if not os.path.exists(enterprise_value_path):
                raise FileNotFoundError(f"enterprise_value.py를 찾을 수 없습니다: {enterprise_value_path}")
            if not os.path.exists(enterprise_enrichment_path):
                raise FileNotFoundError(f"enterprise_enrichment.py를 찾을 수 없습니다: {enterprise_enrichment_path}")
            
            # 현재 작업 디렉토리를 프로젝트 루트로 변경
            original_dir = os.getcwd()
            os.chdir(project_root)  # web 디렉토리로 이동
            
            try:
                # 1. 기업가치 계산
                print("   1) 기업가치 계산 중...")
                result = subprocess.run(
                    ['python', enterprise_value_path], 
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("      ✓ 기업가치 계산 완료")
                if result.stdout:
                    print(f"      출력: {result.stdout}")
                    
                # 2. 재무비율 분석
                print("   2) 재무비율 분석 중...")
                result = subprocess.run(
                    ['python', enterprise_enrichment_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("      ✓ 재무비율 분석 완료")
                if result.stdout:
                    print(f"      출력: {result.stdout}")
                    
            finally:
                os.chdir(original_dir)  # 원래 디렉토리로 복귀
                
        except FileNotFoundError as e:
            print(f"   ⚠️ 파일 찾기 오류: {str(e)}")
            return False, None

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ 처리 중 오류 발생: {str(e)}")
            if e.stdout:
                print(f"   출력: {e.stdout}")
            if e.stderr:
                print(f"   에러: {e.stderr}")
            return False, None
        
        print(f"\n✅ 성공: {company_name} 추가 및 기업가치 계산 완료")
        return True, new_company
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False, None

# 메인 실행 코드
if __name__ == "__main__":
    print("\n=== 기업 정보 추출 프로그램 시작 ===")
    # 현재 파일의 디렉토리 경로를 기준으로 PDF 파일 경로 설정
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'meatbox_finance.pdf')
    print(f"PDF 파일 경로: {pdf_path}")
    
    user_input = {
        'company_name': '인공지능 솔루션을 개발하는 스타트업',
        'category': '모빌리티/교통',
        'capital': 2,
        'investment': 3,
        'investment_count': 4,
        'annual_sales': 5,
        'tech_grade': 'B-',
        'url': '',
        'intro': '',
        'listing': '',
        'founded_date': '',
        'website': '',
        'address': '',
        'investment_stage': ''
    }
    
    success, result = add_new_company(pdf_path, user_input)
    
    if success:
        print("\n프로그램이 성공적으로 완료되었습니다.")
    else:
        print("\n프로그램 실행 중 오류가 발생했습니다.")
