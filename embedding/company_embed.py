from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI, api_key
import json
import os
from embedding.utils.json_to_text import json_to_text, test_json_to_text
from embedding.utils.vector_db import save_to_vector_db, save_vectors_test

# OpenAI 클라이언트 초기화
upstage_api_key = os.getenv('UPSTAGE_API_KEY')

client = OpenAI(
    api_key=upstage_api_key,
    base_url="https://api.upstage.ai/v1"
)

def get_embedding(text: str) -> list:
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
            embedding = get_embedding(company_text)

            if embedding is not None:
                embeddings.append(embedding)
                company_names.append(company['기업명'])
                processed_count += 1
                print(f"[{processed_count}/{total_companies}] '{company['기업명']}' 처리 완료")
        except Exception as e:
            print(f"'{company['기업명']}' 처리 중 오류 발생: {str(e)}")

    # JSON 형식으로 저장
    embeddings_data = {
        company_name: embedding  # embedding이 이미 리스트이므로 tolist() 제거
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

if __name__ == "__main__":
    # process_company_data('inno_company_test.json')
    # test_json_to_text('inno_company_with_ev_financial.json')
    save_vectors_test('company_embeddings.json')
