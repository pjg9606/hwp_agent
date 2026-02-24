import os
from dotenv import load_dotenv
from langchain_upstage import UpstageLayoutAnalysisLoader

# 1. 환경 변수 로드
load_dotenv()

def load_hwp_document(file_path: str):
    # 파일이 있는지 확인
    if not os.path.exists(file_path):
        print(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return []

    print(f"🚀 문서 분석 시작: {file_path}")
    
    # Upstage 파서 설정 (HTML 모드)
    loader = UpstageLayoutAnalysisLoader(
        file_path, 
        output_type="html",
        use_ocr=True,
        split="page"
    )

    try:
        docs = loader.load()
        print(f"✅ 분석 완료! 총 {len(docs)} 페이지를 읽었습니다.")
        return docs
    except Exception as e:
        print(f"❌ 파싱 중 에러 발생: {e}")
        return []

if __name__ == "__main__":
    # 테스트 파일명
    TEST_FILE = "sample.hwp" 
    
    # 파일이 없으면 경고
    if not os.path.exists(TEST_FILE):
        print(f"⚠️ '{TEST_FILE}' 파일이 없습니다. 테스트용 HWP 파일을 폴더에 넣어주세요.")
    else:
        documents = load_hwp_document(TEST_FILE)
        
        if documents:
            # ✅ [요청하신 검증] 총 글자 수 카운트
            total_chars = sum(len(doc.page_content) for doc in documents)
            
            print(f"\n📊 [정밀 검증 결과]")
            print(f"1. 인식된 페이지 수: {len(documents)} 페이지")
            print(f"2. 추출된 총 글자 수: {total_chars:,} 자") # 쉼표 찍어서 보기 좋게 출력
            
            # 글자 수가 너무 적으면 경고
            if total_chars < 500:
                print("⚠️ 경고: 글자 수가 500자 이하입니다. parsing 확인 필요.")
            else:
                print("✅ 성공: 데이터가 충분히 추출되었습니다. (HTML 태그 포함)")


        if documents:
            # 결과 저장
            with open("parsed_result.html", "w", encoding="utf-8") as f:
                for doc in documents:
                    f.write(doc.page_content)
            print("📂 결과가 'parsed_result.html' 파일로 저장되었습니다.")