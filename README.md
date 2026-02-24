# hwp_agent

> 한국 공문서(HWP)를 AI로 분석하는 RAG 기반 질의응답 시스템

한국어 문서 처리에서 가장 흔한 문제인 HWP 파싱을 Upstage Document Parse API로 해결하고,
LangChain + ChromaDB + GPT-4o를 연결한 질의응답 시스템입니다.

---

## 데모

![데모 스크린샷](https://github.com/user-attachments/assets/31dbd038-f7f2-43ad-bab0-39c8bcd4fdb1)

---

## 주요 기능

- HWP / HWPX 파일 업로드 및 파싱 (Upstage Document Parse API)
- 복잡한 레이아웃(표, 다단) 인식
- 벡터 임베딩 및 유사도 검색 (ChromaDB)
- GPT-4o 기반 자연어 질의응답
- Streamlit 웹 인터페이스

---

## 기술 스택

| 역할 | 기술 |
|------|------|
| 문서 파싱 | Upstage Document Parse API |
| 임베딩 | OpenAI text-embedding-3-small |
| 벡터 DB | ChromaDB |
| LLM | GPT-4o |
| 프레임워크 | LangChain |
| UI | Streamlit |

---

## 프로젝트 구조

```
hwp_agent/
├── app.py          # Streamlit UI
├── ingestion.py    # HWP 파싱 (Upstage API)
├── database.py     # 벡터 저장 및 검색 (ChromaDB)
├── main.py         # 엔트리포인트
├── .env.example    # 환경변수 예시
└── requirements.txt
```

---

## 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/pjg9606/hwp_agent.git
cd hwp_agent
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 만들고 API 키를 입력합니다.

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=your_openai_api_key
UPSTAGE_API_KEY=your_upstage_api_key
```

### 4. 실행

```bash
streamlit run app.py
```

---

## 사용 방법

1. 브라우저에서 `http://localhost:8501` 접속
2. HWP 파일 업로드
3. 질문 입력
4. AI 답변 확인

---

## 주의사항

- Upstage Document Parse API는 페이지 단위 과금입니다
- `.env` 파일은 절대 커밋하지 마세요 (`.gitignore` 포함)

---

## 관련 글

- [[공문서 RAG 구축기 1편] HWP 파싱 해결법](https://velog.io/@pjg9606) <!-- 발행 후 링크 업데이트 -->

---

## 라이선스

MIT
