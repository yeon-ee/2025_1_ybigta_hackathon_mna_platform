from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI, api_key
import json
import os
from web.db.utils.json_to_text import json_to_text, test_json_to_text
from web.db.vector_db import save_to_vector_db, save_vectors_test, search_similar_companies

# OpenAI 클라이언트 초기화
upstage_api_key = os.getenv('UPSTAGE_API_KEY')

client = OpenAI(
    api_key=upstage_api_key,
    base_url="https://api.upstage.ai/v1"
)

def get_passage_embedding(text: str) -> list:
    """텍스트의 임베딩을 반환하는 함수"""
    try:
        response = client.embeddings.create(
            input=text,
            model="embedding-passage"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"임베딩 생성 중 에러 발생: {str(e)}")
        return None

def get_query_embedding(text: str) -> list:
    """텍스트의 임베딩을 반환하는 함수"""
    try:
        response = client.embeddings.create(
            input=text,
            model="embedding-query"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"임베딩 생성 중 에러 발생: {str(e)}")
        return None

def process_company_data(file_path: str):
    """회사 데이터를 처리하고 임베딩을 생성하여 JSON으로 저장하는 함수"""
    # JSON 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    embeddings = []
    company_names = []
    processed_count = 0
    total_companies = len(companies)

    for company in companies:
        try:
            # 회사 정보를 텍스트로 변환
            company_text = json_to_text(company)
            # 임베딩 생성
            embedding = get_passage_embedding(company_text)

            if embedding is not None:
                embeddings.append(embedding)
                company_names.append(company['기업명'])
                processed_count += 1
                print(f"[{processed_count}/{total_companies}] '{company['기업명']}' 처리 완료")
        except Exception as e:
            print(f"'{company['기업명']}' 처리 중 오류 발생: {str(e)}")

    # JSON 형식으로 저장
    embeddings_data = {
        company_name: embedding
        for company_name, embedding in zip(company_names, embeddings)
    }

    with open('company_embeddings.json', 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)

    # 벡터 DB에 저장
    save_to_vector_db(company_names, embeddings)

    print(f"\n=== 임베딩 처리 결과 ===")
    print(f"총 회사 수: {total_companies}")
    print(f"성공적으로 처리된 회사 수: {processed_count}")
    print(f"임베딩이 저장된 파일: company_embeddings.json")

def get_matching_company(query: str, top_k: int = 5):
    # 1. 임베딩
    print("query: " + query)
    query_embedding = get_query_embedding(query)
    # print("query embedding: " + query_embedding.__str__())

    # 2. 유사 회사 검색
    results = search_similar_companies(query_embedding, top_k)
    # print(results['metadatas'][0])

    return results['metadatas'][0]

def test_get_matching_company():
    """여러 쿼리로 유사 회사 매칭 테스트"""

    # 다양한 테스트 쿼리들
    test_queries = [
        "투자단계는 무조건 series A 이상이면 좋겠어. 그런데 소재지는 가급적 서울이면 좋겠어. EV 규모는 700억 이하가 되어야만 해."
        # "인공지능 솔루션을 개발하는 스타트업",
        # "반도체 설계 전문 기업",
        # "바이오 의약품 연구개발 회사",
        # "데이터 분석 플랫폼 기업",
        # "클라우드 서비스 제공 기업"
    ]

    try:
        for query in test_queries:
            print(f"\n[테스트 쿼리] {query}")

            # 1. 임베딩
            query_embedding = get_query_embedding(query)

            # 2. 유사 회사 검색
            results = search_similar_companies(query_embedding)

            # 3. 회사 목록 출력
            print("검색된 회사들:")
            companies = results['metadatas'][0]
            # print(companies)
            for i, company in enumerate(companies, 1):
                print(f"{i}. {company.get('company_name', '이름 없음')}")

            print("-" * 50)  # 구분선

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise

if __name__ == "__main__":
    # process_company_data('inno_company_with_ev_financial.json')

    # test_json_to_text('inno_company_with_ev_financial.json')
    # save_vectors_test('company_embeddings.json')
    test_get_matching_company()




