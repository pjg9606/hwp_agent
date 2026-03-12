import os
from dotenv import load_dotenv
from langchain_upstage import UpstageDocumentParseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata

# 1. 환경 변수 로드
load_dotenv()

# DB가 저장될 폴더명 (로컬 폴더에 저장됨)
CHROMA_PATH = "chroma_db"

def save_to_db(file_path):
    """
    1. HWP 파일을 읽고 (Load)
    2. 적절한 크기로 자르고 (Split)
    3. 벡터 DB에 저장합니다 (Embed & Store)
    """
    if not os.path.exists(file_path):
        print(f"❌ 파일이 없습니다: {file_path}")
        return None

    # --- 1. Load (문서 읽기) ---
    print(f"📄 [Load] 문서 분석 중... ({file_path})")
    # 옵션을 다 지우고 파일 경로와 split 설정만 남깁니다.
    loader = UpstageDocumentParseLoader(
        file_path,
        split="page"
    )
    docs = loader.load()

    # --- 2. Split (문서 쪼개기) ---
    print("✂️  [Split] 문서 분할 중...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(docs)
    
    # DB가 싫어하는 복잡한 메타데이터(좌표값 등)를 걸러냅니다.
    chunks = filter_complex_metadata(chunks)

    print(f"   👉 총 {len(docs)}페이지를 {len(chunks)}개의 조각(Chunk)으로 분할했습니다.")

    # --- 3. Embed & Store (저장하기) ---
    print("💾 [Save] 데이터베이스(Chroma)에 저장 중... (OpenAI 과금 발생)")
    
    # ▼▼▼ [수정된 부분] 폴더 삭제 대신 데이터 초기화 방식을 사용합니다 ▼▼▼
    
    # 1. DB 연결 (없으면 생성됨)
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
    )
    
    # 2. 기존 데이터가 있다면 삭제 (Reset)
    # Windows 파일 잠금(WinError 32)을 피하기 위해 폴더를 지우지 않고 내용만 비웁니다.
    existing_ids = db.get()['ids']
    if existing_ids:
        print(f"🧹 기존 데이터 {len(existing_ids)}개를 삭제하고 새로 저장합니다...")
        db.delete(ids=existing_ids)
        
    # 3. 새로운 데이터 추가
    db.add_documents(chunks)

    
    print(f"✅ 저장 완료! DB 경로: ./{CHROMA_PATH}")
    return db

def query_db(query_text):
    """
    저장된 DB에서 질문과 가장 관련된 내용을 찾아옵니다.
    """
    # 저장된 DB 불러오기
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
    )
    
    # 유사도 검색 (Similarity Search)
    results = db.similarity_search(query_text, k=3) # 상위 3개 결과
    return results

if __name__ == "__main__":
    # --- 테스트 실행 ---
    TEST_FILE = "sample.hwp"
    
    if os.path.exists(TEST_FILE):
        # 1. DB 생성
        save_to_db(TEST_FILE)
        
        # 2. 검색 테스트
        test_query = "지원 대상 분야가 어디야?" 
        
        print(f"\n🔍 [Query] 질문: '{test_query}'")
        results = query_db(test_query)
        
        print("\n--- [검색 결과] ---")  #Sanity Check(건전성 검사)
        if results:
            for i, res in enumerate(results):
                print(f"[{i+1}] ...{res.page_content[:200]}...")
                print("--------------------------------------------------")
        else:
            print("검색 결과가 없습니다.")
    else:
        print(f"⚠️ '{TEST_FILE}' 파일이 없습니다.")