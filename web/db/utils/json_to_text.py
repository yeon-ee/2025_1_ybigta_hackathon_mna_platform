import json

def json_to_text(data: dict) -> str:
    sentences = []

    # 기본 회사 소개 문장
    intro_parts = []
    if data.get('기업명'):
        intro_parts.append(data['기업명'])
    if data.get('설립일'):
        intro_parts.append(f"{data['설립일']}에 설립되었으며")
    if data.get('상장여부'):
        intro_parts.append(f"{data['상장여부']} 기업입니다")
    if intro_parts:
        sentences.append(' '.join(intro_parts))

    if data.get('기업소개'):
        sentences.append(f"이 기업은 {data['기업소개']}을 하고 있습니다")

    # 위치 및 연락처 정보
    location_parts = []
    if data.get('주소'):
        location_parts.append(f"회사는 {data['주소']}에 위치해 있으며")
    if data.get('홈페이지'):
        location_parts.append(f"홈페이지 주소는 {data['홈페이지']}입니다")
    if location_parts:
        sentences.append(' '.join(location_parts))

    # 산업 분야
    if data.get('카테고리') and isinstance(data['카테고리'], list) and len(data['카테고리']) > 0:
        sentences.append(f"주요 사업 영역은 {', '.join(data['카테고리'])} 분야를 포함합니다")

    # 주요 정보를 하나의 문장으로
    if data.get('주요정보'):
        info = data['주요정보']
        info_parts = []
        if info.get('자본금'):
            info_parts.append(f"자본금 {info['자본금']}")
        if info.get('고용인원'):
            info_parts.append(f"총 {info['고용인원']}명의 직원")
        if info.get('연매출'):
            info_parts.append(f"연간 {info['연매출']}의 매출")
        if info_parts:
            sentences.append(f"현재 {', '.join(info_parts)}을 보유하고 있습니다")

    # 투자 관련 정보를 하나의 문장으로
    if data.get('투자이력'):
        inv = data['투자이력']
        inv_parts = []
        if inv.get('최종투자단계'):
            inv_parts.append(f"현재 {inv['최종투자단계']} 단계에 있으며")
        if inv.get('누적투자유치금액'):
            inv_parts.append(f"총 {inv['누적투자유치금액']}의 투자를 유치했고")
        if inv.get('투자유치건수'):
            inv_parts.append(f"{inv['투자유치건수']}건의 투자 유치 실적이 있습니다")
        if inv_parts:
            sentences.append(' '.join(inv_parts))

        if inv.get('투자유치목록') and isinstance(inv['투자유치목록'], list) and len(inv['투자유치목록']) > 0:
            investment_details = []
            for investment in inv['투자유치목록'][:3]:
                detail_parts = []
                if investment.get('날짜'):
                    detail_parts.append(investment['날짜'])
                if investment.get('금액'):
                    detail_parts.append(investment['금액'])
                if detail_parts:
                    investment_details.append(' '.join(detail_parts))
            if investment_details:
                sentences.append(f"주요 투자 유치 실적으로는 {', '.join(investment_details)} 등이 있습니다")

    # 재무 실적 정보를 문장으로
    if data.get('손익'):
        for year in sorted(data['손익'].get('매출액', {}).keys()):
            year_parts = []
            if data['손익'].get('매출액', {}).get(year):
                year_parts.append(f"매출 {data['손익']['매출액'][year]}")
            if data['손익'].get('영업이익', {}).get(year):
                year_parts.append(f"영업이익 {data['손익']['영업이익'][year]}")
            if data['손익'].get('순이익', {}).get(year):
                year_parts.append(f"순이익 {data['손익']['순이익'][year]}")
            if year_parts:
                sentences.append(f"{year}년에는 {', '.join(year_parts)}를 기록했습니다")

    # 재무상태를 문장으로
    if data.get('재무'):
        for year in sorted(data['재무'].get('자산', {}).keys()):
            finance_parts = []
            if data['재무'].get('자산', {}).get(year):
                finance_parts.append(f"자산 {data['재무']['자산'][year]}")
            if data['재무'].get('부채', {}).get(year):
                finance_parts.append(f"부채 {data['재무']['부채'][year]}")
            if data['재무'].get('자본', {}).get(year):
                finance_parts.append(f"자본 {data['재무']['자본'][year]}")
            if finance_parts:
                sentences.append(f"{year}년 재무상태는 {', '.join(finance_parts)}를 기록했습니다")

    # 재무비율 정보를 하나의 문장으로
    if data.get('재무비율'):
        ratio = data['재무비율']
        ratio_parts = []
        if ratio.get('수익성등급'):
            ratio_parts.append(f"수익성등급 {ratio['수익성등급']}")
        if ratio.get('부채비율'):
            ratio_parts.append(f"부채비율 {ratio['부채비율']}")
        if ratio.get('영업이익률'):
            ratio_parts.append(f"영업이익률 {ratio['영업이익률']}")
        if ratio.get('순이익률'):
            ratio_parts.append(f"순이익률 {ratio['순이익률']}")
        if ratio.get('자산증가율'):
            ratio_parts.append(f"자산증가율 {ratio['자산증가율']}")
        if ratio_parts:
            sentences.append(f"주요 재무비율은 {', '.join(ratio_parts)}입니다")

    # 기업가치 정보
    if data.get('기업가치', {}).get('EV추정'):
        sentences.append(f"현재 추정 기업가치(EV)는 {data['기업가치']['EV추정']}입니다")

    # 보도자료를 문장으로
    if data.get('보도자료') and isinstance(data['보도자료'], list) and len(data['보도자료']) > 0:
        news_items = []
        for news in data['보도자료'][:3]:
            if news.get('날짜') and news.get('제목'):
                news_items.append(f"{news['날짜']}의 {news['제목']}")
        if news_items:
            sentences.append(f"최근 주요 보도로는 {', '.join(news_items)} 등이 있습니다")

    # 특허 정보를 문장으로
    if data.get('특허명칭리스트') and isinstance(data['특허명칭리스트'], str) and data['특허명칭리스트'].strip():
        sentences.append(f"보유하고 있는 특허로는 {data['특허명칭리스트']}가 있습니다")

    return ' '.join(sentences)

def test_json_to_text(file_path: str):
    """
    모든 회사 데이터에 대해 json_to_text 변환이 정상적으로 작동하는지 테스트하는 함수
    """
    try:
        # JSON 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            companies = json.load(f)

        print(f"총 {len(companies)}개 회사 데이터 테스트 시작\n")

        for idx, company in enumerate(companies, 1):
            try:
                # 회사 정보를 텍스트로 변환
                company_name = company.get('기업명', 'Unknown')
                text_result = json_to_text(company)

                # 변환 결과 출력
                print(f"[{idx}/{len(companies)}] '{company_name}' 변환 성공")
                print("변환된 텍스트 미리보기 (처음 200자):")
                print(f"{text_result[:200]}...\n")

            except Exception as e:
                print(f"[{idx}/{len(companies)}] '{company_name}' 변환 실패")
                print(f"오류 내용: {str(e)}")
                print("문제가 된 데이터:")
                print(json.dumps(company, ensure_ascii=False, indent=2))
                print("\n")

        print("=== 테스트 완료 ===")

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
    except json.JSONDecodeError:
        print(f"JSON 파일 형식이 올바르지 않습니다: {file_path}")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {str(e)}")
