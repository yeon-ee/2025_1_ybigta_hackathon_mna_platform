import uuid
import chromadb
import json
import os

def connect_to_vector_db():
    """ChromaDB 로컬 클라이언트 설정"""
    try:
        # 프로젝트 루트 경로 찾기
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(project_root, "db", "chroma_data")

        print(f"ChromaDB 경로: {db_path}")
        client = chromadb.PersistentClient(path=db_path)

        print("로컬 DB 연결 성공!")
        print(f"현재 작업 디렉토리: {os.getcwd()}")

        try:
            collection = client.get_collection("company_embeddings")
            print(f"컬렉션 데이터 수: {collection.count()}")
        except:
            collection = client.create_collection(
                name="company_embeddings",
                metadata={"hnsw:space": "cosine"}
            )

        return collection

    except Exception as e:
        print(f"ChromaDB 연결 실패: {str(e)}")
        raise


def save_to_vector_db(company_names: list, embeddings: list) -> None:
    """임베딩 벡터를 ChromaDB에 저장하는 함수"""
    try:
        # ChromaDB 연결 설정
        collection = connect_to_vector_db()

        # ID 생성
        ids = [str(uuid.uuid4()) for _ in company_names]

        # 메타데이터 준비
        metadatas = [{"company_name": name} for name in company_names]

        # ChromaDB에 일괄 저장
        collection.add(
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"ChromaDB에 {len(company_names)}개의 임베딩 저장 완료")

    except Exception as e:
        print(f"벡터 DB 저장 중 오류 발생: {str(e)}")

def save_vectors_test(json_file_path):
    """
    JSON 파일에서 임베딩을 읽어와서 다시 저장하는 함수
    """
    try:
        # JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as f:
            embeddings_data = json.load(f)

        # 회사명과 임베딩 분리
        company_names = list(embeddings_data.keys())
        embeddings = list(embeddings_data.values())

        # 벡터 DB에 저장
        save_to_vector_db(company_names, embeddings)

        print(f"\n=== 벡터 저장 완료 ===")
        print(f"처리된 회사 수: {len(company_names)}")

    except Exception as e:
        print(f"벡터 저장 중 오류 발생: {str(e)}")


def search_similar_companies(query_embedding, top_k=5):
    """유사한 회사 검색"""
    collection = connect_to_vector_db()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results
