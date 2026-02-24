import streamlit as st
import os
import shutil
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from database import save_to_db, query_db # 우리가 만든 모듈 가져오기

# 1. 페이지 설정
st.set_page_config(page_title="B2G 공문서 분석 AI", page_icon="📑")

st.title("📑 B2G HWP 공문서 분석 에이전트")
st.caption("공공기관 HWP 문서를 업로드하면 AI가 내용을 분석하고 답변해 드립니다.")

# 2. 사이드바: 파일 업로드 기능
# ... (위쪽 코드는 그대로 유지)

# 2. 사이드바: 파일 업로드 기능
with st.sidebar:
    st.header("1. 문서 업로드")
    
    st.info(" **업로드 제약 사항**\n\nUpstage API 정책상 **100페이지 이하**의 문서만 분석 가능합니다.\n(100쪽이 넘으면 분할해서 올려주세요.)", icon="ℹ️")
    
    uploaded_file = st.file_uploader("HWP 파일을 올려주세요", type=["hwp"])
    
    if uploaded_file:
        # 파일을 처리를 위해 임시 저장
        if not os.path.exists("temp_files"):
            os.makedirs("temp_files")
            
        file_path = os.path.join("temp_files", uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 분석 버튼
        if st.button("문서 분석 시작 (DB 저장)"):
            with st.spinner("문서를 분석하고 있습니다... (약 1~2분 소요)"):
                # 에러 처리를 위해 try-except 블록 추가 
                try:
                    save_to_db(file_path)
                    st.success("✅ 분석 완료! 이제 오른쪽 채팅창에서 질문하세요.")
                except Exception as e:
                    st.error(f"❌ 분석 실패: {e}")

# ... (아래쪽 채팅 코드는 그대로 유지)
# 3. 메인: 채팅 인터페이스
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요 (예: 지원 대상 분야가 어디야?)"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 답변이 써질 공간
        
        # (1) 검색: DB에서 관련 내용 찾아오기
        if os.path.exists("chroma_db"):
            retrieved_docs = query_db(prompt)
            context_text = ""
            for i, doc in enumerate(retrieved_docs):
                context_text += f"\n[참고문서 {i+1}]\n{doc.page_content}\n"
        else:
            context_text = "아직 문서가 업로드되지 않았습니다."
            retrieved_docs = []

        # (2) 생성: LLM에게 질문 + 문맥 던지기
        # 여기서 gpt-4o를 사용해 정확도를 높입니다.
        llm = ChatOpenAI(model="gpt-4o", temperature=0) 
        
        system_prompt = f"""
        당신은 공공기관 행정 문서 전문가입니다.
        아래 제공된 [참고문서]를 바탕으로 사용자의 질문에 답변하세요.
        문서의 구조(표, 리스트)를 잘 파악하여 명확하게 답변하세요.
        문서에 없는 내용은 지어내지 말고 "문서에 해당 내용이 없습니다"라고 답하세요.
        
        [참고문서]
        {context_text}
        """
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ])
        
        # 화면 표시 및 저장
        full_response = response.content
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # (선택) 참고한 문서 출처 보여주기
        if retrieved_docs:
            with st.expander("📚 AI가 참고한 문서 내용 보기"):
                st.markdown(context_text)